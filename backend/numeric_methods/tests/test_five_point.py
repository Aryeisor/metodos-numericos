import json
from decimal import Decimal
from pathlib import Path

from django.test import SimpleTestCase
from rest_framework.test import APITestCase

from numeric_methods.examples_data import EXAMPLES
from numeric_methods.serializers.differentiation import FivePointSerializer
from numeric_methods.solvers.differentiation.display import fixed
from numeric_methods.solvers.differentiation.five_point import solve_five_point
from numeric_methods.solvers.differentiation.formulas import FORMULAS
from numeric_methods.solvers.differentiation.three_point import predicted_side
from numeric_methods.tests import test_differentiation, test_three_point

URL = "/api/solve/cinco-puntos/"
EXAMPLE = {example["id"]: example for example in EXAMPLES["cinco-puntos"]}
MID, AHEAD, BEHIND, MID3 = "punto_medio_5", "extremo_adelante_5", "extremo_atras_5", "punto_medio"
FIVE = (MID, AHEAD, BEHIND)

# Respuestas del solver guardadas para la página de teoría (frontend).
THEORY_EXAMPLE = (Path(__file__).resolve().parents[3] / "frontend" / "src" / "methods"
                  / "differentiation" / "theory" / "fivePointExample.json")


def solve(**data):
    serializer = FivePointSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return solve_five_point(serializer.validated_data).to_dict()


def example(example_id, **changes):
    return solve(**{**EXAMPLE[example_id], **changes})


def row(result, k, key):
    return result["iterations"][k - 1]["extra"][key]


class ExactFractionTests(SimpleTestCase):
    def test_fifth_power(self):
        result = solve(function="x^5", x0=1, h0=0.5)
        self.assertAlmostEqual(row(result, 1, MID)["D"], 19 / 4, places=12)
        self.assertAlmostEqual(row(result, 1, AHEAD)["D"], 7 / 2, places=12)
        self.assertAlmostEqual(row(result, 1, BEHIND)["D"], 7 / 2, places=12)

    def test_quartic_is_exact(self):
        result = solve(function="x^4 - 2x^3 + x", x0=1, h0=0.5)
        for key in FIVE:
            self.assertAlmostEqual(row(result, 1, key)["D"], -1, places=12)
        self.assertAlmostEqual(result["comparison"][0]["midpoint_3"]["D"], -1 / 2, places=12)


class FunctionModeTests(SimpleTestCase):
    def test_burden_first_rows_and_stop(self):
        result = example("cp-burden-xexp")
        self.assertEqual(fixed(result["exact"]), "22.167168")
        first = {
            MID: ("22.166996", "0.000173", "0.000217"),
            AHEAD: ("22.165915", "0.001254", "0.001631"),
            BEHIND: ("22.166312", "0.000857", "0.001034"),
        }
        for key, (D, real, bound) in first.items():
            item = row(result, 1, key)
            self.assertEqual(fixed(item["D"]), D)
            self.assertEqual(fixed(item["real_error"]), real)
            self.assertEqual(fixed(item["bound"]), bound)
        for key, D in {MID: "22.167158", AHEAD: "22.167097", BEHIND: "22.167109"}.items():
            self.assertEqual(fixed(row(result, 2, key)["D"]), D)
        self.assertTrue(result["converged"])
        self.assertEqual(result["iterations_used"], 6)

    def test_comparison(self):
        result = example("cp-burden-xexp")
        self.assertEqual(len(result["comparison"]), 2)
        first = result["comparison"][0]
        self.assertEqual(fixed(first["midpoint_3"]["D"]), "22.228787")
        self.assertEqual(fixed(first["midpoint_3"]["real_error"]), "0.061619")
        self.assertEqual(fixed(first["forward"]["D"]), "23.708446")
        self.assertEqual(fixed(first["backward"]["D"]), "20.749128")
        self.assertIn("la fórmula de 3 puntos (punto medio) daría 22.228787 (error 0.061619), la diferencia "
                      "progresiva 23.708446 (error 1.541278) y la regresiva 20.749128 (error 1.418041).",
                      first["text"])
        self.assertIn("punto medio 22.166996 (error 0.000173: 357 veces menor que el de la fórmula de 3 puntos",
                      first["text"])
        self.assertEqual(result["comparison"][1]["k"], 6)

    def test_richardson_identity(self):
        (identity,) = example("cp-burden-xexp")["verification"]["identities"]
        self.assertEqual(identity["key"], MID)
        self.assertTrue(identity["ok"])
        self.assertEqual((identity["base_display"], identity["double_display"], identity["value_display"]),
                         ("22.228787", "22.414161", "22.166996"))
        self.assertFalse(identity["rounding_difference"])

    def test_endpoints_have_no_identity(self):
        self.assertEqual(example("cp-gauss")["verification"]["identities"], [])

    def test_step_shows_each_product(self):
        item = row(example("cp-burden-xexp"), 1, MID)
        # Con 6 decimales, 26.600399/1.2 = 22.166999 ≠ D: la regla de d agrega uno.
        self.assertEqual(item["decimals"], 7)
        self.assertEqual(item["products_display"], ["10.8893654", "-101.6255952", "137.1916544", "-19.8550297"])
        self.assertEqual(item["numerator_display"], "26.6003949")
        self.assertEqual(item["denominator_display"], "1.2")
        self.assertEqual(fixed(item["D"]), "22.166996")
        self.assertEqual([p["role"] for p in row(example("cp-burden-xexp"), 1, BEHIND)["points"]][-1], "x_0 - 4h")

    def test_stop_rows(self):
        for example_id, rows in (("cp-ln", 6), ("cp-seno", 6), ("cp-cuartica", 6),
                                 ("cp-quintica", 8), ("cp-gauss", 6)):
            with self.subTest(example=example_id):
                result = example(example_id)
                self.assertTrue(result["converged"])
                self.assertEqual(result["iterations_used"], rows)

    def test_first_rows_of_other_examples(self):
        cases = {
            "cp-ln": {MID: ("0.555551", "0.000004"), AHEAD: ("0.555539", "0.000017"), BEHIND: ("0.555514", "0.000042")},
            "cp-seno": {MID: ("0.540301", "0.000002")},
            "cp-gauss": {BEHIND: ("-0.778201", "0.0006")},
        }
        for example_id, formulas in cases.items():
            result = example(example_id)
            for key, (D, real) in formulas.items():
                with self.subTest(example=example_id, formula=key):
                    self.assertEqual(fixed(row(result, 1, key)["D"]), D)
                    self.assertEqual(fixed(row(result, 1, key)["real_error"]), real)
        self.assertEqual(fixed(row(example("cp-seno"), 1, MID)["bound"]), "0.000002")
        gauss = example("cp-gauss")
        self.assertEqual(fixed(row(gauss, 1, BEHIND)["bound"]), "0.000654")
        self.assertEqual(fixed(row(gauss, 2, BEHIND)["D"]), "-0.77876")

    def test_fifth_power_error_equals_bound(self):
        result = example("cp-quintica")
        expected = {1: {MID: (4.75, 0.25), AHEAD: (3.5, 1.5), BEHIND: (3.5, 1.5)},
                    2: {MID: (4.984375, 0.015625), AHEAD: (4.90625, 0.09375), BEHIND: (4.90625, 0.09375)}}
        for k, formulas in expected.items():
            for key, (D, error) in formulas.items():
                with self.subTest(k=k, formula=key):
                    item = row(result, k, key)
                    self.assertAlmostEqual(item["D"], D, places=12)
                    self.assertAlmostEqual(item["real_error"], error, places=12)
                    self.assertAlmostEqual(item["bound"], error, places=12)

    def test_quartic_error_and_bound_zero(self):
        for step in example("cp-cuartica")["iterations"]:
            for key in FIVE:
                self.assertAlmostEqual(step["extra"][key]["D"], -1, places=12)
                self.assertAlmostEqual(step["extra"][key]["real_error"], 0, places=12)
                self.assertEqual(step["extra"][key]["bound"], 0)

    def test_ratio_is_about_one_sixteenth(self):
        result = example("cp-burden-xexp")
        self.assertEqual(result["formulas"][0]["expected_ratio"], 0.0625)
        for k in range(2, 5):
            for key in (MID, AHEAD):
                with self.subTest(k=k, formula=key):
                    self.assertTrue(0.055 <= row(result, k, key)["ratio"] <= 0.065)

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

    def test_fifth_derivative_term_by_term(self):
        higher = example("cp-burden-xexp")["function"]["higher_derivatives"]
        self.assertEqual(sorted(higher), ["2", "3", "4", "5"])
        self.assertTrue(higher["5"]["steps"]["sum_latex"].endswith("= x e^{x} + 5 e^{x}"))


class TableModeTests(SimpleTestCase):
    def values(self, result, key):
        return [None if step["extra"][key] is None else fixed(step["extra"][key]["D"])
                for step in result["iterations"]]

    def recommended(self, result):
        return [(fixed(s["extra"]["recommended"]["D"]), s["extra"]["recommended"]["key"])
                for s in result["iterations"]]

    def test_burden_table(self):
        result = example("cp-tabla-burden")
        self.assertEqual(result["variables"], [MID, AHEAD, BEHIND, MID3])
        # 22.1659225, 28.8798275 y 32.9135975 son empates exactos a 7 decimales:
        # en binario el sexto decimal queda como 2, 8 y 8.
        self.assertEqual(self.values(result, MID), [
            None, None, "16.93887", "19.388942", "22.166999", "25.314936", "28.879828", None, None])
        self.assertEqual(self.values(result, AHEAD), [
            "12.877113", "14.778752", "16.938014", "19.387974", "22.165922", None, None, None, None])
        self.assertEqual(self.values(result, BEHIND), [
            None, None, None, None, "22.166307", "25.314172", "28.878964", "32.913598", "37.477432"])
        self.assertEqual(self.values(result, MID3), [
            None, "14.822565", "16.98744", "19.443735", "22.22879", "25.38459", "28.958315", "33.002965", None])
        self.assertEqual([key for _, key in self.recommended(result)],
                         [AHEAD, AHEAD, MID, MID, MID, MID, MID, BEHIND, BEHIND])
        self.assertEqual([fixed(s["extra"]["exact"]) for s in result["iterations"]], [
            "12.877884", "14.779658", "16.939013", "19.389094", "22.167168", "25.315127", "28.880043",
            "32.914802", "37.4788"])
        x17 = result["iterations"][1]["extra"]
        self.assertEqual(fixed(x17[AHEAD]["real_error"]), "0.000906")
        self.assertEqual(fixed(x17[MID3]["real_error"]), "0.042907")
        check = result["verification"]
        self.assertTrue(all(item["ok"] and item["difference"] < 0.0000005 for item in check["data"]))
        self.assertTrue(check["all_within"])

    def test_identity_per_point_and_rounding_case(self):
        identities = example("cp-tabla-burden")["verification"]["identities"]
        self.assertEqual([len(point["items"]) for point in identities], [0, 0, 1, 1, 1, 1, 1, 0, 0])
        items = [point["items"][0] for point in identities if point["items"]]
        self.assertTrue(all(item["ok"] for item in items))
        self.assertEqual(items[2]["value_display"], "22.166999")
        self.assertFalse(items[2]["rounding_difference"])
        x22 = identities[6]["items"][0]
        # (4(28.958315) − 29.193778)/3 = 28.879827, con los valores mostrados.
        self.assertEqual((x22["base_display"], x22["double_display"], x22["value_display"]),
                         ("28.958315", "29.193778", "28.879827"))
        self.assertEqual(x22["D_display"], "28.879828")
        self.assertTrue(x22["rounding_difference"])
        self.assertTrue(x22["ok"])

    def test_fourth_powers_without_function(self):
        result = example("cp-tabla-cuartas")
        self.assertEqual(self.values(result, MID), [None, None, "32", "108", "256", None, None])
        self.assertEqual(self.values(result, AHEAD), ["0", "4", "32", None, None, None, None])
        self.assertEqual(self.values(result, BEHIND), [None, None, None, None, "256", "500", "864"])
        self.assertEqual(self.values(result, MID3), [None, "8", "40", "120", "272", "520", None])
        self.assertEqual([v for v, _ in self.recommended(result)], ["0", "4", "32", "108", "256", "500", "864"])
        self.assertIsNone(result["function"])
        self.assertIsNone(result["verification"]["data"])
        self.assertTrue(all(i["ok"] for point in result["verification"]["identities"] for i in point["items"]))

    def test_fourth_powers_with_function(self):
        result = example("cp-tabla-cuartas", compare_function="x^4")
        for step in result["iterations"]:
            x = step["extra"]["x"]
            for key in FIVE:
                if step["extra"][key]:
                    self.assertAlmostEqual(step["extra"][key]["real_error"], 0, places=9)
            if step["extra"][MID3]:
                self.assertAlmostEqual(step["extra"][MID3]["real_error"], 4 * x, places=9)
        self.assertTrue(result["verification"]["all_within"])

    def test_single_formula_keeps_reference_and_recommended(self):
        result = example("cp-tabla-cuartas", formula="extremo_atras_5")
        self.assertEqual(result["variables"], [BEHIND, MID3])
        self.assertEqual([v for v, _ in self.recommended(result)], ["0", "4", "32", "108", "256", "500", "864"])

    def test_five_points(self):
        points = [[x, x ** 4] for x in range(5)]
        result = solve(mode="table", points=points)
        self.assertEqual(self.values(result, MID), [None, None, "32", None, None])
        self.assertEqual(self.recommended(result), [
            ("0", AHEAD), ("8", MID3), ("32", MID), ("120", MID3), ("256", BEHIND)])

    def test_altered_data_point(self):
        points = [list(p) for p in EXAMPLE["cp-tabla-burden"]["points"]]
        points[4][1] = 14.8
        result = example("cp-tabla-burden", points=points)
        self.assertEqual([item["ok"] for item in result["verification"]["data"]],
                         [True] * 4 + [False] + [True] * 4)
        self.assertTrue(any("Punto 5: el dato no coincide con la función" in w for w in result["warnings"]))


class TheoryExampleTests(SimpleTestCase):
    """La página de teoría usa respuestas guardadas del solver: deben ser las
    que el solver devuelve hoy y mostrar los valores del libro."""

    def setUp(self):
        self.saved = json.loads(THEORY_EXAMPLE.read_text(encoding="utf-8"))

    def test_rows_one_and_two_and_identity(self):
        result = self.saved["function"]
        expected = {
            1: {MID: ("22.166996", "0.000173", "0.000217"),
                AHEAD: ("22.165915", "0.001254", "0.001631"),
                BEHIND: ("22.166312", "0.000857", "0.001034")},
            2: {MID: ("22.167158", None, None),
                AHEAD: ("22.167097", None, None),
                BEHIND: ("22.167109", None, None)},
        }
        for k, formulas in expected.items():
            for key, (D, real, bound) in formulas.items():
                with self.subTest(k=k, formula=key):
                    item = row(result, k, key)
                    self.assertEqual(fixed(item["D"]), D)
                    if real:
                        self.assertEqual(fixed(item["real_error"]), real)
                        self.assertEqual(fixed(item["bound"]), bound)
        [identity] = result["verification"]["identities"]
        self.assertTrue(identity["ok"])
        self.assertEqual((identity["base_display"], identity["double_display"], identity["value_display"]),
                         ("22.228787", "22.414161", "22.166996"))
        self.assertEqual(result["iterations_used"], 6)

    def test_saved_responses_match_solver(self):
        for key, example_id in (("function", "cp-burden-xexp"), ("table", "cp-tabla-burden")):
            with self.subTest(example=example_id):
                stored = self.saved[key]
                # La gráfica (chart) no se guarda en las respuestas de la página de teoría.
                result = json.loads(json.dumps(example(example_id)))
                result.pop("chart")
                self.assertEqual(result,
                                 {k: v for k, v in stored.items() if k != "request"})


class EndpointTests(APITestCase):
    def post(self, **data):
        return self.client.post(URL, data, format="json")

    def assert_400(self, response, text):
        self.assertEqual(response.status_code, 400)
        self.assertIn(text, str(response.json()))

    def test_solve(self):
        response = self.post(**EXAMPLE["cp-burden-xexp"])
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["method"], "cinco-puntos")
        self.assertEqual([f["key"] for f in data["formulas"]], list(FIVE))

    def test_catalog_and_examples(self):
        methods = self.client.get("/api/methods/").json()
        slugs = [m["slug"] for m in methods]
        entry = methods[slugs.index("cinco-puntos")]
        self.assertEqual(entry["name"], "Fórmula de 5 puntos")
        self.assertEqual(entry["category"], "differentiation")
        self.assertEqual(slugs.index("cinco-puntos"), slugs.index("tres-puntos") + 1)
        self.assertEqual(len(self.client.get("/api/examples/?method=cinco-puntos").json()), 8)

    def test_defaults(self):
        data = self.post(function="x^2", x0=1).json()
        self.assertEqual(data["formula"], "all")
        self.assertEqual(data["tolerance"], 0.000001)
        self.assertEqual(data["max_iterations"], 25)

    def test_non_uniform_table(self):
        self.assert_400(
            self.post(mode="table", points=[[0, 0], [1, 1], [2, 2], [3, 3], [5, 5]]),
            "La fórmula de 5 puntos necesita datos igualmente espaciados: entre la fila 4 y la 5 el "
            "espaciado es 2 y el de la primera pareja es 1",
        )

    def test_four_points(self):
        self.assert_400(self.post(mode="table", points=[[0, 0], [1, 1], [2, 2], [3, 3]]), "entre 5 y 20 puntos")

    def test_domain_error_names_the_point(self):
        self.assert_400(self.post(function="ln(x)", x0=0.35, h0=0.1, formula="extremo_atras_5"),
                        "f(x) no está definida en x = -0.05 (punto x₀ − 4h)")

    def test_invalid_inputs(self):
        self.assert_400(self.post(function="x^2", x0=1, tolerance=0), "La tolerancia del error estimado debe ser mayor que 0")
        self.assert_400(self.post(function="x^2", x0=1, tolerance=-1), "La tolerancia del error estimado debe ser mayor que 0")
        self.assert_400(self.post(function="x^2", x0=1, max_iterations=5), "entre 6 y 30")
        self.assert_400(self.post(function="x^2", x0=1, max_iterations=31), "entre 6 y 30")
        self.assert_400(self.post(function="x^2", x0=1, formula="punto_medio"), "La fórmula debe ser")


class ExplanationTests(SimpleTestCase):
    """Datos del paso a paso explicado de la fórmula de 5 puntos (ejemplo 1)."""

    def setUp(self):
        self.result = example("cp-burden-xexp")

    def points(self, item):
        return [(p["role"], p["display"]["text"], p["f_display"]) for p in item["points"]]

    def assert_bound(self, item, x_M, M, bound):
        self.assertEqual(item["h_fourth"]["text"], "0.0001")
        self.assertEqual(item["M_substitution"]["function_text"], "x*exp(x) + 5*exp(x)")
        self.assertEqual(item["M_substitution"]["x_display"]["text"], x_M)
        self.assertEqual((fixed(item["M_substitution"]["value"]), fixed(item["M"])), (M, M))
        self.assertEqual(fixed(item["bound"]), bound)
        self.assertEqual((item["within_bound"], item["equals_bound"], item["by_rounding"]), (True, False, False))

    def test_row_one_midpoint(self):
        item = row(self.result, 1, MID)
        self.assertEqual(self.points(item), [("x_0 - 2h", "1.8", "10.8893654"), ("x_0 - h", "1.9", "12.7031994"),
                                             ("x_0 + h", "2.1", "17.1489568"), ("x_0 + 2h", "2.2", "19.8550297")])
        self.assertEqual(item["products_display"], ["10.8893654", "-101.6255952", "137.1916544", "-19.8550297"])
        self.assertEqual((item["numerator_display"], item["denominator_display"]), ("26.6003949", "1.2"))
        self.assertEqual((fixed(item["D"]), fixed(item["real_error"])), ("22.166996", "0.000173"))
        self.assertEqual([p["text"] for p in item["interval_display"]], ["1.8", "2.2"])
        self.assert_bound(item, "2.2", "64.980097", "0.000217")

    def test_row_one_endpoints(self):
        ahead = row(self.result, 1, AHEAD)
        self.assertEqual(self.points(ahead), [
            ("x_0", "2", "14.7781122"), ("x_0 + h", "2.1", "17.14895682"), ("x_0 + 2h", "2.2", "19.8550297"),
            ("x_0 + 3h", "2.3", "22.94061965"), ("x_0 + 4h", "2.4", "26.45562331")])
        self.assertEqual(ahead["products_display"],
                         ["-369.452805", "823.14992736", "-714.7810692", "367.0499144", "-79.36686993"])
        self.assertEqual((fixed(ahead["D"]), fixed(ahead["real_error"])), ("22.165915", "0.001254"))
        self.assertEqual([p["text"] for p in ahead["interval_display"]], ["2", "2.4"])
        self.assert_bound(ahead, "2.4", "81.571505", "0.001631")

        behind = row(self.result, 1, BEHIND)
        self.assertEqual(self.points(behind), [
            ("x_0", "2", "14.7781122"), ("x_0 - h", "1.9", "12.7031994"), ("x_0 - 2h", "1.8", "10.8893654"),
            ("x_0 - 3h", "1.7", "9.3057106"), ("x_0 - 4h", "1.6", "7.9248519")])
        self.assertEqual(behind["products_display"],
                         ["369.452805", "-609.7535712", "392.0171544", "-148.8913696", "23.7745557"])
        self.assertEqual(behind["numerator_display"], "26.5995743")
        self.assertEqual((fixed(behind["D"]), fixed(behind["real_error"])), ("22.166312", "0.000857"))
        self.assertEqual([p["text"] for p in behind["interval_display"]], ["1.6", "2"])
        self.assert_bound(behind, "2", "51.723393", "0.001034")

    def test_sign_all_underestimate(self):
        # f⁽⁵⁾ > 0 y D − f' ≈ −(h⁴/30 o h⁴/5)·f⁽⁵⁾: las tres quedan por debajo.
        self.assertEqual(self.result["fifth_derivative"]["sign"], 1)
        self.assertNotIn("third_derivative", self.result)
        D = {key: row(self.result, 1, key)["D"] for key in FIVE}
        self.assertTrue(D[AHEAD] < D[BEHIND] < D[MID] < self.result["exact"])
        for key in FIVE:
            item = row(self.result, 1, key)
            self.assertEqual((item["side"], item["predicted_side"]), ("under", "under"))
        self.assertEqual(predicted_side(FORMULAS[MID], -1), "over")
        self.assertIsNone(predicted_side(FORMULAS[AHEAD], 0))

    def test_forward_endpoint_decimal_coherence(self):
        ahead = row(self.result, 1, AHEAD)
        # Con 7 decimales: 26.5990959/1.2 = 22.165913 ≠ 22.165915; el paso usa 8.
        self.assertEqual(fixed(Decimal("26.5990959") / Decimal("1.2")), "22.165913")
        self.assertEqual(ahead["decimals"], 8)
        self.assertEqual(ahead["numerator_display"], "26.59909763")
        quotient = Decimal(ahead["numerator_display"]) / Decimal(ahead["denominator_display"])
        self.assertEqual(fixed(quotient), fixed(ahead["D"]))

    def test_row_two_midpoint(self):
        item = row(self.result, 2, MID)
        self.assertEqual(row(self.result, 2, "h")["text"], "0.05")
        self.assertEqual(self.points(item), [("x_0 - 2h", "1.9", "12.7031994"), ("x_0 - h", "1.95", "13.7059408"),
                                             ("x_0 + h", "2.05", "15.9241973"), ("x_0 + 2h", "2.1", "17.1489568")])
        self.assertEqual(item["denominator_display"], "0.6")
        self.assertEqual(fixed(item["D"]), "22.167158")
        self.assertEqual(fixed(item["estimated_error"]), "0.000162")
        self.assertFalse(item["below_tolerance"])
        self.assertEqual(fixed(item["real_error"]), "0.000011")
        self.assertEqual(item["h_fourth"]["text"], "0.00000625")
        self.assertEqual(fixed(item["ratio"], 4), "0.0624")
        self.assertEqual(self.result["min_rows"], 6)

    def test_richardson_identity_substitution(self):
        (identity,) = self.result["verification"]["identities"]
        base, double = Decimal(identity["base_display"]), Decimal(identity["double_display"])
        self.assertEqual((identity["base_display"], identity["double_display"]), ("22.228787", "22.414161"))
        self.assertEqual(fixed((4 * base - double) / 3), identity["value_display"])
        self.assertEqual(identity["value_display"], identity["D_display"])
        self.assertEqual(identity["D_display"], fixed(row(self.result, 1, MID)["D"]))

    def test_derivative_breakdown(self):
        product, exponential = "regla del producto: (u·v)′ = u′·v + u·v′", "derivada de la función exponencial"
        fn = self.result["function"]
        self.assertEqual([fn["higher_derivatives"][n]["text"] for n in ("2", "3", "4", "5")],
                         [f"x*exp(x) + {k}*exp(x)" for k in range(2, 6)])
        for n in ("2", "3", "4", "5"):
            self.assertEqual([t["rule"] for t in fn["higher_derivatives"][n]["steps"]["terms"]], [product, exponential])
        # Cada derivada es la anterior más eˣ.
        self.assertEqual(self.result["derivative_pattern"], {"latex": "e^{x}"})

        quintic = example("cp-quintica")
        fn = quintic["function"]
        self.assertEqual([fn["derivative"]["text"]] + [fn["higher_derivatives"][n]["text"] for n in ("2", "3", "4", "5")],
                         ["5*x^4", "20*x^3", "60*x^2", "120*x", "120"])
        self.assertEqual([t["rule"] for t in fn["higher_derivatives"]["5"]["steps"]["terms"]],
                         ["la derivada de x respecto a x es 1"])
        self.assertIsNone(quintic["derivative_pattern"])

    def test_quartic_error_and_bound_zero_equal_without_R(self):
        result = example("cp-cuartica")
        for step in result["iterations"]:
            for key in FIVE:
                item = step["extra"][key]
                self.assertEqual(item["bound"], 0)
                self.assertTrue(item["within_bound"])
                self.assertTrue(item["equals_bound"])
                self.assertFalse(item["by_rounding"])
        self.assertTrue(result["verification"]["final"][MID]["equals_bound"])

    def test_quintic_error_equals_bound_without_R(self):
        result = example("cp-quintica")
        for key, error in ((MID, 0.25), (AHEAD, 1.5), (BEHIND, 1.5)):
            item = row(result, 1, key)
            self.assertEqual((item["real_error"], item["bound"]), (error, error))
            self.assertTrue(item["equals_bound"])
        for step in result["iterations"]:
            for key in FIVE:
                self.assertFalse(step["extra"][key]["by_rounding"])

    def test_table_mode_explanation(self):
        extra = example("cp-tabla-burden")["iterations"][1]["extra"]
        self.assertEqual((extra["fifth_derivative"]["sign"], extra["third_derivative"]["sign"]), (1, 1))
        self.assertEqual(extra[AHEAD]["h_fourth"]["text"], "0.0001")
        # El punto medio de 3 puntos de referencia lleva sus datos de 3 puntos.
        self.assertEqual(extra[MID3]["h_squared"]["text"], "0.01")
        self.assertEqual((extra[AHEAD]["side"], extra[MID3]["side"]), ("under", "over"))
        self.assertEqual(extra["recommended"]["key"], AHEAD)
        self.assertEqual((fixed(extra[AHEAD]["real_error"]), fixed(extra[MID3]["real_error"])), ("0.000906", "0.042907"))
        quartics = example("cp-tabla-cuartas")["iterations"][2]["extra"]
        self.assertIsNone(quartics["fifth_derivative"])
        self.assertIsNone(quartics[MID]["side"])

    def test_three_point_and_differences_unchanged(self):
        # Regresión: los datos nuevos de 5 puntos no llegan a 3 puntos ni a diferencias.
        three = test_three_point.example("tp-burden-xexp")
        self.assertNotIn("fifth_derivative", three)
        self.assertNotIn("derivative_pattern", three)
        self.assertNotIn("h_fourth", three["iterations"][0]["extra"][MID3])
        self.assertEqual(three["iterations"][0]["extra"][MID3]["h_squared"]["text"], "0.01")
        differences = test_differentiation.example("dif-burden-ln")
        self.assertNotIn("fifth_derivative", differences)
        for item in differences["iterations"][0]["extra"].values():
            if isinstance(item, dict) and "points" in item:
                self.assertNotIn("h_fourth", item)
                self.assertNotIn("h_squared", item)
