import sympy as sp
from django.test import SimpleTestCase
from rest_framework.test import APITestCase

from numeric_methods.examples_data import EXAMPLES
from numeric_methods.expressions.parser import make_symbols, parse_equation, parse_function
from numeric_methods.expressions.to_latex import expression_to_latex
from numeric_methods.solvers.nonlinear.fixed_point import build_fixed_point_system
from numeric_methods.solvers.nonlinear.isolation_steps import _agrees, isolation_steps

XY = ["x", "y"]
GROUP = "Dejamos los términos con {} en el lado izquierdo y pasamos los demás al derecho, cambiando su signo:"
SIMPLIFY = "Simplificamos: esta es la función de iteración que se evalúa en cada paso."


def isolation(text, variable, variables=XY):
    """Despeje de `variable` en `text`, tal como lo arma el solver."""
    functions = build_fixed_point_system(
        [text if v == variable else f"{v} = 1" for v in variables], variables
    )
    return next(f for f in functions if f.name == variable).isolation


def pairs(result):
    return [(s["description"], s["latex"]) for s in result["steps"]]


class LinearStepsTests(SimpleTestCase):
    def test_simple_linear_equation(self):
        result = isolation("3*x - y**2 - 1 = 0", "x")
        self.assertEqual(result["kind"], "linear")
        self.assertEqual(pairs(result), [
            ("Ecuación original:", "3 x - y^{2} - 1 = 0"),
            (GROUP.format("x"), "3 x = 1 + y^{2}"),
            ("Dividimos ambos lados entre el coeficiente de x, que es 3:", r"x = \frac{1 + y^{2}}{3}"),
            (SIMPLIFY, r"x = \frac{1}{3} + \frac{y^{2}}{3}"),
        ])

    def test_coefficient_one_has_no_division_and_no_repeated_step(self):
        result = isolation("x - 2*y = 0", "x")
        self.assertEqual(pairs(result), [
            ("Ecuación original:", "x - 2 y = 0"),
            (GROUP.format("x"), "x = 2 y"),
        ])

    def test_negative_coefficient(self):
        result = isolation("-3*y + x + 4 = 1", "y")
        self.assertEqual(pairs(result), [
            ("Ecuación original:", "- 3 y + x + 4 = 1"),
            (GROUP.format("y"), "- 3 y = -3 - x"),
            ("Dividimos ambos lados entre el coeficiente de y, que es -3:", r"y = \frac{-3 - x}{-3}"),
            (SIMPLIFY, r"y = 1 + \frac{x}{3}"),
        ])

    def test_coefficient_minus_one_multiplies_by_minus_one(self):
        result = isolation("5 - x = y", "x")
        self.assertEqual(pairs(result)[1:], [
            (GROUP.format("x"), "- x = -5 + y"),
            ("Multiplicamos ambos lados por −1:", "x = 5 - y"),
        ])

    def test_fractional_coefficient_shows_the_computed_quotient(self):
        # Antes de calcularlo se veía "- 2x / (- 3/3)".
        result = isolation("x = (x + y)/3", "y")
        self.assertEqual(result["steps"][-1], {
            "description": "Dividimos ambos lados entre el coeficiente de y, que es -1/3:",
            "latex": "y = 2 x",
        })

    def test_symbolic_coefficient(self):
        result = isolation("x*y + x - 1 = 0", "x")
        self.assertEqual(pairs(result)[1:], [
            (GROUP.format("x"), r"\left(1 + y\right) x = 1"),
            ("Dividimos ambos lados entre el coeficiente de x, que es y + 1:", r"x = \frac{1}{1 + y}"),
        ])

    def test_already_isolated_only_reorders(self):
        result = isolation("y = (x + 1)/2", "y")
        self.assertEqual(pairs(result), [
            ("Ecuación original:", r"y = \frac{x + 1}{2}"),
            ("Ordenamos los términos: esta es la función de iteración.", r"y = \frac{1}{2} + \frac{x}{2}"),
        ])

    def test_already_grouped_skips_moving_terms(self):
        result = isolation("3*x = y^2 + 1", "x")
        self.assertEqual([d for d, _ in pairs(result)], [
            "Ecuación original:",
            "Dividimos ambos lados entre el coeficiente de x, que es 3:",
            SIMPLIFY,
        ])


class GeneralCaseTests(SimpleTestCase):
    def test_single_power_term_with_constant(self):
        result = isolation("x^3 - 8 = 0", "x")
        self.assertEqual(result["kind"], "power")
        self.assertEqual(pairs(result), [
            ("Ecuación original:", "x^{3} - 8 = 0"),
            ("Dejamos el término con x en el lado izquierdo y pasamos los demás al derecho, "
             "cambiando su signo:", "x^{3} = 8"),
            ("Aplicamos la raíz cúbica en ambos lados:", r"x = \sqrt[3]{8}"),
            (SIMPLIFY, "x = 2"),
        ])

    def test_power_with_coefficient(self):
        result = isolation("2*y^3 - x = 0", "y")
        self.assertEqual(result["kind"], "power")
        self.assertEqual([latex for _, latex in pairs(result)][1:4], [
            "2 y^{3} = x",
            r"y^{3} = \frac{x}{2}",
            r"y = \sqrt[3]{\frac{x}{2}}",
        ])

    def test_square_root_is_undone_by_squaring(self):
        result = isolation("sqrt(x) = y + 1", "x")
        self.assertEqual(pairs(result), [
            ("Ecuación original:", r"\sqrt{x} = y + 1"),
            ("Elevamos ambos lados a la potencia 2:", r"x = \left(1 + y\right)^{2}"),
        ])

    def test_reciprocal(self):
        result = isolation("1/y - x = 0", "y")
        self.assertEqual(result["steps"][-1]["latex"], r"y = \frac{1}{x}")

    def test_other_forms_fall_back_without_inventing_steps(self):
        result = isolation("exp(y) = x + 3", "y")
        self.assertEqual(result["kind"], "symbolic")
        steps = result["steps"]
        self.assertEqual(len(steps), 3)
        self.assertIn("métodos simbólicos", steps[1]["description"])
        self.assertIsNone(steps[1]["latex"])
        self.assertEqual(steps[2]["latex"], r"y = \ln{\left(3 + x \right)}")

    def test_steps_that_do_not_reach_g_are_never_shown(self):
        # Si el desglose no coincide con la g de sympy, se usa el respaldo.
        x, y = make_symbols(XY).values()
        _, lhs, rhs = parse_equation("3*x - y = 0", XY)
        wrong_g = y / 2
        result = isolation_steps(lhs, rhs, x, wrong_g)
        self.assertEqual(result["kind"], "symbolic")

    def test_numeric_agreement_check(self):
        x, y = make_symbols(XY).values()
        self.assertTrue(_agrees((y + 1) / 3, sp.Rational(1, 3) + y / 3))
        self.assertFalse(_agrees(y + 1, y + 2))
        self.assertTrue(_agrees(sp.cbrt(8 * y), 2 * sp.cbrt(y)))


class ExamplesTests(SimpleTestCase):
    def test_every_example_ends_in_its_iteration_function(self):
        for example in EXAMPLES["punto-fijo"]:
            functions = build_fixed_point_system(example["equations"], example["variables"])
            for f in functions:
                with self.subTest(example=example["id"], variable=f.name):
                    steps = f.isolation["steps"]
                    self.assertEqual(steps[0]["description"], "Ecuación original:")
                    self.assertEqual(steps[-1]["latex"], f"{sp.latex(f.symbol)} = {expression_to_latex(f.g)}")
                    # Ninguna fórmula se repite dos veces seguidas.
                    latexes = [s["latex"] for s in steps if s["latex"]]
                    self.assertTrue(all(a != b for a, b in zip(latexes, latexes[1:])))

    def test_all_current_examples_are_linear_in_their_variable(self):
        kinds = {
            example["id"]: [f.isolation["kind"] for f in
                            build_fixed_point_system(example["equations"], example["variables"])]
            for example in EXAMPLES["punto-fijo"]
        }
        self.assertTrue(all(kind == "linear" for ks in kinds.values() for kind in ks), kinds)


class IsolationApiTests(APITestCase):
    def test_response_includes_isolation_steps(self):
        example = next(e for e in EXAMPLES["punto-fijo"] if e["id"] == "algebraico-2x2")
        payload = {k: example[k] for k in ("equations", "variables", "x0", "tolerance", "max_iterations")}
        data = self.client.post("/api/solve/punto-fijo/", payload, format="json").json()
        isolation_ = data["equations"][0]["isolation"]
        self.assertEqual(isolation_["kind"], "linear")
        self.assertEqual(isolation_["steps"][-1]["latex"], f"x = {data['equations'][0]['g_latex']}")
        self.assertEqual(set(isolation_["steps"][0]), {"description", "latex"})


class FunctionNameOnLeftSideTests(SimpleTestCase):
    def test_known_function_on_the_left_is_an_equation_not_a_header(self):
        name, expr = parse_function("sqrt(x) = y + 1", XY)
        self.assertIsNone(name)
        x, y = make_symbols(XY).values()
        self.assertEqual(sp.simplify(expr - (sp.sqrt(x) - y - 1)), 0)

    def test_user_function_header_still_works(self):
        name, _ = parse_function("f1(x, y) = x^2 - y", XY)
        self.assertEqual(name, "f1")
