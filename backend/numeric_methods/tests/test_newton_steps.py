import sympy as sp
from django.test import SimpleTestCase

from numeric_methods.examples_data import EXAMPLES
from numeric_methods.expressions.normalize import evaluate_tree
from numeric_methods.expressions.parser import make_symbols, parse_expression
from numeric_methods.expressions.to_latex import expression_to_latex
from numeric_methods.solvers.nonlinear.derivative_steps import entry_steps, signed_sum_latex, term_step
from numeric_methods.solvers.nonlinear.newton import solve_newton

XY = ["x", "y"]
X, Y = make_symbols(XY).values()
CHAPRA = ["x^2 + x*y - 10 = 0", "y + 3*x*y^2 - 57 = 0"]


def parsed(text):
    """Expresión del usuario en la forma evaluada que usa Newton."""
    return evaluate_tree(parse_expression(text, XY))


def step(text, variable):
    return term_step(parsed(text), {"x": X, "y": Y}[variable])


class TermRuleTests(SimpleTestCase):
    def test_power_rule(self):
        self.assertEqual(step("x^2", "x"), {
            "latex": r"\frac{\partial}{\partial x}\left(x^{2}\right) = 2 \cdot x = 2 x",
            "rule": "regla de la potencia",
        })

    def test_other_variable_is_a_constant_factor(self):
        result = step("x*y", "x")
        self.assertEqual(result["latex"], r"\frac{\partial}{\partial x}\left(x y\right) = y")
        self.assertIn("y se trata como constante respecto a x", result["rule"])

    def test_constant_term(self):
        self.assertEqual(step("x*y", "y")["latex"], r"\frac{\partial}{\partial y}\left(x y\right) = x")
        self.assertEqual(term_step(sp.Integer(-10), X), {
            "latex": r"\frac{\partial}{\partial x}\left(-10\right) = 0",
            "rule": "derivada de una constante",
        })
        self.assertIn("no depende de x", term_step(Y**2, X)["rule"])

    def test_power_with_coefficient_that_depends_on_other_variables(self):
        result = step("3*x*y^2", "y")
        self.assertEqual(result["latex"],
                         r"\frac{\partial}{\partial y}\left(3 x y^{2}\right) = 3 x \cdot 2 \cdot y = 6 x y")
        self.assertIn("regla de la potencia", result["rule"])

    def test_chain_rule_with_a_function(self):
        result = step("sin(x*y)", "x")
        self.assertEqual(
            result["latex"],
            r"\frac{\partial}{\partial x}\left(\sin{\left(x y \right)}\right) = "
            r"\cos{\left(x y \right)} \cdot y = y \cos{\left(x y \right)}",
        )
        self.assertTrue(result["rule"].startswith("regla de la cadena"))

    def test_chain_rule_with_a_power_of_an_expression(self):
        result = step("sqrt(x^2 + y)", "x")
        self.assertIn(r"\frac{1}{2} \cdot", result["latex"])
        self.assertIn(r"\cdot 2 x =", result["latex"])
        self.assertIn("potencia de una expresión", result["rule"])

    def test_product_rule(self):
        result = step("x*exp(x)", "x")
        self.assertIn(r"1 \cdot e^{x} + x \cdot e^{x}", result["latex"])
        self.assertTrue(result["rule"].startswith("regla del producto"))

    def test_absolute_value_has_no_leftover_derivative(self):
        self.assertEqual(
            step("abs(y)", "y")["latex"],
            r"\frac{\partial}{\partial y}\left(\left|{y}\right|\right) = \operatorname{sign}{\left(y \right)}",
        )

    def test_unknown_form_shows_only_the_result(self):
        result = step("2^x", "x")
        self.assertEqual(result["rule"], "derivada directa")
        self.assertEqual(result["latex"].count("="), 1)

    def test_every_step_ends_in_the_sympy_derivative(self):
        for text in ("x^2", "x*y", "3*x*y^2", "sin(x*y)", "sqrt(x^2 + y)", "x*exp(x)", "abs(y)",
                     "(x + y)^2", "x/y", "ln(x*y)", "cos(x)^3"):
            for variable, symbol in (("x", X), ("y", Y)):
                with self.subTest(text=text, variable=variable):
                    expected = expression_to_latex(sp.diff(parsed(text), symbol), order=None)
                    self.assertTrue(step(text, variable)["latex"].endswith(f"= {expected}"))


class SumTests(SimpleTestCase):
    def test_a_negative_sum_is_not_negated_as_a_block(self):
        # La derivada de −81(x₂ + 0.1)² es −162x₂ − 16.2 (una suma): va entera.
        derivative = sp.Add(-162 * X, -16.2)
        self.assertEqual(signed_sum_latex([derivative, sp.Integer(0)]), "- 162 x - 16.2 + 0")
        self.assertEqual(signed_sum_latex([sp.Integer(0), derivative]), r"0 + \left(- 162 x - 16.2\right)")

    def test_entry_lists_each_term_and_the_sum(self):
        result = entry_steps(parsed("x^2 + x*y - 10"), X, "f_{1}")
        self.assertEqual(len(result["terms"]), 3)
        self.assertEqual(result["sum_latex"], r"\frac{\partial f_{1}}{\partial x} = 2 x + y + 0 = 2 x + y")

    def test_many_constant_terms_are_grouped(self):
        result = entry_steps(parsed("x^2 + y + y^3 + sin(y) + 1"), X, "f_{1}")
        self.assertEqual(len(result["terms"]), 2)
        self.assertIn("ninguno de estos términos depende de x", result["terms"][1]["rule"])
        self.assertTrue(result["sum_latex"].endswith("= 2 x"))


class NewtonResponseStepsTests(SimpleTestCase):
    def setUp(self):
        self.result = solve_newton({"equations": CHAPRA, "variables": XY, "x0": [1.5, 3.5],
                                    "tolerance": 1e-6, "max_iterations": 100}).to_dict()

    def test_jacobian_steps_shape(self):
        steps = self.result["jacobian"]["steps"]
        self.assertEqual(len(steps), 2)
        self.assertTrue(all(len(row) == 2 for row in steps))
        self.assertEqual(steps[0][0]["sum_latex"],
                         r"\frac{\partial f_{1}}{\partial x} = 2 x + y + 0 = 2 x + y")

    def test_term_templates_and_values(self):
        terms = self.result["equations"][0]["terms"]
        self.assertEqual(terms, [
            {"sign": "+", "template": "@@0@@^{2}"},
            {"sign": "+", "template": r"@@0@@ \cdot @@1@@"},
            {"sign": "-", "template": "10"},
        ])
        extra = self.result["iterations"][0]["extra"]
        # f₁(1.5, 3.5) = (1.5)² + (1.5)(3.5) − 10 = 2.25 + 5.25 − 10 = −2.5
        self.assertEqual(extra["F_terms"][0], [2.25, 5.25, -10.0])
        self.assertEqual(extra["F_terms"][1], [55.125, 3.5, -57.0])

    def test_term_values_add_up_to_F_in_every_iteration_of_every_example(self):
        for example in EXAMPLES["newton"]:
            result = solve_newton({k: example[k] for k in
                                   ("equations", "variables", "x0", "tolerance", "max_iterations")}).to_dict()
            for row in result["iterations"]:
                for values, total in zip(row["extra"]["F_terms"], row["extra"]["F"]):
                    with self.subTest(example=example["id"], iteration=row["iteration"]):
                        self.assertAlmostEqual(sum(values), total, places=9)
