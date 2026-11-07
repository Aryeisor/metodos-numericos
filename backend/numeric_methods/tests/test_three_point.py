import json
from pathlib import Path
from unittest import skipUnless

from django.test import SimpleTestCase
from rest_framework.test import APITestCase

from numeric_methods.examples_data import EXAMPLES
from numeric_methods.serializers.differentiation import ThreePointSerializer
from numeric_methods.solvers.differentiation.display import fixed
from numeric_methods.solvers.differentiation.three_point import solve_three_point

URL = "/api/solve/tres-puntos/"
EXAMPLE = {example["id"]: example for example in EXAMPLES["tres-puntos"]}
MID, AHEAD, BEHIND = "punto_medio", "extremo_adelante", "extremo_atras"

# Respuestas del solver guardadas para la página de teoría (frontend).
THEORY_EXAMPLE = (Path(__file__).resolve().parents[3] / "frontend" / "src" / "methods"
                  / "differentiation" / "theory" / "threePointExample.json")


def solve(**data):
    serializer = ThreePointSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return solve_three_point(serializer.validated_data).to_dict()


def example(example_id, **changes):
    return solve(**{**EXAMPLE[example_id], **changes})


def row(result, k, key):
    return result["iterations"][k - 1]["extra"][key]


class ExactFractionTests(SimpleTestCase):
    def test_cubic(self):
        result = solve(function="x^3 - 2x^2 + x", x0=2, h0=0.1)
        self.assertAlmostEqual(row(result, 1, MID)["D"], 501 / 100, places=12)
        self.assertAlmostEqual(row(result, 1, AHEAD)["D"], 249 / 50, places=12)
        self.assertAlmostEqual(row(result, 1, BEHIND)["D"], 249 / 50, places=12)

    def test_square_is_exact(self):
        result = solve(function="x^2", x0=3, h0=0.1)
        for key in (MID, AHEAD, BEHIND):
            self.assertAlmostEqual(row(result, 1, key)["D"], 6, places=12)


class FunctionModeTests(SimpleTestCase):
    def test_burden_first_rows_and_stop(self):
        result = example("tp-burden-xexp")
        self.assertEqual(fixed(result["exact"]), "22.167168")
        first = {
            MID: ("22.228787", "0.061619", "0.069412"),
            AHEAD: ("22.032305", "0.134863", "0.156434"),
            BEHIND: ("22.054521", "0.112647", "0.123151"),
        }
        for key, (D, real, bound) in first.items():
            item = row(result, 1, key)
            self.assertEqual(fixed(item["D"]), D)
            self.assertEqual(fixed(item["real_error"]), real)
            self.assertEqual(fixed(item["bound"]), bound)
        second = {MID: "22.182565", AHEAD: "22.134957", BEHIND: "22.137729"}
        for key, D in second.items():
            self.assertEqual(fixed(row(result, 2, key)["D"]), D)
        self.assertTrue(result["converged"])
        self.assertEqual(result["iterations_used"], 11)

    def test_comparison_with_differences(self):
        comparison = example("tp-burden-xexp")["comparison"]
        self.assertEqual(len(comparison), 2)
        first = comparison[0]
        self.assertEqual(fixed(first["forward"]["D"]), "23.708446")
        self.assertEqual(fixed(first["backward"]["D"]), "20.749128")
        self.assertEqual(fixed(first["forward"]["real_error"]), "1.541278")
        self.assertEqual(fixed(first["backward"]["real_error"]), "1.418041")
        self.assertIn("Con h = 0.1, la diferencia progresiva daría 23.708446 (error 1.541278) y la regresiva "
                      "20.749128 (error 1.418041).", first["text"])
        self.assertIn("punto medio 22.228787 (error 0.061619: 25 veces menor que el de la progresiva",
                      first["text"])
        self.assertEqual(comparison[1]["k"], 11)

    def test_stop_rows(self):
        for example_id, rows in (("tp-ln", 7), ("tp-seno", 7), ("tp-cubica", 9),
                                 ("tp-cuadratica", 6), ("tp-gauss", 9)):
            with self.subTest(example=example_id):
                result = example(example_id)
                self.assertTrue(result["converged"])
                self.assertEqual(result["iterations_used"], rows)

    def test_first_rows_of_other_examples(self):
        cases = {
            "tp-ln": {MID: ("0.556128", "0.000573"), AHEAD: ("0.554542", "0.001014"), BEHIND: ("0.554253", "0.001302")},
            "tp-seno": {MID: ("0.539402", "0.0009")},
            "tp-cubica": {MID: ("5.01", "0.01"), AHEAD: ("4.98", "0.02"), BEHIND: ("4.98", "0.02")},
            "tp-gauss": {BEHIND: ("-0.791208", "0.012407")},
        }
        for example_id, formulas in cases.items():
            result = example(example_id)
            for key, (D, real) in formulas.items():
                with self.subTest(example=example_id, formula=key):
                    self.assertEqual(fixed(row(result, 1, key)["D"]), D)
                    self.assertEqual(fixed(row(result, 1, key)["real_error"]), real)
        self.assertEqual(fixed(row(example("tp-seno"), 1, MID)["bound"]), "0.001036")
        self.assertEqual(fixed(row(example("tp-gauss"), 1, BEHIND)["bound"]), "0.01298")
        cubic = example("tp-cubica")
        for key, D in ((MID, "5.0025"), (AHEAD, "4.995"), (BEHIND, "4.995")):
            self.assertEqual(fixed(row(cubic, 2, key)["D"]), D)
        for key in (MID, AHEAD, BEHIND):
            self.assertEqual(fixed(row(cubic, 1, key)["bound"]), fixed(row(cubic, 1, key)["real_error"]))

    def test_quadratic_is_exact(self):
        result = example("tp-cuadratica")
        for step in result["iterations"]:
            for key in (MID, AHEAD, BEHIND):
                self.assertAlmostEqual(step["extra"][key]["D"], 1, places=12)
                self.assertAlmostEqual(step["extra"][key]["real_error"], 0, places=12)
                self.assertEqual(step["extra"][key]["bound"], 0)

    def test_ratio_is_about_one_quarter(self):
        result = example("tp-burden-xexp")
        for k in range(2, 7):
            for key in (MID, AHEAD):
                with self.subTest(k=k, formula=key):
                    self.assertTrue(0.23 <= row(result, k, key)["ratio"] <= 0.26)

    def test_real_error_within_bound_plus_rounding(self):
        for example_id, data in EXAMPLE.items():
            if data["mode"] != "function":
                continue
            result = example(example_id)
            self.assertTrue(result["verification"]["all_within"], example_id)
            for step in result["iterations"]:
                for key in result["variables"]:
                    item = step["extra"][key]
                    self.assertLessEqual(item["real_error"], item["bound"] + item["rounding"],
                                         (example_id, step["iteration"], key))

    def test_identities_of_row_one(self):
        identities = {i["key"]: i for i in example("tp-burden-xexp")["verification"]["identities"]}
        self.assertEqual(set(identities), {MID, AHEAD, BEHIND})
        self.assertTrue(all(i["ok"] for i in identities.values()))
        self.assertEqual(fixed(identities[MID]["forward"]), "23.708446")
        self.assertEqual(fixed(identities[MID]["backward"]), "20.749128")
        self.assertEqual(fixed(identities[MID]["value"]), "22.228787")
        self.assertEqual(fixed(identities[AHEAD]["value"]), "22.032305")
        self.assertEqual(fixed(identities[BEHIND]["value"]), "22.054521")

    def test_higher_derivatives_term_by_term(self):
        higher = example("tp-burden-xexp")["function"]["higher_derivatives"]
        self.assertEqual(higher["2"]["steps"]["sum_latex"], "f''(x) = x e^{x} + e^{x} + e^{x} = x e^{x} + 2 e^{x}")
        self.assertEqual(higher["3"]["steps"]["sum_latex"], "f'''(x) = x e^{x} + e^{x} + 2 e^{x} = x e^{x} + 3 e^{x}")
        cubic = example("tp-cubica")["function"]["higher_derivatives"]
        self.assertEqual(len(cubic["2"]["steps"]["terms"]), 3)
        self.assertTrue(cubic["3"]["steps"]["sum_latex"].endswith("= 6"))

    def test_step_shows_each_product(self):
        item = row(example("tp-burden-xexp"), 1, AHEAD)
        self.assertEqual(item["products_display"], ["-44.3343366", "68.59582728", "-19.8550297"])
        self.assertEqual(item["denominator_display"], "0.2")
        self.assertEqual(item["numerator_display"], "4.40646098")
        self.assertEqual([p["role"] for p in item["points"]], ["x_0", "x_0 + h", "x_0 + 2h"])


class TableModeTests(SimpleTestCase):
    def values(self, result, key):
        return [None if step["extra"][key] is None else fixed(step["extra"][key]["D"])
                for step in result["iterations"]]

    def recommended(self, result):
        return [(fixed(s["extra"]["recommended"]["D"]), s["extra"]["recommended"]["key"])
                for s in result["iterations"]]

    def test_burden_table(self):
        result = example("tp-tabla-burden")
        self.assertEqual(self.values(result, AHEAD), ["16.832945", "19.26947", "22.03231", None, None])
        self.assertEqual(self.values(result, MID), [None, "19.443735", "22.22879", "25.38459", None])
        self.assertEqual(self.values(result, BEHIND), [None, None, "22.054525", "25.18811", "28.73687"])
        self.assertEqual([fixed(s["extra"]["exact"]) for s in result["iterations"]],
                         ["16.939013", "19.389094", "22.167168", "25.315127", "28.880043"])
        self.assertEqual(self.recommended(result), [
            ("16.832945", AHEAD), ("19.443735", MID), ("22.22879", MID), ("25.38459", MID), ("28.73687", BEHIND),
        ])
        check = result["verification"]
        self.assertTrue(all(item["ok"] for item in check["data"]))
        self.assertTrue(all(item["difference"] < 0.0000005 for item in check["data"]))
        identities = {i["key"]: i for i in check["identities"][2]["items"]}
        self.assertEqual(fixed(identities[MID]["forward"]), "23.70845")
        self.assertEqual(fixed(identities[MID]["backward"]), "20.74913")
        self.assertEqual(fixed(identities[MID]["value"]), "22.22879")
        self.assertEqual(fixed(identities[AHEAD]["base"]), "23.70845")
        self.assertEqual(fixed(identities[AHEAD]["double"]), "25.38459")
        self.assertEqual(fixed(identities[AHEAD]["value"]), "22.03231")
        self.assertTrue(all(i["ok"] for point in check["identities"] for i in point["items"]))
        self.assertEqual([len(point["items"]) for point in check["identities"]], [1, 2, 3, 2, 1])

    def test_step_products_with_table_data(self):
        item = row(example("tp-tabla-burden"), 3, AHEAD)
        self.assertEqual(item["products_display"], ["-44.334336", "68.595828", "-19.85503"])
        self.assertEqual(item["denominator_display"], "0.2")
        self.assertEqual(item["numerator_display"], "4.406462")

    def test_cubes_without_function(self):
        result = example("tp-tabla-cubos")
        self.assertEqual(self.values(result, AHEAD), ["-2", "1", "10", "25", None, None])
        self.assertEqual(self.values(result, MID), [None, "4", "13", "28", "49", None])
        self.assertEqual(self.values(result, BEHIND), [None, None, "10", "25", "46", "73"])
        self.assertEqual([value for value, _ in self.recommended(result)], ["-2", "4", "13", "28", "49", "73"])
        self.assertIsNone(result["function"])
        self.assertIsNone(result["verification"]["data"])
        self.assertTrue(all(i["ok"] for point in result["verification"]["identities"] for i in point["items"]))

    def test_cubes_with_function(self):
        result = example("tp-tabla-cubos", compare_function="x^3")
        for step in result["iterations"]:
            for key, error in ((MID, 1), (AHEAD, 2), (BEHIND, 2)):
                item = step["extra"][key]
                if item:
                    self.assertAlmostEqual(item["real_error"], error, places=12)
                    self.assertAlmostEqual(item["bound"], error, places=12)
                    self.assertTrue(item["within_bound"])
        self.assertTrue(result["verification"]["all_within"])

    def test_single_formula_shows_one_column(self):
        result = example("tp-tabla-cubos", formula="punto_medio")
        self.assertEqual(result["variables"], [MID])
        self.assertEqual([value for value, _ in self.recommended(result)], ["-2", "4", "13", "28", "49", "73"])

    def test_altered_data_point(self):
        points = [list(p) for p in EXAMPLE["tp-tabla-burden"]["points"]]
        points[2][1] = 14.8
        result = example("tp-tabla-burden", points=points)
        self.assertEqual([item["ok"] for item in result["verification"]["data"]], [True, True, False, True, True])
        self.assertTrue(any("Punto 3: el dato no coincide con la función" in w for w in result["warnings"]))


@skipUnless(THEORY_EXAMPLE.exists(), "sin el frontend (p. ej. en la imagen Docker del backend)")
class TheoryExampleTests(SimpleTestCase):
    """La página de teoría usa respuestas guardadas del solver: deben ser las
    que el solver devuelve hoy y mostrar los valores del libro."""

    def setUp(self):
        self.saved = json.loads(THEORY_EXAMPLE.read_text(encoding="utf-8"))

    def test_rows_one_and_two_and_identities(self):
        result = self.saved["function"]
        expected = {
            1: {MID: ("22.228787", "0.061619", "0.069412"),
                AHEAD: ("22.032305", "0.134863", "0.156434"),
                BEHIND: ("22.054521", "0.112647", "0.123151")},
            2: {MID: ("22.182565", "0.015397", None),
                AHEAD: ("22.134957", "0.032212", None),
                BEHIND: ("22.137729", "0.029439", None)},
        }
        for k, formulas in expected.items():
            for key, (D, real, bound) in formulas.items():
                with self.subTest(k=k, formula=key):
                    item = row(result, k, key)
                    self.assertEqual(fixed(item["D"]), D)
                    self.assertEqual(fixed(item["real_error"]), real)
                    if bound:
                        self.assertEqual(fixed(item["bound"]), bound)
        identities = {i["key"]: i for i in result["verification"]["identities"]}
        self.assertTrue(all(i["ok"] for i in identities.values()))
        self.assertEqual(fixed(identities[AHEAD]["double"]), "25.384588")
        self.assertEqual([fixed(identities[key]["value"]) for key in (MID, AHEAD, BEHIND)],
                         ["22.228787", "22.032305", "22.054521"])
        self.assertEqual(result["iterations_used"], 11)

    def test_saved_responses_match_solver(self):
        for key, example_id in (("function", "tp-burden-xexp"), ("table", "tp-tabla-burden")):
            with self.subTest(example=example_id):
                stored = self.saved[key]
                self.assertEqual(json.loads(json.dumps(example(example_id))),
                                 {k: v for k, v in stored.items() if k != "request"})


class EndpointTests(APITestCase):
    def post(self, **data):
        return self.client.post(URL, data, format="json")

    def assert_400(self, response, text):
        self.assertEqual(response.status_code, 400)
        self.assertIn(text, str(response.json()))

    def test_solve(self):
        response = self.post(**EXAMPLE["tp-burden-xexp"])
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["method"], "tres-puntos")
        self.assertEqual([f["key"] for f in data["formulas"]], [MID, AHEAD, BEHIND])
        self.assertEqual(data["formulas"][0]["expected_ratio"], 0.25)

    def test_catalog_and_examples(self):
        methods = self.client.get("/api/methods/").json()
        slugs = [m["slug"] for m in methods]
        entry = methods[slugs.index("tres-puntos")]
        self.assertEqual(entry["name"], "Fórmula de 3 puntos")
        self.assertEqual(entry["category"], "differentiation")
        self.assertEqual(slugs.index("tres-puntos"), slugs.index("diferencias-finitas") + 1)
        self.assertEqual(len(self.client.get("/api/examples/?method=tres-puntos").json()), 8)

    def test_defaults(self):
        data = self.post(function="x^2", x0=1).json()
        self.assertEqual(data["formula"], "all")
        self.assertEqual(data["tolerance"], 0.000001)
        self.assertEqual(data["max_iterations"], 25)

    def test_non_uniform_table(self):
        self.assert_400(
            self.post(mode="table", points=[[0, 0], [1, 1], [3, 9]]),
            "La fórmula de 3 puntos necesita datos igualmente espaciados: entre la fila 2 y la 3 el "
            "espaciado es 2 y el de la primera pareja es 1",
        )
        self.assert_400(
            self.post(mode="table", points=[[0, 0], [0.25, 1], [0.5, 2], [1, 3]]),
            "entre la fila 3 y la 4 el espaciado es 0.5 y el de la primera pareja es 0.25",
        )

    def test_two_points(self):
        self.assert_400(self.post(mode="table", points=[[0, 0], [1, 1]]), "entre 3 y 20 puntos")

    def test_domain_error_names_the_point(self):
        self.assert_400(self.post(function="ln(x)", x0=0.15, h0=0.1, formula="extremo_atras"),
                        "f(x) no está definida en x = -0.05 (punto x₀ − 2h)")

    def test_invalid_inputs(self):
        self.assert_400(self.post(function="x^2", x0=1, tolerance=0), "La tolerancia del error estimado debe ser mayor que 0")
        self.assert_400(self.post(function="x^2", x0=1, tolerance=-1), "La tolerancia del error estimado debe ser mayor que 0")
        self.assert_400(self.post(function="x^2", x0=1, max_iterations=5), "entre 6 y 30")
        self.assert_400(self.post(function="x^2", x0=1, max_iterations=31), "entre 6 y 30")
        self.assert_400(self.post(function="x^2", x0=1, formula="both"), "La fórmula debe ser")
