"""Método del trapecio: valores de referencia verificados con un script
independiente (fracciones exactas y los ejemplos precargados)."""

import json
import math
from fractions import Fraction
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from rest_framework.test import APITestCase

from numeric_methods.examples_data import TRAPEZOID_EXAMPLES
from numeric_methods.serializers.integration import IntegrationSerializer
from numeric_methods.solvers.integration import exact
from numeric_methods.solvers.integration.rules import TRAPEZOID, apply
from numeric_methods.solvers.integration.trapezoid import solve_trapezoid

# Respuestas del solver guardadas para la página de teoría (frontend).
THEORY_EXAMPLE = (Path(__file__).resolve().parents[3] / "frontend" / "src" / "methods"
                  / "integration" / "theory" / "trapezoidExample.json")

CHAPRA = "0.2 + 25x - 200x^2 + 675x^3 - 900x^4 + 400x^5"


def chapra(x):
    return 0.2 + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5


def solve(**data):
    serializer = IntegrationSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return solve_trapezoid(serializer.validated_data).to_dict()


def example(number):
    return solve(**TRAPEZOID_EXAMPLES[number - 1])


def rows(result):
    return [step["extra"] for step in result["iterations"]]


class ExactFractionTests(SimpleTestCase):
    def test_square_on_zero_two(self):
        result = solve(function="x^2", a=0, b=2)
        for row, T, E in zip(rows(result), (4, 3, Fraction(11, 4)), (Fraction(-4, 3), Fraction(-1, 3), Fraction(-1, 12))):
            self.assertAlmostEqual(row["T"], float(T), places=12)
            self.assertAlmostEqual(row["true_error"], float(E), places=12)
            self.assertAlmostEqual(row["approx_error"], float(E), places=12)

    def test_chapra_polynomial(self):
        result = solve(function=CHAPRA, a=0, b=0.8)
        for row, T in zip(rows(result), (Fraction(108, 625), Fraction(668, 625), Fraction(928, 625))):
            self.assertAlmostEqual(row["T"], float(T), places=12)


class ChapraExampleTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.result = example(1)

    def test_first_rows(self):
        expected = [
            # T, Eₜ, εₜ, Eₐ, cota
            (0.1728, 1.467733, 89.4668, 2.56, 17.066667),
            (1.0688, 0.571733, 34.8505, 0.64, 4.266667),
            (1.4848, 0.155733, 9.4928, 0.16, 1.066667),
        ]
        for row, (T, E, rel, Ea, bound) in zip(rows(self.result), expected):
            self.assertAlmostEqual(row["T"], T, places=6)
            self.assertAlmostEqual(row["true_error"], E, places=6)
            self.assertAlmostEqual(row["relative_error"], rel, places=4)
            self.assertAlmostEqual(row["approx_error"], Ea, places=6)
            self.assertAlmostEqual(row["bound"], bound, places=6)
        self.assertAlmostEqual(self.result["mean_second"]["value"], -60, places=9)
        self.assertEqual(self.result["M2"]["value"], 400)
        self.assertEqual(self.result["integral"]["kind"], "exact")
        self.assertAlmostEqual(self.result["integral"]["value"], 3076 / 1875, places=12)

    def test_stops_at_row_13(self):
        self.assertTrue(self.result["converged"])
        self.assertEqual(self.result["iterations_used"], 13)
        last = rows(self.result)[-1]
        self.assertEqual(last["n"], 4096)
        self.assertAlmostEqual(last["T"], 1.640533, places=6)

    def test_ratio_tends_to_a_quarter(self):
        for row in rows(self.result)[4:8]:
            self.assertTrue(0.24 <= row["ratio"] <= 0.26, row["ratio"])

    def test_term_by_term_check(self):
        check = self.result["verification"]
        values = [round(t["value"], 6) for t in check["upper"]["terms"]]
        self.assertEqual(values, [0.16, 8, -34.133333, 69.12, -58.9824, 17.476267])
        self.assertAlmostEqual(check["upper"]["value"], 1.640533, places=6)
        self.assertEqual(check["lower"]["value"], 0)
        self.assertTrue(check["lower"]["all_zero"])
        self.assertIn(r"\frac{200}{3} x^{3}", self.result["integral"]["antiderivative"]["latex"])
        self.assertTrue(check["all_within"])

    def test_no_concavity_note(self):
        self.assertFalse(any("f''" in note for note in self.result["notes"]))

    def test_first_row_step(self):
        step = rows(self.result)[0]["step"]
        self.assertEqual(step["kind"], "formula")
        self.assertEqual(step["ends"], ["0.2", "0.232"])
        self.assertEqual(step["factor_h"]["text"], "0.4")
        self.assertEqual(step["bracket"], "0.432")


class RecurrenceTests(SimpleTestCase):
    def test_recurrence_matches_direct_formula(self):
        for number, f, a, b in ((1, chapra, 0, 0.8), (6, math.exp, 0, 1)):
            result = example(number)
            for row in rows(result)[1:8]:
                n = row["n"]
                h = (b - a) / n
                direct = apply(TRAPEZOID, [f(b if i == n else a + i * (b - a) / n) for i in range(n + 1)], h)
                with self.subTest(example=number, n=n):
                    self.assertLessEqual(abs(row["T"] - direct), 1e-12 * max(1, abs(direct)))

    def test_recurrence_by_hand(self):
        result = example(1)
        second, third = rows(result)[1:3]
        self.assertAlmostEqual(second["T"], 0.1728 / 2 + 0.4 * chapra(0.4), places=12)
        self.assertAlmostEqual(second["T"], 1.0688, places=12)
        self.assertAlmostEqual(third["T"], 1.0688 / 2 + 0.2 * (chapra(0.2) + chapra(0.6)), places=12)
        self.assertAlmostEqual(third["T"], 1.4848, places=12)
        self.assertEqual(second["step"]["kind"], "recurrence")
        self.assertEqual(second["step"]["previous"], "0.1728")
        self.assertEqual(second["step"]["sum"], "2.456")
        self.assertEqual(second["step"]["product"], "0.9824")


class ExampleTests(SimpleTestCase):
    def test_stop_rows(self):
        for number, stop in ((2, 10), (3, 13), (4, 12), (5, 6), (6, 10)):
            with self.subTest(example=number):
                result = example(number)
                self.assertTrue(result["converged"])
                self.assertEqual(result["iterations_used"], stop)

    def test_examples_first_rows(self):
        for number, values in ((2, (0.68394, 0.73137, 0.742984)), (3, (0, 1.570796, 1.896119)),
                               (4, (4, 3, 2.75)), (6, (1.753931, 1.727222, 1.720519))):
            result = example(number)
            for row, T in zip(rows(result), values):
                with self.subTest(example=number, n=row["n"]):
                    self.assertAlmostEqual(row["T"], T, places=6)

    def test_straight_line_is_exact(self):
        for row in rows(example(5)):
            self.assertAlmostEqual(row["T"], 10, places=12)
            self.assertEqual(row["bound"], 0)
            self.assertAlmostEqual(row["true_error"], 0, places=12)

    def test_true_error_within_bound_in_every_row(self):
        for number in range(1, 7):
            with self.subTest(example=number):
                self.assertTrue(all(row["within_bound"] for row in rows(example(number))))

    def test_square_error_equals_bound(self):
        for row in rows(example(4)):
            self.assertAlmostEqual(abs(row["true_error"]), row["bound"], places=12)
            self.assertAlmostEqual(row["approx_error"], row["true_error"], places=12)


class IntegralTests(SimpleTestCase):
    def test_reference_with_erf(self):
        result = example(2)
        self.assertEqual(result["integral"]["kind"], "reference")
        self.assertAlmostEqual(result["integral"]["value"], 0.746824, places=6)
        self.assertTrue(any("erf(x)" in note for note in result["notes"]))

    def test_exact_sine(self):
        result = example(3)
        self.assertEqual(result["integral"]["kind"], "exact")
        self.assertAlmostEqual(result["integral"]["value"], 2, places=12)
        # sin(π) en punto flotante es 1.2e-16, no 0: T₁ ≈ 1.9e-16.
        self.assertAlmostEqual(rows(result)[0]["relative_error"], 100, places=9)

    def test_exact_reciprocal(self):
        result = solve(function="1/x", a=1, b=2)
        self.assertEqual(result["integral"]["kind"], "exact")
        self.assertAlmostEqual(result["integral"]["value"], math.log(2), places=12)
        first, second = rows(result)[:2]
        self.assertAlmostEqual(first["T"], 0.75, places=12)
        self.assertAlmostEqual(second["T"], 0.708333, places=6)

    def test_timeout_falls_back_to_reference(self):
        with mock.patch.dict(exact._CACHE, clear=True), \
                mock.patch.object(exact, "_integrate_with_timeout", return_value=exact.TIMED_OUT):
            result = solve(function="x^2", a=0, b=2)
        self.assertEqual(result["integral"]["kind"], "reference")
        self.assertAlmostEqual(result["integral"]["value"], 8 / 3, places=12)
        self.assertTrue(result["integral"]["timed_out"])
        self.assertTrue(any("límite" in note for note in result["notes"]))

    def test_real_timeout_kills_the_worker(self):
        with mock.patch.dict(exact._CACHE, clear=True):
            self.assertEqual(exact._integrate_with_timeout(*_hard_integral(), timeout=0.01), exact.TIMED_OUT)


def _hard_integral():
    import sympy as sp

    x = sp.Symbol("x", real=True)
    return sp.exp(sp.sin(x) ** 3) * sp.tan(x ** 2 + 1) ** 5, x


class ConcavityTests(SimpleTestCase):
    def test_sine_underestimates(self):
        self.assertTrue(any("subestima" in note for note in example(3)["notes"]))

    def test_square_overestimates(self):
        self.assertTrue(any("sobreestima" in note for note in example(4)["notes"]))


class TableModeTests(SimpleTestCase):
    def test_uniform_chapra_table(self):
        result = example(7)
        self.assertEqual(result["verification"]["areas"],
                         ["0.07445", "0.12885", "0.14475", "0.20315", "0.28905", "0.33945", "0.29135", "0.12975"])
        self.assertAlmostEqual(result["total"], 1.6008, places=12)
        self.assertTrue(result["uniform"])
        self.assertTrue(result["composite"]["equal"])
        self.assertAlmostEqual(result["composite"]["value"], 1.6008, places=12)
        final = result["verification"]["final"]
        self.assertAlmostEqual(final["true_error"], 0.039733, places=6)
        self.assertAlmostEqual(final["relative_error"], 2.422, places=3)
        self.assertTrue(final["within_bound"])

    def test_unequal_segments(self):
        result = example(8)
        self.assertEqual(result["verification"]["areas"],
                         ["0.090584", "0.130749", "0.152432", "0.076366", "0.090618", "0.10598",
                          "0.317514", "0.334461", "0.166348", "0.12975"])
        self.assertAlmostEqual(result["total"], 1.594801, places=6)
        self.assertFalse(result["uniform"])
        self.assertIsNone(result["composite"])
        self.assertTrue(any("no uniforme" in note for note in result["notes"]))
        final = result["verification"]["final"]
        self.assertAlmostEqual(final["true_error"], 0.045732, places=6)
        self.assertAlmostEqual(final["relative_error"], 2.7877, places=4)
        self.assertTrue(all(row["ok"] for row in result["verification"]["data"]))

    def test_altered_data_point_is_flagged(self):
        data = dict(TRAPEZOID_EXAMPLES[6])
        data["points"] = [list(p) for p in data["points"]]
        data["points"][3][1] = 1.7
        result = solve(**data)
        self.assertFalse(result["verification"]["data"][3]["ok"])
        self.assertTrue(any("Punto 3" in w for w in result["warnings"]))

    def test_without_compare_function(self):
        result = solve(mode="table", points=[[0, 1], [1, 3], [3, 3]])
        self.assertEqual(result["total"], 2 + 6)
        self.assertIsNone(result["integral"])
        self.assertIsNone(result["verification"]["final"])


class SingularityTests(SimpleTestCase):
    def test_interior_singularity_stops(self):
        result = solve(function="1/(x - 1)", a=0, b=2)
        self.assertFalse(result["converged"])
        self.assertEqual(result["iterations_used"], 1)
        self.assertTrue(any("x = 1," in w and "puede no existir" in w for w in result["warnings"]))


class ValidationTests(APITestCase):
    URL = "/api/solve/trapecio/"

    def assert_error(self, payload, fragment):
        response = self.client.post(self.URL, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn(fragment, str(response.json()))

    def test_errors(self):
        self.assert_error({"function": "x", "a": 2, "b": 1}, "El límite inferior a debe ser menor que el límite superior b")
        self.assert_error({"function": "x", "a": 1, "b": 1}, "debe ser menor")
        self.assert_error({"function": "1/x", "a": 0, "b": 1}, "límite a")
        self.assert_error({"function": "y + 1", "a": 0, "b": 1}, "f(x)")
        self.assert_error({"function": "x", "a": 0, "b": 1, "n0": 0}, "n₀")
        self.assert_error({"function": "x", "a": 0, "b": 1, "n0": 1001}, "n₀")
        self.assert_error({"function": "x", "a": 0, "b": 1, "max_iterations": 5}, "entre 6 y 22")
        self.assert_error({"function": "x", "a": 0, "b": 1, "max_iterations": 23}, "entre 6 y 22")
        self.assert_error({"mode": "table", "points": [[0, 1], [2, 1], [1, 1]]}, "Fila 3")
        self.assert_error({"mode": "table", "points": [[0, 1]]}, "entre 2 y 30")

    def test_singularity_in_first_row_is_400(self):
        self.assert_error({"function": "1/(x - 1)", "a": 0, "b": 2, "n0": 2}, "x = 1,")


class EndpointTests(APITestCase):
    def test_solve(self):
        response = self.client.post("/api/solve/trapecio/", {"function": "x^2", "a": 0, "b": 2}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["category"], "integration")

    def test_catalog_and_examples(self):
        catalog = self.client.get("/api/methods/").json()
        method = next(m for m in catalog if m["slug"] == "trapecio")
        self.assertEqual(method["category_label"], "Integración numérica")
        self.assertEqual(method["name"], "Método del trapecio")
        examples = self.client.get("/api/examples/?method=trapecio").json()
        self.assertEqual(len(examples), 8)


class ExplanationTests(SimpleTestCase):
    """Datos que el backend envía para el paso a paso explicado (ejemplo 4: x² en [0, 2])."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.square = example(4)
        cls.chapra = example(1)

    def test_square_first_row(self):
        row = rows(self.square)[0]
        points = row["step"]["points"]
        self.assertEqual([p["f_display"] for p in points], ["0", "4"])
        self.assertEqual([p["terms"] for p in points], [[0], [4]])
        self.assertEqual([p["product"] for p in points], ["0", "4"])
        self.assertEqual(row["step"]["bracket"], "4")
        self.assertEqual(row["T"], 4)
        mean = self.square["mean_second"]
        self.assertEqual((mean["fb_substitution"]["value"], mean["fa_substitution"]["value"]), (4, 0))
        self.assertEqual(mean["value"], 2)
        self.assertAlmostEqual(row["approx_error"], -1.333333, places=6)
        self.assertEqual(self.square["M2"]["value"], 2)
        self.assertIsNone(self.square["M2"]["substitution"])
        self.assertAlmostEqual(row["bound"], 1.333333, places=6)
        self.assertEqual(row["coefficient_numerator"]["text"], "8")
        self.assertTrue(row["equals_bound"])
        self.assertTrue(row["within_bound"])
        self.assertFalse(row["by_rounding"])

    def test_square_rows_two_and_three(self):
        second, third = rows(self.square)[1:3]
        self.assertEqual([p["x_display"]["text"] for p in second["step"]["points"]], ["1"])
        self.assertEqual([p["x_display"]["text"] for p in third["step"]["points"]], ["0.5", "1.5"])
        self.assertEqual((second["step"]["sum"], third["step"]["sum"]), ("1", "2.5"))
        self.assertEqual((second["T"], third["T"]), (3, 2.75))
        self.assertFalse(second["below_tolerance"])

    def test_derivative_steps(self):
        first, second = self.square["function"]["first"], self.square["function"]["second"]
        self.assertTrue(first["steps"]["terms"][0]["latex"].endswith("= 2 x"))
        self.assertIn("potencia", first["steps"]["terms"][0]["rule"])
        self.assertTrue(second["steps"]["terms"][0]["latex"].endswith("= 2"))
        self.assertTrue(second["constant"])
        chapra = self.chapra["function"]
        self.assertEqual(len(chapra["first"]["steps"]["terms"]), 6)
        self.assertIn(r"\left(- 200 x^{2}\right) = \left(-200\right) \cdot 2 \cdot x = - 400 x",
                      chapra["first"]["steps"]["terms"][3]["latex"])
        self.assertTrue(chapra["first"]["steps"]["sum_latex"].endswith("- 400 x + 25"))
        self.assertTrue(chapra["second"]["steps"]["sum_latex"].endswith("4050 x - 400"))
        self.assertFalse(chapra["second"]["constant"])
        exponential = example(6)["function"]["first"]["steps"]["terms"][0]
        self.assertEqual(exponential["latex"], r"\frac{d}{d x}\left(e^{x}\right) = e^{x}")
        self.assertIn("exponencial", exponential["rule"])

    def test_chapra_M2_substitution(self):
        M2 = self.chapra["M2"]
        self.assertEqual(M2["value"], 400)
        self.assertEqual(M2["substitution"]["value"], -400)
        self.assertEqual(len(M2["substitution"]["terms"]), 4)

    def test_antiderivative_steps(self):
        square = self.square["integral"]["antiderivative"]
        self.assertTrue(square["steps"]["detailed"])
        self.assertEqual(square["steps"]["terms"][0]["latex"],
                         r"\int x^{2}\,dx = \frac{x^{2 + 1}}{2 + 1} = \frac{1}{3} x^{3}")
        self.assertTrue(square["check"]["ok"])
        self.assertEqual(square["check"]["sum_latex"], "F'(x) = x^{2}")
        chapra = self.chapra["integral"]["antiderivative"]
        results = [t["latex"].rsplit(" = ", 1)[1] for t in chapra["steps"]["terms"]]
        self.assertEqual(results, ["0.2 x", "12.5 x^{2}", r"- \frac{200}{3} x^{3}", "168.75 x^{4}",
                                   "- 180 x^{5}", r"\frac{200}{3} x^{6}"])
        self.assertTrue(chapra["check"]["ok"])
        self.assertEqual(chapra["check"]["sum_latex"],
                         "F'(x) = 0.2 + 25 x - 200 x^{2} + 675 x^{3} - 900 x^{4} + 400 x^{5}")

    def test_not_detailed_antiderivative(self):
        result = solve(function="x*exp(x)", a=0, b=1)
        antiderivative = result["integral"]["antiderivative"]
        self.assertFalse(antiderivative["steps"]["detailed"])
        self.assertTrue(antiderivative["check"]["ok"])

    def test_true_error_shown_as_zero(self):
        # La vista agrega la nota cuando |Eₜ| < 0.0000005 y εₜ no se ve 0.
        final = example(6)["verification"]["final"]
        self.assertLess(abs(final["true_error"]), 5e-7)
        self.assertEqual(round(final["relative_error"], 6), 0.000008)

    def test_no_rounding_mark_within_bound(self):
        for number in range(1, 7):
            for row in rows(example(number)):
                if row["bound"] is None or row["true_error"] is None:
                    continue
                with self.subTest(example=number, n=row["n"]):
                    if abs(row["true_error"]) <= row["bound"] * (1 + 1e-9):
                        self.assertFalse(row["by_rounding"])

    def test_integral_parentheses_only_for_sums(self):
        self.assertFalse(self.square["function"]["is_sum"])
        self.assertTrue(self.chapra["function"]["is_sum"])

    def test_large_rows_send_sixteen_points(self):
        last = rows(self.chapra)[-1]
        self.assertEqual(last["step"]["count"], 2048)
        self.assertEqual(len(last["step"]["points"]), 16)
        row_12 = rows(self.chapra)[11]
        self.assertEqual(row_12["step"]["count"], 1024)
        self.assertEqual(len(row_12["step"]["points"]), 1024)


def trimmed(result):
    """Como se guarda para la teoría: las filas con más puntos que `fold` sólo
    con los 8 primeros y los 8 últimos (lo mismo que hace el solver con más de
    1024), para que el JSON no pese 1.4 MB."""
    result = json.loads(json.dumps(result))
    for step in result["iterations"]:
        shown = step["extra"].get("step")
        if shown and len(shown["points"]) > shown["fold"]:
            shown["points"] = shown["points"][:8] + shown["points"][-8:]
    return result


class TheoryExampleTests(SimpleTestCase):
    """La página de teoría usa respuestas guardadas del solver: deben ser las
    que el solver devuelve hoy y mostrar los valores de Chapra."""

    def setUp(self):
        self.saved = json.loads(THEORY_EXAMPLE.read_text(encoding="utf-8"))

    def test_rows_one_to_three(self):
        saved = self.saved["function"]
        expected = [
            # T, Eₜ, εₜ, Eₐ, cota
            ("0.1728", "1.467733", "89.46684", "2.56", "17.066667"),
            ("1.0688", "0.571733", "34.850455", "0.64", "4.266667"),
            ("1.4848", "0.155733", "9.492848", "0.16", "1.066667"),
        ]
        for row, values in zip(rows(saved), expected):
            shown = tuple(f"{row[key]:.6f}".rstrip("0").rstrip(".")
                          for key in ("T", "true_error", "relative_error", "approx_error", "bound"))
            self.assertEqual(shown, values)
        self.assertEqual(saved["iterations_used"], 13)
        self.assertEqual(rows(saved)[-1]["n"], 4096)
        self.assertEqual(f"{self.saved['table']['total']:.6f}", "1.594801")

    def test_saved_responses_match_solver(self):
        for key, number in (("function", 1), ("table", 8)):
            with self.subTest(example=number):
                stored = self.saved[key]
                self.assertEqual(trimmed(example(number)), {k: v for k, v in stored.items() if k != "request"})
