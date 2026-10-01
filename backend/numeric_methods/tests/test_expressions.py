import time
from unittest import mock

import sympy as sp
from django.test import SimpleTestCase

from numeric_methods.expressions import parser as parser_module
from numeric_methods.expressions.differentiate import derivative, gradient, jacobian
from numeric_methods.expressions.parser import (
    ExpressionError,
    make_symbols,
    parse_expression,
    parse_function,
    parse_system,
    validate_expression_tree,
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


class LexicalLayerTests(SimpleTestCase):
    """Capa 1: lo que se rechaza antes de llegar a parse_expr."""

    def test_attacks_never_reach_parse_expr(self):
        with mock.patch.object(parser_module, "parse_expr") as parse_expr:
            for text in ParserSecurityTests.ATTACKS:
                with self.subTest(text=text), self.assertRaises(ExpressionError):
                    parse_expression(text, XY)
            parse_expr.assert_not_called()

    def test_rejects_line_breaks_instead_of_silently_truncating(self):
        # Antes, "x\n+y" se parseaba como "x": se perdía "+y" sin ningún error.
        for text in ["x\n+y", "x\r\n+ y", "x \\\n+ y", "x\r+y"]:
            with self.subTest(text=text), self.assertRaises(ExpressionError):
                parse_expression(text, XY)

    def test_rejects_control_and_invisible_characters(self):
        for text in ["x\x00+y", "x\x0b+y", "x​+y", "x +y", "x﻿"]:
            with self.subTest(text=repr(text)), self.assertRaises(ExpressionError):
                parse_expression(text, XY)

    def test_rejects_unicode_lookalikes(self):
        # dígito arábigo, signo menos U+2212, espacio de no separación, x de ancho completo
        for text in ["١ + x", "x − y", "x + y", "ｘ + y"]:
            with self.subTest(text=repr(text)), self.assertRaises(ExpressionError):
                parse_expression(text, XY)

    def test_accepts_tabs_and_surrounding_spaces(self):
        x, y = symbols()
        self.assertEqual(sp.simplify(parse_expression("  x\t+\ty  ", XY) - (x + y)), 0)


class GlobalDictTests(SimpleTestCase):
    """Capa 2: los únicos nombres visibles para el eval interno de parse_expr."""

    def test_contains_only_the_minimum_required(self):
        names = set(parser_module._global_dict())
        expected = (
            {"__builtins__", "Add", "Mul", "Pow", "Integer", "Float"}
            | set(parser_module.ALLOWED_FUNCTIONS)
            | set(parser_module.ALLOWED_CONSTANTS)
        )
        self.assertEqual(names, expected)

    def test_builtins_are_empty(self):
        self.assertEqual(parser_module._global_dict()["__builtins__"], {})

    def test_cannot_build_arbitrary_symbols(self):
        # Sin `Symbol`, la transformación auto_symbol no puede fabricar nombres.
        self.assertNotIn("Symbol", parser_module._global_dict())

    def test_no_dunder_or_module_entries(self):
        for name, value in parser_module._global_dict().items():
            with self.subTest(name=name):
                self.assertFalse(name.startswith("__") and name != "__builtins__")
                self.assertNotEqual(type(value).__name__, "module")


class TreeValidationTests(SimpleTestCase):
    """Capa 3: el árbol ya parseado sólo puede contener lo permitido.

    Se prueba directamente con árboles construidos a mano, porque la capa
    léxica impide producirlos desde texto: es la defensa por si ésta fallara.
    """

    def setUp(self):
        self.symbols = make_symbols(XY)
        self.x = self.symbols["x"]

    def assert_rejected(self, expr):
        with self.assertRaises(ExpressionError):
            validate_expression_tree(expr, self.symbols)

    def test_accepts_whitelisted_tree(self):
        x, y = self.symbols["x"], self.symbols["y"]
        validate_expression_tree(
            sp.sin(x) * sp.exp(y) + sp.log(x, 2) + sp.sqrt(y) + sp.Abs(x) + sp.pi + sp.E,
            self.symbols,
        )

    def test_rejects_undeclared_symbol(self):
        self.assert_rejected(self.x + sp.Symbol("z", real=True))

    def test_rejects_symbol_with_different_assumptions(self):
        self.assert_rejected(self.x + sp.Symbol("x"))

    def test_rejects_functions_outside_whitelist(self):
        for expr in (sp.Function("f")(self.x), sp.gamma(self.x), sp.Integral(self.x, self.x),
                     sp.Derivative(self.x, self.x), sp.floor(self.x),
                     sp.Piecewise((self.x, self.x > 0), (0, True))):
            with self.subTest(expr=type(expr).__name__):
                self.assert_rejected(expr)

    def test_rejects_non_finite_and_complex_constants(self):
        for expr in (sp.oo, -sp.oo, sp.zoo, sp.nan, sp.I * self.x):
            with self.subTest(expr=str(expr)):
                self.assert_rejected(expr)

    def test_rejects_non_expressions(self):
        for expr in (sp.Tuple(self.x, 1), sp.Eq(self.x, 1), sp.Lambda(self.x, self.x)):
            with self.subTest(expr=type(expr).__name__):
                self.assert_rejected(expr)


class ResourceLimitTests(SimpleTestCase):
    """Entradas cortas que serían costosísimas al evaluarse numéricamente."""

    def assert_rejected_fast(self, text):
        start = time.perf_counter()
        with self.assertRaises(ExpressionError):
            parse_expression(text, XY)
        self.assertLess(time.perf_counter() - start, 0.5)

    def test_rejects_numeric_power_towers(self):
        # 11 caracteres: con lambdify, 9**9**9 cuelga el proceso calculando enteros.
        for text in ["9**9**9", "9**9**9 * x", "x**(9**9**9)", "2**2**2**2**2**2", "sin(9^9^9)"]:
            with self.subTest(text=text):
                self.assert_rejected_fast(text)

    def test_rejects_huge_exponents(self):
        # Con floats desbordan al instante, pero con enteros exactos cuelgan.
        for text in ["x**(10**50)", "(1/2)**(10**50)", "y^1001"]:
            with self.subTest(text=text):
                self.assert_rejected_fast(text)

    def test_rejects_huge_numbers(self):
        for text in ["1e999", "10**400", "9" * 120, "1e101 * x"]:
            with self.subTest(text=text[:20]):
                self.assert_rejected_fast(text)

    def test_rejects_literal_division_by_zero(self):
        for text in ["1/0", "x/0", "0**-1", "1/(1-1)", "y/(2 - 2)"]:
            with self.subTest(text=text):
                self.assert_rejected_fast(text)

    def test_rejects_excessive_nesting_and_length(self):
        for text in ["**".join(["x"] * 45), "(" * 31 + "x" + ")" * 31, "x+" * 150 + "x"]:
            with self.subTest(text=text[:20]):
                self.assert_rejected_fast(text)

    def test_reasonable_expressions_stay_accepted(self):
        for text in [
            "x**1000",
            "**".join(["x"] * 35),
            " + ".join(f"{k}*x**{k}*y" for k in range(1, 25)),
            "1e100 * x",
            "sin(" * 25 + "x" + ")" * 25,
        ]:
            with self.subTest(text=text[:20]):
                parse_expression(text, XY)


class FractionLatexTests(SimpleTestCase):
    """Una división escrita por el usuario se dibuja siempre como una fracción."""

    def latex(self, text):
        return expression_to_latex(parse_expression(text, XY))

    def test_simple_numeric_fraction(self):
        self.assertEqual(self.latex("1/3"), r"\frac{1}{3}")
        self.assertEqual(self.latex("2/3"), r"\frac{2}{3}")
        self.assertEqual(self.latex("-1/3"), r"- \frac{1}{3}")

    def test_symbolic_numerator_and_denominator(self):
        self.assertEqual(self.latex("1/x"), r"\frac{1}{x}")
        self.assertEqual(self.latex("(x+1)/(y-2)"), r"\frac{x + 1}{y - 2}")
        self.assertEqual(self.latex("-x/2"), r"- \frac{x}{2}")
        self.assertEqual(self.latex("x/y/2"), r"\frac{x}{2 y}")
        self.assertEqual(self.latex("x*(1/3)"), r"\frac{x}{3}")

    def test_fraction_inside_larger_expression(self):
        self.assertEqual(self.latex("x - 1/3"), r"x - \frac{1}{3}")
        self.assertEqual(
            self.latex("sin(x/2) + (x+1)/3 - y/2"),
            r"\sin{\left(\frac{x}{2} \right)} + \frac{x + 1}{3} - \frac{y}{2}",
        )
        self.assertEqual(self.latex("x**(1/2)"), r"x^{\frac{1}{2}}")

    def test_nested_fraction(self):
        self.assertEqual(self.latex("1/(1/x)"), r"\frac{1}{\frac{1}{x}}")

    def test_never_renders_division_as_product_by_reciprocal(self):
        for text in ["1/3", "1/x", "x*(1/3)", "(1/3)*x", "1/3 + 1/4", "1/x**2", "1/(1/x)", "x**(1/2)"]:
            with self.subTest(text=text):
                latex = self.latex(text)
                self.assertNotIn(r"\cdot \frac", latex)
                self.assertNotIn(r"1 \frac", latex)
                self.assertNotIn(r"\left(-1\right)", latex)

    def test_evaluate_false_is_preserved_for_other_operations(self):
        self.assertEqual(self.latex("x + x"), "x + x")
        self.assertEqual(self.latex("x - x"), "x - x")

    def test_evaluated_derivatives_render_exactly_as_standard_sympy(self):
        system = parse_system(["x**2 + x*y - 10", "y + 3*x*y**2 - 57"], XY)
        J = jacobian([expr for _, expr in system], XY)
        for entry in J:
            self.assertEqual(expression_to_latex(entry), sp.latex(entry, order="none"))
        self.assertEqual(matrix_to_latex(J), sp.latex(J, order="none"))

    def test_derivative_with_divisions_from_user_input(self):
        # La derivada arrastra la división sin evaluar que escribió el usuario.
        _, expr = parse_function("g(x, y) = exp(-x/2) + x/(1+y)", XY)
        latex = expression_to_latex(jacobian([expr], XY)[0])
        self.assertIn(r"e^{- \frac{x}{2}}", latex)
        self.assertNotIn(r"\left(-1\right)", latex)
