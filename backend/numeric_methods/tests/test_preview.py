import math

import sympy as sp
from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from numeric_methods.examples_data import EXAMPLES
from numeric_methods.expressions.parser import (
    MAX_EXPONENT,
    MAX_LENGTH,
    MAX_NESTING,
    make_symbols,
    parse_expression,
)
from numeric_methods.expressions.to_latex import expression_to_latex
from numeric_methods.expressions.to_text import expression_to_text
from numeric_methods.serializers.expressions import MAX_PREVIEW_VARIABLES
from numeric_methods.solvers.nonlinear.fixed_point import solve_fixed_point

URL = "/api/expressions/preview"
XY = ["x", "y"]


class PreviewEndpointTests(APITestCase):
    def _post(self, equation, variables=XY, url=URL):
        return self.client.post(url, {"equation": equation, "variables": variables}, format="json")

    def _latex(self, equation, variables=XY):
        response = self._post(equation, variables)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(set(response.json()), {"latex"})
        return response.json()["latex"]

    def _error(self, equation, variables=XY, field="equation"):
        response = self._post(equation, variables)
        self.assertEqual(response.status_code, 400, response.content)
        data = response.json()
        self.assertIn(field, data)
        self.assertIsInstance(data[field], list)
        self.assertTrue(all(isinstance(m, str) for m in data[field]))
        return data[field][0]

    # --- parseo válido -------------------------------------------------

    def test_equation_with_both_sides(self):
        self.assertEqual(self._latex("3*x - y**2 - 1 = 0"), "3 x - y^{2} - 1 = 0")

    def test_other_variables_are_valid_inside_the_equation(self):
        self.assertEqual(self._latex("x = y^2/3 + 1/3"), r"x = \frac{y^{2}}{3} + \frac{1}{3}")

    def test_plain_expression(self):
        self.assertEqual(self._latex("sqrt(x) + abs(y)"), r"\sqrt{x} + \left|{y}\right|")

    def test_function_header_form(self):
        self.assertEqual(self._latex("f1(x, y) = x^2 + x*y - 10"), "f_{1}(x, y) = x^{2} + x y - 10")

    def test_logarithms(self):
        self.assertEqual(self._latex("log(x) + ln(y)"), r"\log_{10}{\left(x \right)} + \ln{\left(y \right)}")

    def test_constants(self):
        self.assertEqual(self._latex("x = pi*e"), r"x = \pi e")

    def test_only_parses_does_not_solve(self):
        # Ambigua para Punto Fijo (dos despejes de x), pero es una ecuación válida.
        self.assertEqual(self._latex("x^2 - y = 0"), "x^{2} - y = 0")

    def test_works_with_and_without_trailing_slash(self):
        self.assertEqual(reverse("expression-preview"), "/api/expressions/preview")
        for url in (URL, URL + "/"):
            with self.subTest(url=url):
                self.assertEqual(self._post("x + y", url=url).status_code, 200)

    def test_only_post_is_allowed(self):
        self.assertEqual(self.client.get(URL).status_code, 405)

    # --- parseo inválido ----------------------------------------------

    def test_malformed_expression(self):
        self.assertEqual(self._error("3*x +* y"), "La expresión no está bien formada.")

    def test_undeclared_variable(self):
        self.assertIn("'z' no es una variable declarada", self._error("x + z = 0"))

    def test_empty_equation(self):
        self.assertEqual(self._error("   "), "La expresión está vacía.")

    def test_two_equal_signs(self):
        self.assertIn("único '='", self._error("x = y = 1"))

    def test_missing_fields(self):
        response = self.client.post(URL, {}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json()), {"equation", "variables"})

    def test_invalid_variables(self):
        for variables, fragment in ((["x", "x"], "repetida"), (["x", "sin"], "reservado"),
                                    (["x", "2y"], "no es un nombre"), ([], "al menos una")):
            with self.subTest(variables=variables):
                self.assertIn(fragment, self._error("x = 1", variables, field="variables"))

    def test_too_many_variables(self):
        names = [f"x{i}" for i in range(MAX_PREVIEW_VARIABLES + 1)]
        self._error("x1 = 0", names, field="variables")

    # --- mismos límites de seguridad que el parser --------------------

    def test_code_injection_is_rejected(self):
        for attack in ("__import__('os').getcwd()", "x.__class__", "lambda: 1", "[x]", "'x'"):
            with self.subTest(attack=attack):
                self._error(attack)

    def test_length_limit(self):
        message = self._error("x + " * (MAX_LENGTH // 4 + 1) + "x")
        self.assertIn(str(MAX_LENGTH), message)

    def test_nesting_limit(self):
        depth = MAX_NESTING + 1
        self.assertIn("anidados", self._error("(" * depth + "x" + ")" * depth))

    def test_magnitude_limit(self):
        self.assertIn("demasiado grande", self._error("9^9^9 * x"))

    def test_exponent_limit(self):
        self.assertIn(str(MAX_EXPONENT), self._error("x^(10^50)"))

    def test_multiline_input(self):
        self.assertIn("una sola línea", self._error("x\n+ y"))

    def test_literal_division_by_zero(self):
        self.assertIn("división entre cero", self._error("x/0 = 1"))

    def test_consecutive_numbers_are_rejected(self):
        # Antes "007" se leía como 0·7 y "1.5.2" como 1.5·0.2, sin avisar.
        for text in ("x = 007", "x = 01", "x = 1.5.2", "x = 2 3"):
            with self.subTest(text=text):
                self.assertIn("dos números seguidos", self._error(text))

    def test_number_next_to_a_name_is_still_implicit_multiplication(self):
        self.assertEqual(self._latex("3x + 2pi + 1e5"), r"3 x + 2 \pi + 100000.0")


class LogarithmTests(SimpleTestCase):
    def test_log_is_base_ten_and_ln_is_natural(self):
        self.assertAlmostEqual(float(parse_expression("log(1000)", XY)), 3.0)
        self.assertAlmostEqual(float(parse_expression("ln(e^2)", XY)), 2.0)
        self.assertAlmostEqual(float(parse_expression("log(8, 2)", XY)), 3.0)

    def test_log_evaluates_and_differentiates_with_floats(self):
        x = make_symbols(XY)["x"]
        expr = parse_expression("log(x)", XY)
        self.assertAlmostEqual(sp.lambdify([x], expr, "math")(100.0), 2.0)
        self.assertEqual(sp.simplify(sp.diff(expr, x) - 1 / (x * sp.log(10))), 0)

    def test_latex(self):
        cases = {
            "log(x)": r"\log_{10}{\left(x \right)}",
            "ln(x)": r"\ln{\left(x \right)}",
            "log(x, 2)": r"\log_{2}{\left(x \right)}",
            "2*log(x) + 1": r"2 \log_{10}{\left(x \right)} + 1",
            "-log(x)/3": r"- \frac{\log_{10}{\left(x \right)}}{3}",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(expression_to_latex(parse_expression(text, XY)), expected)

    def test_text_uses_the_parser_syntax(self):
        cases = {
            "log(x)": "log(x)",
            "ln(x + 1)": "ln(x + 1)",
            "log(x, 2)": "log(x, 2)",
            "abs(y) + x**2": "x^2 + abs(y)",
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                written = expression_to_text(parse_expression(text, XY))
                self.assertEqual(written, expected)
                # El texto vuelve a parsearse a la misma expresión.
                again = parse_expression(written, XY)
                self.assertEqual(sp.simplify(again - parse_expression(text, XY)), 0)

    def test_fixed_point_reports_isolations_in_parser_syntax(self):
        result = solve_fixed_point({
            "equations": ["x = log(y + 10)", "y = ln(x + 1)"], "variables": XY,
            "x0": [1, 1], "tolerance": 1e-6, "max_iterations": 100,
        }).to_dict()
        self.assertTrue(result["converged"])
        self.assertEqual([e["g_text"] for e in result["equations"]], ["log(y + 10)", "ln(x + 1)"])
        self.assertEqual(result["equations"][0]["g_latex"], r"\log_{10}{\left(10 + y \right)}")


class AlgebraicExampleTests(SimpleTestCase):
    def test_converges_to_the_hand_computed_solution(self):
        example = next(e for e in EXAMPLES["punto-fijo"] if e["id"] == "algebraico-2x2")
        result = solve_fixed_point({k: example[k] for k in
                                    ("equations", "variables", "x0", "tolerance", "max_iterations")})
        data = result.to_dict()
        self.assertTrue(data["converged"])
        x, y = data["solution"]
        self.assertAlmostEqual(x, 0.4036, places=3)
        self.assertAlmostEqual(y, 0.4593, places=3)
        self.assertTrue(math.isclose(3 * x - y**2 - 1, 0, abs_tol=1e-6))
        self.assertTrue(math.isclose(x**2 + 4 * y - 2, 0, abs_tol=1e-6))
        self.assertEqual([e["g_text"] for e in data["equations"]], ["y^2/3 + 1/3", "1/2 - x^2/4"])
