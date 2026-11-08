"""Método de Simpson: valores de referencia verificados con un script
independiente (fracciones exactas y los ejemplos precargados)."""

import json
import math
from fractions import Fraction
from pathlib import Path

from django.test import SimpleTestCase
from rest_framework.test import APITestCase

from numeric_methods.examples_data import SIMPSON_EXAMPLES
from numeric_methods.serializers.integration import SimpsonSerializer
from numeric_methods.solvers.integration.rules import SIMPSON_13, SIMPSON_38, TRAPEZOID, apply
from numeric_methods.solvers.integration.simpson import solve_simpson

# Respuestas del solver guardadas para la página de teoría (frontend).
THEORY_EXAMPLE = (Path(__file__).resolve().parents[3] / "frontend" / "src" / "methods"
                  / "integration" / "theory" / "simpsonExample.json")

CHAPRA = "0.2 + 25x - 200x^2 + 675x^3 - 900x^4 + 400x^5"


def chapra(x):
    return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5


def chapra_exact(x):
    return Fraction(1, 5) + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5


def exact_rule(rule, f, a, b, n):
    h = (b - a) / n
    return rule.factor * h * sum(w * f(a + i * h) for i, w in enumerate(rule.weights(n)))


def solve(**data):
    serializer = SimpsonSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return solve_simpson(serializer.validated_data).to_dict()


_CACHE = {}


def example(number):
    if number not in _CACHE:
        _CACHE[number] = solve(**SIMPSON_EXAMPLES[number - 1])
    return _CACHE[number]


def block(result, key):
    return next(b for b in result["rules"] if b["rule"]["key"] == key)


def rows(result, key):
    return block(result, key)["rows"]


class ExactFractionTests(SimpleTestCase):
    def test_quartic(self):
        result = solve(function="x^4", a=0, b=2)
        for key, values in (("simpson13", ((Fraction(20, 3), Fraction(-4, 15)), (Fraction(77, 12), Fraction(-1, 60)))),
                            ("simpson38", ((Fraction(176, 27), Fraction(-16, 135)), (Fraction(173, 27), Fraction(-1, 135))))):
            for row, (S, E) in zip(rows(result, key), values):
                with self.subTest(rule=key, n=row["n"]):
                    self.assertAlmostEqual(row["S"], float(S), places=12)
                    self.assertAlmostEqual(row["true_error"], float(E), places=12)
        # Las mismas fracciones con la fórmula de pesos en aritmética exacta.
        quartic = lambda x: x ** 4  # noqa: E731
        self.assertEqual(exact_rule(SIMPSON_13, quartic, Fraction(0), Fraction(2), 2), Fraction(20, 3))
        self.assertEqual(exact_rule(SIMPSON_38, quartic, Fraction(0), Fraction(2), 6), Fraction(173, 27))

    def test_chapra(self):
        a, b = Fraction(0), Fraction(4, 5)
        self.assertEqual(exact_rule(SIMPSON_13, chapra_exact, a, b, 2), Fraction(2564, 1875))
        self.assertEqual(exact_rule(SIMPSON_13, chapra_exact, a, b, 4), Fraction(3044, 1875))
        self.assertEqual(exact_rule(SIMPSON_38, chapra_exact, a, b, 3), Fraction(25636, 16875))
        result = example(1)
        for row, S in zip(rows(result, "simpson13"), (Fraction(2564, 1875), Fraction(3044, 1875))):
            self.assertAlmostEqual(row["S"], float(S), places=12)
        self.assertAlmostEqual(rows(result, "simpson38")[0]["S"], float(Fraction(25636, 16875)), places=12)

    def test_cubic_is_exact(self):
        for key in ("simpson13", "simpson38"):
            for row in rows(example(4), key):
                with self.subTest(rule=key, n=row["n"]):
                    self.assertAlmostEqual(row["S"], 4, places=12)
                    self.assertEqual(row["bound"], 0)
                    self.assertAlmostEqual(row["true_error"], 0, places=12)
        cubic = lambda x: x ** 3  # noqa: E731
        for rule, n in ((SIMPSON_13, 2), (SIMPSON_38, 3)):
            self.assertEqual(exact_rule(rule, cubic, Fraction(0), Fraction(2), n), 4)


class ChapraExampleTests(SimpleTestCase):
    def setUp(self):
        self.result = example(1)

    def test_first_rows(self):
        expected = {
            "simpson13": [(1.367467, 0.273067, 16.645), (1.623467, None, None), (1.639467, None, None)],
            "simpson38": [(1.51917, 0.121363, 7.3978), (1.632948, None, None), (1.640059, None, None)],
        }
        for key, values in expected.items():
            for row, (S, E, rel) in zip(rows(self.result, key), values):
                with self.subTest(rule=key, n=row["n"]):
                    self.assertAlmostEqual(row["S"], S, places=6)
                    # f⁽⁵⁾ es constante: Eₐ = Eₜ en todas las filas.
                    self.assertAlmostEqual(row["approx_error"], row["true_error"], places=9)
                    if E is not None:
                        self.assertAlmostEqual(row["true_error"], E, places=6)
                        self.assertAlmostEqual(row["relative_error"], rel, places=3)
        self.assertAlmostEqual(rows(self.result, "simpson13")[0]["bound"], 2.4576, places=9)
        self.assertAlmostEqual(rows(self.result, "simpson38")[0]["bound"], 1.092267, places=6)
        self.assertAlmostEqual(self.result["mean_fourth"]["value"], -2400, places=9)
        self.assertEqual(self.result["M4"]["value"], 21600)
        self.assertEqual(self.result["M4"]["x"], 0)

    def test_approx_error_equals_true_in_every_row(self):
        for key in ("simpson13", "simpson38"):
            for row in rows(self.result, key):
                self.assertAlmostEqual(row["approx_error"], row["true_error"], places=9)

    def test_stops_at_row_7(self):
        self.assertTrue(self.result["converged"])
        self.assertEqual(self.result["iterations_used"], 7)
        self.assertEqual([rows(self.result, k)[-1]["n"] for k in ("simpson13", "simpson38")], [128, 192])

    def test_comparison_with_trapezoid(self):
        first = rows(self.result, "simpson13")[0]["trapezoid"]
        self.assertAlmostEqual(first["T"], 1.0688, places=12)
        self.assertAlmostEqual(first["true_error"], 0.571733, places=6)
        self.assertEqual(round(first["times"], 1), 2.1)
        sixteen = next(r for r in rows(self.result, "simpson13") if r["n"] == 16)["trapezoid"]
        self.assertEqual(round(sixteen["times"], 1), 149.8)

    def test_identity_with_trapezoid(self):
        identity = rows(self.result, "simpson13")[0]["identity"]
        self.assertEqual((identity["T_n_display"], identity["T_half_display"]), ("1.0688", "0.1728"))
        self.assertEqual(identity["value_display"], "1.367467")
        self.assertTrue(identity["ok"])
        self.assertTrue(all(r["identity"]["ok"] for r in rows(self.result, "simpson13")))
        self.assertTrue(all(r["identity"] is None for r in rows(self.result, "simpson38")))

    def test_ratio_tends_to_one_sixteenth(self):
        for key in ("simpson13", "simpson38"):
            for row in rows(self.result, key)[1:5]:
                with self.subTest(rule=key, n=row["n"]):
                    self.assertTrue(0.06 <= row["ratio"] <= 0.065, row["ratio"])

    def test_no_concavity_note(self):
        self.assertFalse(any("f⁽⁴⁾" in note for note in self.result["notes"]))

    def test_first_row_step(self):
        step = rows(self.result, "simpson13")[0]["step"]
        self.assertEqual([p["weight"] for p in step["points"]], [1, 4, 1])
        self.assertEqual(step["bracket"], "10.256")
        step = rows(self.result, "simpson38")[0]["step"]
        self.assertEqual([p["weight"] for p in step["points"]], [1, 3, 3, 1])


class IdentityExactTests(SimpleTestCase):
    def test_four_t_minus_t_half(self):
        a, b = Fraction(0), Fraction(4, 5)
        for n in (2, 4, 8):
            with self.subTest(n=n):
                T_n = exact_rule(TRAPEZOID, chapra_exact, a, b, n)
                T_half = exact_rule(TRAPEZOID, chapra_exact, a, b, n // 2)
                self.assertEqual((4 * T_n - T_half) / 3, exact_rule(SIMPSON_13, chapra_exact, a, b, n))


class AlternativePathTests(SimpleTestCase):
    """Las filas reutilizan las evaluaciones de la anterior: deben coincidir con la fórmula de pesos directa."""

    def test_reused_values_match_weights_formula(self):
        for number, f, a, b in ((1, chapra, 0, 0.8), (6, lambda x: 1 / x, 1, 2)):
            for b_ in example(number)["rules"]:
                rule = {"simpson13": SIMPSON_13, "simpson38": SIMPSON_38}[b_["rule"]["key"]]
                for row in b_["rows"][:8]:
                    n = row["n"]
                    direct = apply(rule, [f(b if i == n else a + i * (b - a) / n) for i in range(n + 1)], (b - a) / n)
                    with self.subTest(example=number, rule=rule.key, n=n):
                        self.assertLessEqual(abs(row["S"] - direct), 1e-12 * max(1, abs(direct)))

    def test_more_rows_with_low_tolerance(self):
        result = solve(function=CHAPRA, a=0, b=0.8, tolerance=1e-15, max_iterations=8)
        self.assertEqual(len(rows(result, "simpson13")), 8)


class ExampleTests(SimpleTestCase):
    def test_stop_rows(self):
        for number, stop in ((2, 6), (3, 6), (4, 6), (5, 7), (6, 6)):
            with self.subTest(example=number):
                result = example(number)
                self.assertTrue(result["converged"])
                self.assertEqual(result["iterations_used"], stop)

    def test_first_rows(self):
        expected = (
            (2, "simpson13", (0.74718, 0.746855, 0.746826)),
            (2, "simpson38", (0.746992, 0.746838, 0.746825)),
            (3, "simpson13", (2.094395, 2.00456, 2.000269)),
            (5, "simpson13", (6.666667, 6.416667, 6.401042)),
            (5, "simpson38", (6.518519, 6.407407, 6.400463)),
            (6, "simpson38", (0.69375, 0.693195, 0.69315)),
        )
        for number, key, values in expected:
            for row, S in zip(rows(example(number), key), values):
                with self.subTest(example=number, rule=key, n=row["n"]):
                    self.assertAlmostEqual(row["S"], S, places=6)

    def test_selected_rules(self):
        self.assertEqual([b["rule"]["key"] for b in example(3)["rules"]], ["simpson13"])
        self.assertEqual([b["rule"]["key"] for b in example(6)["rules"]], ["simpson38"])

    def test_reference_integral(self):
        result = example(2)
        self.assertEqual(result["integral"]["kind"], "reference")
        self.assertAlmostEqual(result["integral"]["value"], 0.746824, places=6)

    def test_quartic_error_equals_bound_without_R(self):
        result = example(5)
        for key, errors in (("simpson13", (-0.266667, -0.016667, -0.001042)),
                            ("simpson38", (-0.118519, -0.007407, -0.000463))):
            for row, E in zip(rows(result, key), errors):
                self.assertAlmostEqual(row["true_error"], E, places=6)
            for k, row in enumerate(rows(result, key), start=1):
                with self.subTest(rule=key, n=row["n"]):
                    self.assertAlmostEqual(abs(row["true_error"]), row["bound"], places=12)
                    self.assertAlmostEqual(row["approx_error"], row["true_error"], places=12)
                    self.assertFalse(row["by_rounding"])
                    self.assertTrue(row["within_bound"])
                    # En las últimas filas el redondeo deja |Eₜ| unos 10⁻¹⁵ por debajo: ✔ normal, no «=».
                    if k <= 5:
                        self.assertTrue(row["equals_bound"])

    def test_true_error_within_bound_plus_rounding(self):
        for number in range(1, 7):
            for b in example(number)["rules"]:
                for row in b["rows"]:
                    with self.subTest(example=number, rule=b["rule"]["key"], n=row["n"]):
                        self.assertLessEqual(abs(row["true_error"]), row["bound"] * (1 + 1e-9) + row["rounding"])
                        self.assertTrue(row["within_bound"])


class ConcavityTests(SimpleTestCase):
    def test_sine_overestimates(self):
        self.assertTrue(any("sobreestima" in note for note in example(3)["notes"]))

    def test_chapra_has_no_note(self):
        self.assertFalse(any("estima" in note for note in example(1)["notes"]))


class TableModeTests(SimpleTestCase):
    def test_chapra_table_n8(self):
        result = example(7)
        (app,) = result["applications"]
        self.assertEqual(app["key"], "simpson13")
        self.assertTrue(any("no es múltiplo de 3" in note for note in result["notes"]))
        self.assertEqual([p["weights"][0]["weight"] for p in app["points"]], [1, 4, 2, 4, 2, 4, 2, 4, 1])
        self.assertEqual(app["parts"][0]["step"]["bracket"], "49.184")
        self.assertAlmostEqual(app["total"], 1.639467, places=6)
        self.assertAlmostEqual(app["final"]["true_error"], 0.001067, places=6)
        self.assertAlmostEqual(app["final"]["relative_error"], 0.065, places=3)
        identity = app["identity"]
        self.assertEqual((identity["T_n_display"], identity["T_half_display"]), ("1.6008", "1.4848"))
        self.assertTrue(identity["ok"])

    def test_combination_n5(self):
        result = example(8)
        (app,) = result["applications"]
        self.assertEqual(app["key"], "combined")
        first, second = app["parts"]
        self.assertEqual((first["rule"], first["start"], first["end"]), ("simpson13", 0, 2))
        self.assertEqual((second["rule"], second["start"], second["end"]), ("simpson38", 2, 5))
        self.assertAlmostEqual(first["value"], 0.380324, places=6)
        self.assertAlmostEqual(second["value"], 1.264753, places=6)
        self.assertAlmostEqual(app["total"], 1.645077, places=6)
        self.assertAlmostEqual(app["final"]["true_error"], -0.004544, places=6)
        self.assertAlmostEqual(app["final"]["relative_error"], 0.277, places=3)
        # El punto de unión pertenece a las dos partes.
        self.assertEqual(app["points"][2]["weights"], [{"rule": "simpson13", "weight": 1},
                                                       {"rule": "simpson38", "weight": 1}])
        self.assertEqual([len(p["weights"]) for p in app["points"]], [1, 1, 2, 1, 1, 1])
        self.assertIsNone(app["identity"])

    def test_quartic_table_both_rules(self):
        result = solve(mode="table", points=[[x, x ** 4] for x in range(7)], compare_function="x^4")
        values = {app["key"]: app["total"] for app in result["applications"]}
        self.assertAlmostEqual(values["simpson13"], 1556, places=9)
        self.assertAlmostEqual(values["simpson38"], 1557, places=9)
        self.assertAlmostEqual(result["integral"]["value"], 1555.2, places=9)

    def test_three_segments_only_three_eighths(self):
        result = solve(mode="table", points=[[0, 0], [1, 1], [2, 8], [3, 27]])
        self.assertEqual([app["key"] for app in result["applications"]], ["simpson38"])
        self.assertAlmostEqual(result["applications"][0]["total"], 20.25, places=12)

    def test_altered_data_point_is_flagged(self):
        data = dict(SIMPSON_EXAMPLES[6])
        data["points"] = [list(p) for p in data["points"]]
        data["points"][3][1] = 1.7
        result = solve(**data)
        self.assertFalse(result["verification"]["data"][3]["ok"])
        self.assertTrue(any("Punto 3" in w for w in result["warnings"]))


class DerivativeTests(SimpleTestCase):
    def test_third_and_fourth_derivatives(self):
        fn = example(1)["function"]
        self.assertTrue(fn["fourth"]["steps"]["sum_latex"].endswith("48000 x - 21600"))
        self.assertFalse(fn["fourth"]["constant"])
        self.assertIn("potencia", fn["fourth"]["steps"]["terms"][0]["rule"])
        self.assertEqual(len(fn["third"]["steps"]["terms"]), 4)
        mean = example(1)["mean_fourth"]
        self.assertAlmostEqual(mean["fa_substitution"]["value"], 4050, places=9)
        self.assertAlmostEqual(mean["fb_substitution"]["value"], 2130, places=9)


class ValidationTests(APITestCase):
    URL = "/api/solve/simpson/"

    def assert_error(self, payload, fragment):
        response = self.client.post(self.URL, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn(fragment, str(response.json()))

    def test_errors(self):
        self.assert_error({"function": "x", "a": 0, "b": 1, "rule": "simpson13", "n0_13": 3},
                          "Simpson 1/3 necesita un número par de segmentos, porque cada parábola ocupa 2 segmentos")
        self.assert_error({"function": "x", "a": 0, "b": 1, "rule": "simpson38", "n0_38": 4},
                          "múltiplo de 3, porque cada cúbica ocupa 3 segmentos")
        self.assert_error({"mode": "table", "points": [[0, 1], [0.25, 1], [0.5, 1], [1, 1]]},
                          "entre la fila 3 y la 4 el espaciado es 0.5 y el de la primera pareja es 0.25. "
                          "Con datos de espaciado desigual puedes usar el método del trapecio")
        self.assert_error({"mode": "table", "rule": "simpson13", "points": [[0, 1], [1, 1], [2, 1], [3, 1]]},
                          "«Ambas»")
        self.assert_error({"mode": "table", "rule": "simpson38", "points": [[0, 1], [1, 1], [2, 1], [3, 1], [4, 1]]},
                          "«Simpson 1/3»")
        self.assert_error({"mode": "table", "points": [[0, 1], [1, 1]]}, "se necesitan al menos 2 segmentos")
        self.assert_error({"function": "x", "a": 1, "b": 1}, "debe ser menor")
        self.assert_error({"function": "1/x", "a": 0, "b": 1}, "límite a")


class EndpointTests(APITestCase):
    def test_solve(self):
        response = self.client.post("/api/solve/simpson/", {"function": "x^2", "a": 0, "b": 2}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["category"], "integration")

    def test_catalog_and_examples(self):
        catalog = self.client.get("/api/methods/").json()
        slugs = [m["slug"] for m in catalog]
        self.assertEqual(slugs.index("simpson"), slugs.index("trapecio") + 1)
        method = catalog[slugs.index("simpson")]
        self.assertEqual(method["name"], "Método de Simpson")
        self.assertEqual(method["category_label"], "Integración numérica")
        self.assertEqual(len(self.client.get("/api/examples/?method=simpson").json()), 8)


class PieceChartTests(SimpleTestCase):
    def test_parabolas_pass_through_the_points(self):
        chart = block(example(1), "simpson13")["chart_rows"][0]
        self.assertEqual(len(chart["pieces"]), 1)
        piece = chart["pieces"][0]
        self.assertAlmostEqual(piece["y"][0], chart["y"][0], places=12)
        self.assertAlmostEqual(piece["y"][-1], chart["y"][-1], places=12)
        self.assertEqual([r["n"] for r in block(example(1), "simpson38")["chart_rows"]], [3, 6, 12, 24, 48])
        combined = example(8)["applications"][0]["chart_row"]["pieces"]
        self.assertEqual([p["rule"] for p in combined], ["simpson13", "simpson38"])

    def test_no_stray_values(self):
        self.assertTrue(all(math.isfinite(y) for p in block(example(2), "simpson13")["chart_rows"][0]["pieces"]
                            for y in p["y"]))


def theory_trimmed(result):
    """Como se guarda para la teoría: sin `chart_rows` (la figura de la teoría
    se calcula en el navegador) y las filas con más puntos que `fold` sólo con
    los 8 primeros y los 8 últimos, como en la teoría del trapecio."""
    result = json.loads(json.dumps(result))
    for b in result.get("rules", []):
        b.pop("chart_rows")
        for row in b["rows"]:
            step = row["step"]
            if len(step["points"]) > step["fold"]:
                step["points"] = step["points"][:8] + step["points"][-8:]
    return result


class TheoryExampleTests(SimpleTestCase):
    """La página de teoría usa respuestas guardadas del solver: deben ser las
    que el solver devuelve hoy y mostrar los valores de Chapra."""

    def setUp(self):
        self.saved = json.loads(THEORY_EXAMPLE.read_text(encoding="utf-8"))

    def test_row_one_of_both_rules(self):
        saved = self.saved["function"]
        expected = {
            # S, Eₜ, εₜ, Eₐ, cota
            "simpson13": ("1.367467", "0.273067", "16.644993", "0.273067", "2.4576"),
            "simpson38": ("1.51917", "0.121363", "7.397775", "0.121363", "1.092267"),
        }
        for key, values in expected.items():
            row = rows(saved, key)[0]
            shown = tuple(f"{row[k]:.6f}".rstrip("0").rstrip(".")
                          for k in ("S", "true_error", "relative_error", "approx_error", "bound"))
            self.assertEqual(shown, values, key)
        self.assertEqual(saved["iterations_used"], 7)
        self.assertEqual(f"{self.saved['table']['applications'][0]['total']:.6f}", "1.645077")

    def test_saved_responses_match_solver(self):
        for key, number in (("function", 1), ("table", 8)):
            with self.subTest(example=number):
                stored = self.saved[key]
                self.assertEqual(theory_trimmed(example(number)), {k: v for k, v in stored.items() if k != "request"})
