import sympy as sp
from django.test import SimpleTestCase

from numeric_methods.expressions.differentiate import derivative, gradient, jacobian
from numeric_methods.expressions.parser import (
    ExpressionError,
    make_symbols,
    parse_expression,
    parse_function,
    parse_system,
)
from numeric_methods.expressions.to_latex import (
    expression_to_latex,
    function_to_latex,
    matrix_to_latex,
)

XY = ["x", "y"]


def symbols():
    s = make_symbols(XY)
    return s["x"], s["y"]


class ParseExpressionTests(SimpleTestCase):
    def test_parses_python_syntax(self):
        x, y = symbols()
        expr = parse_expression("x**2 + x*y - 10", XY)
        self.assertEqual(sp.simplify(expr - (x**2 + x * y - 10)), 0)

    def test_accepts_caret_and_implicit_multiplication(self):
        x, y = symbols()
        expr = parse_expression("3x^2 + 2(x + y)", XY)
        self.assertEqual(sp.simplify(expr - (3 * x**2 + 2 * (x + y))), 0)

    def test_accepts_functions_and_constants(self):
        x, y = symbols()
        expr = parse_expression("sin(x) + exp(y) + ln(x) + sqrt(y) + pi", XY)
        expected = sp.sin(x) + sp.exp(y) + sp.log(x) + sp.sqrt(y) + sp.pi
        self.assertEqual(sp.simplify(expr - expected), 0)

    def test_does_not_simplify_what_the_user_wrote(self):
        self.assertNotEqual(parse_expression("x - x", XY), 0)

    def test_rejects_unknown_names(self):
        with self.assertRaises(ExpressionError):
            parse_expression("x + z", XY)

    def test_rejects_empty_and_malformed(self):
        for text in ["", "   ", "x +", "(x + 1", "x ** * 2"]:
            with self.subTest(text=text), self.assertRaises(ExpressionError):
                parse_expression(text, XY)

    def test_rejects_too_long_input(self):
        with self.assertRaises(ExpressionError):
            parse_expression("x+" * 200 + "x", XY)


class ParserSecurityTests(SimpleTestCase):
    """Nada de esto debe llegar a evaluarse: la validación léxica lo frena antes."""

    ATTACKS = [
        '__import__("os").system("echo hacked")',
        "__import__('os').getcwd()",
        "x.__class__.__mro__",
        "(lambda: 1)()",
        "open('/etc/passwd')",
        "eval('1+1')",
        "exec('import os')",
        "globals()",
        "[x for x in ()]",
        "{'a': 1}",
        "x if y else 1",
        "'texto'",
        "x; import os",
        "x @ y",
        "0x1F",
        "2j",
        "1_000",
    ]

    def test_rejects_code_injection(self):
        for text in self.ATTACKS:
            with self.subTest(text=text), self.assertRaises(ExpressionError):
                parse_expression(text, XY)

    def test_rejects_reserved_or_invalid_variable_names(self):
        for variables in (["sin"], ["pi"], ["lambda"], ["x", "x"], ["2x"], ["__x"], []):
            with self.subTest(variables=variables), self.assertRaises(ExpressionError):
                make_symbols(variables)


class ParseFunctionTests(SimpleTestCase):
    def test_function_header_form(self):
        x, y = symbols()
        name, expr = parse_function("f1(x, y) = x**2 + x*y - 10", XY)
        self.assertEqual(name, "f1")
        self.assertEqual(sp.simplify(expr - (x**2 + x * y - 10)), 0)

    def test_equation_form_moves_everything_to_the_left(self):
        x, y = symbols()
        name, expr = parse_function("x**2 + x*y = 10", XY)
        self.assertIsNone(name)
        self.assertEqual(sp.simplify(expr - (x**2 + x * y - 10)), 0)

    def test_header_arguments_must_match_variables(self):
        with self.assertRaises(ExpressionError):
            parse_function("f1(x) = x**2 + y", XY)

    def test_rejects_double_equals(self):
        with self.assertRaises(ExpressionError):
            parse_function("x == 1", XY)

    def test_parse_system(self):
        system = parse_system(["f1(x, y) = x**2 + x*y - 10", "f2(x, y) = y + 3*x*y**2 - 57"], XY)
        self.assertEqual([name for name, _ in system], ["f1", "f2"])


class DifferentiateTests(SimpleTestCase):
    def test_derivative_and_gradient(self):
        x, y = symbols()
        expr = parse_expression("x**2 + x*y - 10", XY)
        self.assertEqual(sp.simplify(derivative(expr, "x") - (2 * x + y)), 0)
        grad = gradient(expr, XY)
        self.assertEqual(sp.simplify(grad[1] - x), 0)

    def test_jacobian_of_textbook_system(self):
        # Burden & Faires: f1 = x² + xy − 10, f2 = y + 3xy² − 57
        x, y = symbols()
        system = parse_system(["x**2 + x*y - 10", "y + 3*x*y**2 - 57"], XY)
        J = jacobian([expr for _, expr in system], XY)
        expected = sp.Matrix([[2 * x + y, x], [3 * y**2, 1 + 6 * x * y]])
        self.assertEqual(sp.simplify(J - expected), sp.zeros(2, 2))

    def test_jacobian_evaluates_at_a_point(self):
        x, y = symbols()
        system = parse_system(["x**2 + x*y - 10", "y + 3*x*y**2 - 57"], XY)
        J = jacobian([expr for _, expr in system], XY)
        self.assertEqual(J.subs({x: 1.5, y: 3.5}).tolist(), [[6.5, 1.5], [36.75, 32.5]])


class ToLatexTests(SimpleTestCase):
    def test_expression_keeps_user_term_order(self):
        expr = parse_expression("exp(-x) - x", XY)
        self.assertEqual(expression_to_latex(expr), "e^{- x} - x")

    def test_function_with_indexed_name(self):
        _, expr = parse_function("f1(x, y) = x**2 + x*y - 10", XY)
        self.assertEqual(function_to_latex("f1", XY, expr), "f_{1}(x, y) = x^{2} + x y - 10")

    def test_matrix_keeps_order_of_parsed_entries(self):
        x, y = symbols()
        entry = parse_expression("2x + y", XY)
        latex = matrix_to_latex([[entry, x], [3 * y**2, 1]])
        self.assertIn(r"\begin{matrix}", latex)
        self.assertIn("2 x + y", latex)
