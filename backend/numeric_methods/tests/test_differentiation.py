import json
from decimal import Decimal
from pathlib import Path
from unittest import skipUnless

from django.test import SimpleTestCase
from rest_framework.test import APITestCase

from numeric_methods.examples_data import EXAMPLES
from numeric_methods.serializers.differentiation import DifferentiationSerializer
from numeric_methods.solvers.differentiation import display
from numeric_methods.solvers.differentiation.finite_differences import predicted_side, solve_finite_differences
from numeric_methods.solvers.differentiation.formulas import BACKWARD, FORWARD
from numeric_methods.tests import test_five_point

URL = "/api/solve/diferencias-finitas/"
EXAMPLE = {example["id"]: example for example in EXAMPLES["diferencias-finitas"]}


def solve(**data):
    serializer = DifferentiationSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return solve_finite_differences(serializer.validated_data).to_dict()


def example(example_id, **changes):
    return solve(**{**EXAMPLE[example_id], **changes})


# Respuestas del solver guardadas para la página de teoría (frontend).
THEORY_EXAMPLE = (Path(__file__).resolve().parents[3] / "frontend" / "src" / "methods"
                  / "differentiation" / "theory" / "finiteDifferencesExample.json")


def row(result, k, key):
    return result["iterations"][k - 1]["extra"][key]


class FormulaTests(SimpleTestCase):
    def test_square_with_exact_fractions(self):
        result = solve(function="x^2", x0=3, h0=0.1, formula="both")
        forward, backward = row(result, 1, "forward"), row(result, 1, "backward")
        self.assertAlmostEqual(forward["D"], 61 / 10, places=12)
        self.assertAlmostEqual(backward["D"], 59 / 10, places=12)
        for item in (forward, backward):
            self.assertAlmostEqual(item["real_error"], 1 / 10, places=12)
            self.assertAlmostEqual(item["bound"], 1 / 10, places=12)
            self.assertTrue(item["within_bound"])
        self.assertAlmostEqual(row(result, 2, "forward")["D"], 6.05, places=12)
        self.assertAlmostEqual(row(result, 2, "backward")["D"], 5.95, places=12)

    def test_cubic_first_row(self):
        result = example("dif-cubica")
        forward, backward = row(result, 1, "forward"), row(result, 1, "backward")
        self.assertAlmostEqual(forward["D"], 5.41, places=10)
        self.assertAlmostEqual(backward["D"], 4.61, places=10)
        self.assertAlmostEqual(forward["real_error"], 0.41, places=10)
        self.assertAlmostEqual(backward["real_error"], 0.39, places=10)
        self.assertAlmostEqual(forward["M"], 8.6, places=10)
        self.assertAlmostEqual(backward["M"], 8, places=10)
        self.assertAlmostEqual(forward["bound"], 0.43, places=10)
        self.assertAlmostEqual(backward["bound"], 0.4, places=10)


class RefinementTests(SimpleTestCase):
    def test_burden(self):
        result = example("dif-burden-ln")
        self.assertAlmostEqual(result["exact"], 1 / 1.8, places=12)
        first = {key: row(result, 1, key) for key in ("forward", "backward")}
        self.assertEqual(display.fixed(first["forward"]["D"]), "0.540672")
        self.assertEqual(display.fixed(first["backward"]["D"]), "0.571584")
        self.assertEqual(display.fixed(first["forward"]["real_error"]), "0.014883")
        self.assertEqual(display.fixed(first["backward"]["real_error"]), "0.016029")
        self.assertEqual(display.fixed(first["forward"]["bound"]), "0.015432")
        self.assertEqual(display.fixed(first["backward"]["bound"]), "0.017301")
        self.assertAlmostEqual(first["forward"]["M"], 1 / 1.8 ** 2, places=12)
        self.assertEqual(first["forward"]["x_M"], 1.8)
        self.assertAlmostEqual(first["backward"]["M"], 1 / 1.7 ** 2, places=12)
        self.assertAlmostEqual(first["backward"]["x_M"], 1.7, places=12)
        self.assertEqual([p["f_display"][:8] for p in first["forward"]["points"]], ["0.641853", "0.587786"])
        self.assertIsNone(first["forward"]["estimated_error"])
        self.assertIsNone(first["forward"]["ratio"])

        second = {key: row(result, 2, key) for key in ("forward", "backward")}
        self.assertEqual(display.fixed(second["forward"]["D"]), "0.547979")
        self.assertEqual(display.fixed(second["backward"]["D"]), "0.563418")
        self.assertEqual(display.fixed(second["forward"]["real_error"]), "0.007576")
        self.assertEqual(display.fixed(second["backward"]["real_error"]), "0.007862")

        self.assertTrue(result["converged"])
        self.assertEqual(result["iterations_used"], 9)
        self.assertEqual(display.fixed(row(result, 9, "forward")["D"]), "0.555495")
        self.assertEqual(display.fixed(row(result, 9, "backward")["D"]), "0.555616")

    def test_stop_rows(self):
        cases = {
            "dif-exp": (10, {"forward": "1.000098"}, "1"),
            "dif-seno": (10, {"backward": "0.540384"}, "0.540302"),
            "dif-cubica": (13, {"forward": "5.000098", "backward": "4.999902"}, "5"),
            "dif-lineal": (6, {"forward": "3", "backward": "3"}, "3"),
            "dif-xexp": (15, {"forward": "22.167258", "backward": "22.167078"}, "22.167168"),
        }
        for example_id, (rows, values, exact) in cases.items():
            with self.subTest(example=example_id):
                result = example(example_id)
                self.assertTrue(result["converged"])
                self.assertEqual(result["iterations_used"], rows)
                self.assertEqual(display.fixed(result["exact"]), exact)
                for key, value in values.items():
                    self.assertEqual(display.fixed(row(result, rows, key)["D"]), value)

    def test_linear_function_is_exact(self):
        result = example("dif-lineal")
        for step in result["iterations"]:
            for key in ("forward", "backward"):
                self.assertEqual(step["extra"][key]["D"], 3)
                self.assertEqual(step["extra"][key]["real_error"], 0)
                self.assertEqual(step["extra"][key]["bound"], 0)
        self.assertEqual(result["warnings"], [])

    def test_at_least_six_rows(self):
        result = example("dif-burden-ln", tolerance=1)
        self.assertTrue(result["converged"])
        self.assertEqual(result["iterations_used"], 6)

    def test_not_converged(self):
        result = example("dif-xexp", tolerance=0.000001, max_iterations=10)
        self.assertFalse(result["converged"])
        self.assertEqual(result["iterations_used"], 10)
        self.assertTrue(any("No se alcanzó la tolerancia" in w for w in result["warnings"]))

    def test_ratio_is_about_one_half(self):
        result = example("dif-burden-ln")
        for k in range(2, 7):
            for key in ("forward", "backward"):
                with self.subTest(k=k, formula=key):
                    self.assertTrue(0.45 <= row(result, k, key)["ratio"] <= 0.55)

    def test_real_error_within_bound_in_every_function_example(self):
        for example_id, data in EXAMPLE.items():
            if data["mode"] != "function":
                continue
            result = example(example_id)
            self.assertTrue(result["verification"]["all_within"], example_id)
            for step in result["iterations"]:
                for key in result["variables"]:
                    self.assertTrue(step["extra"][key]["within_bound"], (example_id, step["iteration"], key))

    def test_shown_quotient_matches_shown_values(self):
        # El cociente de los valores visibles coincide con D a 6 decimales.
        for example_id, data in EXAMPLE.items():
            if data["mode"] != "function":
                continue
            result = example(example_id)
            for step in result["iterations"]:
                h = Decimal(step["extra"]["h"]["text"]) if step["extra"]["h"]["exact"] else None
                for key in result["variables"]:
                    item = step["extra"][key]
                    if h is None:
                        continue
                    quotient = Decimal(item["numerator_display"]) / h
                    self.assertEqual(display.fixed(quotient), display.fixed(item["D"]), (example_id, step["iteration"]))


class TheoryExampleTests(SimpleTestCase):
    """El ejemplo resuelto de la teoría usa respuestas guardadas del solver:
    deben seguir siendo las que el solver devuelve hoy."""

    def test_rows_one_and_two(self):
        result = example("dif-burden-ln")
        expected = {
            1: {"forward": ("0.540672", None, "0.014883", "0.015432"),
                "backward": ("0.571584", None, "0.016029", "0.017301")},
            2: {"forward": ("0.547979", "0.007307", "0.007576", "0.007716"),
                "backward": ("0.563418", "0.008167", "0.007862", "0.008163")},
        }
        for k, formulas in expected.items():
            for key, (D, estimated, real, bound) in formulas.items():
                with self.subTest(k=k, formula=key):
                    item = row(result, k, key)
                    self.assertEqual(display.fixed(item["D"]), D)
                    if estimated is None:
                        self.assertIsNone(item["estimated_error"])
                    else:
                        self.assertEqual(display.fixed(item["estimated_error"]), estimated)
                    self.assertEqual(display.fixed(item["real_error"]), real)
                    self.assertEqual(display.fixed(item["bound"]), bound)
                    self.assertTrue(item["within_bound"])

    @skipUnless(THEORY_EXAMPLE.exists(), "sin el frontend (p. ej. en la imagen Docker del backend)")
    def test_saved_responses_match_solver(self):
        saved = json.loads(THEORY_EXAMPLE.read_text(encoding="utf-8"))
        for key, example_id in (("function", "dif-burden-ln"), ("table", "dif-carro")):
            with self.subTest(example=example_id):
                stored = saved[key]
                self.assertEqual(json.loads(json.dumps(example(example_id))),
                                 {k: v for k, v in stored.items() if k != "request"})


class DisplayTests(SimpleTestCase):
    def test_exact_step(self):
        _, shown = display.step_size(0.1, 7)
        self.assertEqual(shown, {"exact": True, "text": "0.0015625", "latex": "0.0015625", "approx": None})

    def test_long_step_uses_power_form(self):
        _, shown = display.step_size(0.1, 15)
        self.assertFalse(shown["exact"])
        self.assertEqual(shown["latex"], "0.1/2^{14}")
        self.assertEqual(shown["text"], "0.1/2^14")
        self.assertEqual(shown["approx"], "0.000006")

    def test_step_decimals(self):
        self.assertEqual(display.step_decimals(Decimal("0.001")), 9)
        self.assertEqual(display.step_decimals(Decimal("0.1")), 7)
        self.assertEqual(display.step_decimals(Decimal("2")), 6)


class VerificationTests(SimpleTestCase):
    def test_cubic_term_by_term(self):
        substitution = example("dif-cubica")["verification"]["substitution"]
        self.assertEqual([t["value"] for t in substitution["terms"]], [12, -8, 1])
        self.assertEqual([t["sign"] for t in substitution["terms"]], ["+", "-", "+"])
        self.assertEqual(substitution["value"], 5)

    def test_derivative_steps_use_ordinary_notation(self):
        steps = example("dif-cubica")["function"]["derivative"]["steps"]
        self.assertEqual(len(steps["terms"]), 3)
        self.assertTrue(steps["terms"][0]["latex"].startswith(r"\frac{d}{d x}"))
        self.assertTrue(steps["sum_latex"].startswith("f'(x) ="))
        self.assertTrue(steps["sum_latex"].endswith("3 x^{2} - 4 x + 1"))

    def test_second_derivative_term_by_term(self):
        steps = example("dif-cubica")["function"]["higher_derivatives"]["2"]["steps"]
        self.assertEqual(len(steps["terms"]), 3)
        self.assertTrue(steps["sum_latex"].startswith("f''(x) ="))
        self.assertTrue(steps["sum_latex"].endswith("= 6 x - 4"))

    def test_absolute_value_not_differentiable(self):
        result = solve(function="abs(x)", x0=0, h0=0.1)
        self.assertFalse(result["differentiable"])
        self.assertIn("f no es derivable en x₀: no se muestran el error real ni la razón entre errores.",
                      result["warnings"])
        self.assertIsNone(row(result, 1, "forward")["real_error"])
        self.assertIsNone(row(result, 1, "forward")["bound"])
        self.assertIsNone(result["verification"]["substitution"])

    def test_trigonometry_flag(self):
        self.assertTrue(example("dif-seno")["function"]["uses_trigonometry"])
        self.assertFalse(example("dif-exp")["function"]["uses_trigonometry"])


class TableModeTests(SimpleTestCase):
    def values(self, result, key):
        return [None if step["extra"][key] is None else display.fixed(step["extra"][key]["D"])
                for step in result["iterations"]]

    def test_car_with_function(self):
        result = example("dif-carro")
        self.assertTrue(result["converged"])
        self.assertEqual(self.values(result, "forward"), ["2", "6", "10", "14", "18", None])
        self.assertEqual(self.values(result, "backward"), [None, "2", "6", "10", "14", "18"])
        for step in result["iterations"]:
            self.assertEqual(step["extra"]["exact"], 4 * step["extra"]["x"])
            for key in ("forward", "backward"):
                item = step["extra"][key]
                if item:
                    self.assertEqual(item["real_error"], 2)
                    self.assertEqual(item["bound"], 2)
                    self.assertTrue(item["within_bound"])
        check = result["verification"]
        self.assertTrue(all(pair["equal"] for pair in check["secant"]))
        self.assertTrue(all(item["ok"] for item in check["data"]))
        self.assertTrue(check["all_within"])
        self.assertEqual(result["warnings"], [])

    def test_table_without_function(self):
        result = example("dif-tabla")
        expected = ["19.98163", "24.40562", "29.80909", "36.4089", "44.46993"]
        self.assertEqual(self.values(result, "forward"), expected + [None])
        self.assertEqual(self.values(result, "backward"), [None] + expected)
        check = result["verification"]
        self.assertEqual(len(check["secant"]), 5)
        self.assertTrue(all(pair["equal"] for pair in check["secant"]))
        self.assertEqual(display.fixed(check["secant"][0]["forward"]), "19.98163")
        self.assertIsNone(check["data"])
        self.assertIsNone(result["function"])
        self.assertTrue(result["uniform"])

    def test_altered_data_point(self):
        points = [list(p) for p in EXAMPLE["dif-carro"]["points"]]
        points[3][1] = 19
        result = example("dif-carro", points=points)
        oks = [item["ok"] for item in result["verification"]["data"]]
        self.assertEqual(oks, [True, True, True, False, True, True])
        self.assertTrue(any("Punto 4: el dato no coincide con la función" in w for w in result["warnings"]))

    def test_non_uniform_spacing(self):
        result = solve(mode="table", points=[[0, 0], [1, 1], [3, 9]], compare_function="x^2")
        self.assertEqual(self.values(result, "forward"), ["1", "4", None])
        self.assertEqual(self.values(result, "backward"), [None, "1", "4"])
        self.assertFalse(result["uniform"])
        self.assertIn("El espaciado de los datos no es uniforme: cada fórmula usa su propio h.",
                      result["warnings"])


class EndpointTests(APITestCase):
    def post(self, **data):
        return self.client.post(URL, data, format="json")

    def test_solve(self):
        response = self.post(**EXAMPLE["dif-burden-ln"])
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for field in ("method", "category", "converged", "iterations", "iterations_used", "warnings",
                      "mode", "formula", "formulas", "function", "exact", "differentiable",
                      "verification", "x0", "h0", "tolerance", "max_iterations", "sampling_points"):
            self.assertIn(field, data)
        self.assertEqual(data["category"], "differentiation")
        self.assertEqual([f["key"] for f in data["formulas"]], ["forward", "backward"])
        extra = data["iterations"][0]["extra"]
        self.assertEqual(extra["h"]["text"], "0.1")
        for field in ("D", "estimated_error", "real_error", "bound", "M", "x_M", "ratio", "rounding",
                      "within_bound", "points", "decimals", "numerator_display"):
            self.assertIn(field, extra["forward"])

    def test_table_mode_endpoint(self):
        response = self.post(**EXAMPLE["dif-tabla"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["mode"], "table")

    def test_catalog_and_examples(self):
        methods = self.client.get("/api/methods/").json()
        entry = next(m for m in methods if m["slug"] == "diferencias-finitas")
        self.assertEqual(entry["name"], "Diferencias progresiva y regresiva")
        self.assertEqual(entry["category"], "differentiation")
        self.assertEqual(entry["category_label"], "Diferenciación numérica")
        examples = self.client.get("/api/examples/?method=diferencias-finitas").json()
        self.assertEqual(len(examples), 8)

    def assert_400(self, response, text):
        self.assertEqual(response.status_code, 400)
        self.assertIn(text, str(response.json()))

    def test_domain_error_names_the_point(self):
        self.assert_400(self.post(function="ln(x)", x0=0.05, h0=0.1),
                        "f(x) no está definida en x = -0.05 (punto x₀ − h)")

    def test_invalid_inputs(self):
        self.assert_400(self.post(function="x^2", x0=1, h0=0), "h₀ debe ser un número mayor que 0")
        self.assert_400(self.post(function="x^2", x0=1, h0=-0.1), "h₀ debe ser un número mayor que 0")
        self.assert_400(self.post(function="x^2", x0=1, max_iterations=5), "entre 6 y 30")
        self.assert_400(self.post(function="x^2", x0=1, max_iterations=31), "entre 6 y 30")
        self.assert_400(self.post(function="x + y", x0=1), "'y' no es una variable declarada")
        self.assert_400(self.post(function="x^2"), "Falta el valor de x₀")

    def test_invalid_tables(self):
        self.assert_400(self.post(mode="table", points=[[0, 0], [2, 1], [1, 3]]), "Fila 3")
        self.assert_400(self.post(mode="table", points=[[0, 0], [0, 1]]), "estrictamente crecientes")
        self.assert_400(self.post(mode="table", points=[[0, 0]]), "entre 2 y 20 puntos")
        self.assert_400(self.post(mode="table", points=[[0, 0], [1, None]]), "Fila 2: falta el valor de y")


class ExplanationTests(SimpleTestCase):
    """Datos del paso a paso explicado (sólo diferencias progresiva y regresiva)."""

    def test_sine_backward_first_row(self):
        result = example("dif-seno")
        item = row(result, 1, "backward")
        x0, neighbor = sorted(item["points"], key=lambda p: abs(p["offset"]))
        # Punto: 1 − 0.1 = 0.9, exacto.
        self.assertEqual(result["x0_display"]["text"], "1")
        self.assertEqual(row(result, 1, "h")["text"], "0.1")
        self.assertEqual(neighbor["display"]["text"], "0.9")
        # Sustituciones sin(1) y sin(0.9), con 7 decimales (regla de coherencia).
        self.assertEqual(result["function"]["template"], r"\sin{\left(@@0@@ \right)}")
        self.assertEqual((x0["f_display"], neighbor["f_display"]), ("0.841471", "0.7833269"))
        self.assertEqual(item["decimals"], 7)
        self.assertEqual(item["numerator_display"], "0.0581441")
        self.assertEqual(display.fixed(item["D"]), "0.581441")
        # f'(1) = cos(1) y error real.
        exact = result["verification"]["substitution"]
        self.assertEqual(exact["function_text"], "cos(x)")
        self.assertEqual(display.fixed(exact["value"]), "0.540302")
        self.assertEqual(display.fixed(item["real_error"]), "0.041138")
        # M = |f''(1)| = |−sin(1)|, en x = 1.
        self.assertEqual(item["x_M"], 1.0)
        self.assertEqual(item["M_substitution"]["function_text"], "-sin(x)")
        self.assertEqual(display.fixed(item["M_substitution"]["value"]), "-0.841471")
        self.assertEqual(display.fixed(item["M"]), "0.841471")
        # Cota (0.1/2)·M = 0.05·M, sin marca R.
        self.assertEqual(item["half_h"]["text"], "0.05")
        self.assertEqual(display.fixed(item["bound"]), "0.042074")
        self.assertTrue(item["within_bound"])
        self.assertFalse(item["by_rounding"])
        self.assertFalse(item["equals_bound"])
        # Sobreestima, como predice f'' < 0 con la regresiva.
        self.assertEqual(item["side"], "over")
        self.assertEqual(item["predicted_side"], "over")
        self.assertEqual(result["curvature"]["sign"], -1)

    def test_sine_backward_second_row(self):
        result = example("dif-seno")
        item = row(result, 2, "backward")
        self.assertEqual(row(result, 2, "h")["text"], "0.05")
        neighbor = next(p for p in item["points"] if p["offset"] == -1)
        self.assertEqual(neighbor["display"]["text"], "0.95")
        self.assertEqual(item["decimals"], 8)
        self.assertEqual(display.fixed(item["D"]), "0.56111")
        self.assertEqual(display.fixed(item["estimated_error"]), "0.020331")
        self.assertFalse(item["below_tolerance"])
        self.assertEqual(display.fixed(item["real_error"]), "0.020807")
        self.assertEqual(display.fixed(item["bound"]), "0.021037")
        self.assertEqual(display.fixed(item["ratio"], 4), "0.5058")
        self.assertEqual(result["min_rows"], 6)

    def test_ln_forward_underestimates(self):
        result = example("dif-burden-ln")
        forward = row(result, 1, "forward")
        self.assertEqual(forward["numerator_display"], "0.0540672")
        # ln x es cóncava: la progresiva queda por debajo y la regresiva por encima.
        self.assertEqual((forward["side"], forward["predicted_side"]), ("under", "under"))
        backward = row(result, 1, "backward")
        self.assertEqual((backward["side"], backward["predicted_side"]), ("over", "over"))
        self.assertEqual(result["curvature"]["sign"], -1)

    def test_predicted_side_rule(self):
        self.assertEqual(predicted_side(FORWARD, 1), "over")
        self.assertEqual(predicted_side(FORWARD, -1), "under")
        self.assertEqual(predicted_side(BACKWARD, 1), "under")
        self.assertEqual(predicted_side(BACKWARD, -1), "over")
        self.assertIsNone(predicted_side(FORWARD, 0))

    def test_derivative_breakdown(self):
        power, x_rule, constant = "regla de la potencia", "la derivada de x respecto a x es 1", "derivada de una constante"
        cases = {
            "dif-seno": (["derivada de la función seno"], "cos(x)", ["derivada de la función coseno"], "-sin(x)"),
            "dif-burden-ln": (["derivada de la función logaritmo natural"], "1/x", [power], "-1/x^2"),
            "dif-cubica": ([power, power, x_rule], "3*x^2 - 4*x + 1", [power, x_rule, constant], "6*x - 4"),
        }
        for example_id, (rules1, text1, rules2, text2) in cases.items():
            with self.subTest(example=example_id):
                fn = example(example_id)["function"]
                self.assertEqual([t["rule"] for t in fn["derivative"]["steps"]["terms"]], rules1)
                self.assertEqual(fn["derivative"]["text"], text1)
                second = fn["higher_derivatives"]["2"]
                self.assertEqual([t["rule"] for t in second["steps"]["terms"]], rules2)
                self.assertEqual(second["text"], text2)

    def test_linear_error_equals_bound_without_R(self):
        result = example("dif-lineal")
        for k in range(1, len(result["iterations"]) + 1):
            for key in ("forward", "backward"):
                item = row(result, k, key)
                self.assertEqual((item["real_error"], item["bound"]), (0.0, 0.0))
                self.assertTrue(item["within_bound"])
                self.assertTrue(item["equals_bound"])
                self.assertFalse(item["by_rounding"])
                self.assertEqual(item["side"], "equal")
        final = result["verification"]["final"]["forward"]
        self.assertTrue(final["equals_bound"])
        self.assertEqual(final["matching_decimals"], 6)

    def test_conclusion_decimals(self):
        final = example("dif-seno")["verification"]["final"]["backward"]
        self.assertEqual(final["matching_decimals"], 3)

    def test_five_point_unchanged(self):
        # Los datos del paso a paso explicado no llegan a 5 puntos (3 puntos
        # tiene los suyos: ver test_three_point.ExplanationTests).
        for module in (test_five_point,):
            for example_id in module.EXAMPLE:
                with self.subTest(example=example_id):
                    result = module.example(example_id)
                    self.assertNotIn("min_rows", result)
                    self.assertNotIn("curvature", result)
                    for step in result["iterations"]:
                        for item in step["extra"].values():
                            if isinstance(item, dict) and "points" in item:
                                for key in ("side", "half_h", "equals_bound", "below_tolerance"):
                                    self.assertNotIn(key, item)
