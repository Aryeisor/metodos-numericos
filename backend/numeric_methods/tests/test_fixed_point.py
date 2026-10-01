import json
import math

import sympy as sp
from django.test import SimpleTestCase
from rest_framework.test import APITestCase

from numeric_methods.examples_data import EXAMPLES
from numeric_methods.expressions.parser import make_symbols, parse_function
from numeric_methods.solvers.nonlinear.fixed_point import (
    MAX_SOLVE_DEGREE,
    NonlinearValidationError,
    build_fixed_point_system,
    estimate_degree,
    isolate,
    iterate,
    solve_fixed_point,
)
from numeric_methods.solvers.validation import MIN_ITERATIONS

CANNOT = "No fue posible despejar"


def equation(text, variables=("x", "y")):
    return parse_function(text, list(variables))[1]


def symbol(name, variables=("x", "y")):
    return make_symbols(list(variables))[name]


def run(equations, variables, x0=None, tolerance=1e-6, max_iterations=100):
    data = {
        "equations": equations,
        "variables": variables,
        "tolerance": tolerance,
        "max_iterations": max_iterations,
    }
    if x0 is not None:
        data["x0"] = x0
    return solve_fixed_point(data).to_dict()


class IsolationTests(SimpleTestCase):
    def test_isolates_the_variable_when_there_is_a_single_real_solution(self):
        x, y = symbol("x"), symbol("y")
        g = isolate(equation("3*x - cos(y) - 1 = 0"), x, 1)
        self.assertEqual(sp.simplify(g - (sp.cos(y) + 1) / 3), 0)

    def test_accepts_an_equation_already_written_as_x_equals(self):
        x, y = symbol("x"), symbol("y")
        g = isolate(equation("x = sqrt(y^2 + 1)"), x, 1)
        self.assertEqual(sp.simplify(g - sp.sqrt(y**2 + 1)), 0)

    def test_rejects_when_the_variable_does_not_appear(self):
        with self.assertRaises(NonlinearValidationError) as ctx:
            isolate(equation("y - 1 = 0"), symbol("x"), 1)
        self.assertEqual(
            ctx.exception.errors,
            [
                "No fue posible despejar x de la ecuación 1 de forma automática. "
                "Reescribe la ecuación de otra forma."
            ],
        )

    def test_rejects_when_there_are_no_solutions(self):
        with self.assertRaises(NonlinearValidationError) as ctx:
            isolate(equation("exp(x) + 1 = 0"), symbol("x"), 2)
        self.assertIn(f"{CANNOT} x de la ecuación 2", ctx.exception.errors[0])

    def test_rejects_when_every_solution_is_complex(self):
        # sympy devuelve dos raíces y ambas contienen la unidad imaginaria.
        x = symbol("x")
        f = equation("x^3 + y^2 + 1 = 0")
        candidates = sp.solve(f, x, rational=False)
        self.assertTrue(candidates)
        self.assertTrue(all(c.has(sp.I) for c in candidates))
        with self.assertRaises(NonlinearValidationError) as ctx:
            isolate(f, x, 1)
        self.assertIn(CANNOT, ctx.exception.errors[0])

    def test_rejects_when_real_solutions_are_only_provably_complex(self):
        # Con variables reales sympy descarta él mismo las raíces de x^2 = -4.
        with self.assertRaises(NonlinearValidationError) as ctx:
            isolate(equation("x^2 + 4 = 0"), symbol("x"), 1)
        self.assertIn(CANNOT, ctx.exception.errors[0])

    def test_rejects_multiple_real_solutions_listing_them(self):
        with self.assertRaises(NonlinearValidationError) as ctx:
            isolate(equation("x^2 - y = 0"), symbol("x"), 1)
        message = ctx.exception.errors[0]
        self.assertIn("admite 2 despejes reales de x", message)
        self.assertIn("ambiguo", message)
        self.assertIn("x = -sqrt(y)", message)
        self.assertIn("x = sqrt(y)", message)

    def test_rejects_high_degree_before_calling_sympy(self):
        # Despejar x de x^1000 - y tarda ~10 s en sympy: se rechaza antes.
        for text, degree in (("x^1000 - y = 0", "1000"), ("x^2*x^3 - y = 0", "5"),
                             ("((x^4)^4)^4 - y = 0", "64"), ("exp(x^5) - y = 0", "5")):
            with self.subTest(text=text):
                with self.assertRaises(NonlinearValidationError) as ctx:
                    isolate(equation(text), symbol("x"), 1)
                message = ctx.exception.errors[0]
                self.assertTrue(message.startswith(f"{CANNOT} x de la ecuación 1"))
                self.assertIn(f"grado {degree}", message)

    def test_degree_estimate(self):
        x = symbol("x")
        cases = {
            "x^4 + y = 0": 4,
            "x*y + 1 = 0": 1,
            "y = 0": 0,
            "sqrt(x) - y = 0": 0.5,
            "(x + 1)^2*x = 0": 3,
            "cos(x^2) - y = 0": 2,
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(estimate_degree(equation(text), x), expected)
        self.assertEqual(MAX_SOLVE_DEGREE, 4)

    def test_reports_every_failing_equation_at_once(self):
        with self.assertRaises(NonlinearValidationError) as ctx:
            build_fixed_point_system(["x^2 - y = 0", "exp(y) + 1 = 0"], ["x", "y"])
        errors = ctx.exception.errors
        self.assertEqual(len(errors), 2)
        self.assertIn("ecuación 1", errors[0])
        self.assertIn(f"{CANNOT} y de la ecuación 2", errors[1])

    def test_each_equation_is_isolated_for_its_own_variable(self):
        functions = build_fixed_point_system(["2*x - y = 0", "3*y - x - 1 = 0"], ["x", "y"])
        self.assertEqual([f.name for f in functions], ["x", "y"])
        self.assertEqual([f.dependencies for f in functions], [[1], [0]])


class SequentialUpdateTests(SimpleTestCase):
    def test_two_variables_use_the_new_x_when_computing_y(self):
        # x = (y + 1)/2 ; y = x^2/4 ; x0 = (0, 0)
        result = run(["2*x - y - 1 = 0", "4*y - x^2 = 0"], ["x", "y"], x0=[0, 0])
        first, second = result["iterations"][:2]
        # Iteración 1: x = (0 + 1)/2 = 0.5; y = 0.5^2/4 = 0.0625 (con la x NUEVA;
        # con la anterior, como en Jacobi, daría 0).
        self.assertEqual(first["x"], [0.5, 0.0625])
        self.assertEqual(first["extra"]["inputs"], [[0.0], [0.5]])
        # Iteración 2: x = (0.0625 + 1)/2 = 0.53125; y = 0.53125^2/4.
        self.assertEqual(second["x"], [0.53125, 0.53125**2 / 4])
        self.assertEqual(second["extra"]["inputs"], [[0.0625], [0.53125]])
        # Error: max(|0.53125 - 0.5|, |0.0705566... - 0.0625|) = 0.03125.
        self.assertEqual(second["error"], 0.03125)

    def test_three_variables_mix_new_and_previous_values(self):
        # x1 = 1 + x2*x3 ; x2 = (x1 + x3)/4 ; x3 = x1*x2/2 ; x0 = (0, 0, 0)
        result = run(
            ["x1 - x2*x3 - 1 = 0", "x2 = (x1 + x3)/4", "x3 = x1*x2/2"],
            ["x1", "x2", "x3"],
            x0=[0, 0, 0],
        )
        first, second = result["iterations"][:2]
        # Iteración 1: x1 = 1 + 0*0 = 1; x2 = (1 + 0)/4 = 0.25; x3 = 1*0.25/2 = 0.125
        self.assertEqual(first["x"], [1.0, 0.25, 0.125])
        # Iteración 2:
        #   x1 = 1 + x2^(1)*x3^(1)          = 1 + 0.25*0.125      = 1.03125
        #   x2 = (x1^(2) + x3^(1))/4         = (1.03125 + 0.125)/4 = 0.2890625
        #   x3 = x1^(2)*x2^(2)/2             = 1.03125*0.2890625/2 = 0.1490478515625
        self.assertEqual(second["x"], [1.03125, 0.2890625, 0.1490478515625])
        # Valores con los que se evaluó cada g_i (en el orden de sus dependencias):
        # x2 recibe x1 nuevo y x3 anterior; x3 recibe x1 y x2 nuevos.
        self.assertEqual(
            second["extra"]["inputs"],
            [[0.25, 0.125], [1.03125, 0.125], [1.03125, 0.2890625]],
        )

    def test_respects_the_minimum_number_of_iterations(self):
        # Converge exactamente en la primera iteración (g constantes), pero se
        # exige el mínimo de iteraciones como en los métodos lineales.
        result = run(["x - 2 = 0", "y - 3 = 0"], ["x", "y"])
        self.assertTrue(result["converged"])
        self.assertEqual(result["iterations_used"], MIN_ITERATIONS)
        self.assertEqual(result["solution"], [2.0, 3.0])

    def test_default_initial_point_is_zero(self):
        result = run(["3*x - cos(y) - 1 = 0", "4*y - sin(x) - 2 = 0"], ["x", "y"])
        self.assertEqual(result["x0"], [0.0, 0.0])
        self.assertEqual(result["iterations"][0]["extra"]["inputs"][0], [0.0])

    def test_stops_after_max_iterations_without_converging(self):
        # x = 2y, y = 2x: diverge sin salir de los reales.
        result = run(["x = 2*y", "y = 2*x"], ["x", "y"], x0=[1, 1], max_iterations=10)
        self.assertFalse(result["converged"])
        self.assertEqual(result["iterations_used"], 10)
        self.assertTrue(any("no alcanzó la tolerancia" in w for w in result["warnings"]))
        self.assertIsNone(result["failure"])


class NonFiniteTests(SimpleTestCase):
    def test_complex_value_stops_the_method(self):
        # x = sqrt(y), y = x - 3, x0 = (1, 1): en la iteración 2 sqrt(-2).
        result = run(["x = sqrt(y)", "y = x - 3"], ["x", "y"], x0=[1, 1])
        self.assertFalse(result["converged"])
        self.assertEqual(result["iterations_used"], 2)
        self.assertEqual(result["failure"], {"iteration": 2, "variable_index": 0})
        last = result["iterations"][-1]
        self.assertEqual(last["x"], [None, None])
        self.assertIsNone(last["error"])
        self.assertEqual(last["extra"]["inputs"], [[-2.0]])
        # La solución reportada es el último punto completo.
        self.assertEqual(result["solution"], [1.0, -2.0])
        self.assertEqual(len(result["warnings"]), 1)
        self.assertIn("no dio un número real finito", result["warnings"][0])
        self.assertIn("iteración 2", result["warnings"][0])

    def test_overflow_stops_the_method(self):
        # y = exp(x) con x creciendo: exp(19348244) desborda en la iteración 3.
        result = run(["x - y^2 - 1 = 0", "y = exp(x)"], ["x", "y"], x0=[0, 0])
        self.assertFalse(result["converged"])
        self.assertEqual(result["failure"], {"iteration": 3, "variable_index": 1})
        self.assertIsNone(result["iterations"][-1]["x"][1])
        self.assertTrue(all(math.isfinite(v) for v in result["solution"]))

    def test_domain_error_stops_the_method(self):
        # log(0) en la primera iteración.
        result = run(["x = log(y)", "y = x + 1"], ["x", "y"], x0=[0, 0])
        self.assertFalse(result["converged"])
        self.assertEqual(result["failure"], {"iteration": 1, "variable_index": 0})

    def test_result_is_strict_json(self):
        result = run(["x = sqrt(y)", "y = x - 3"], ["x", "y"], x0=[1, 1])
        json.dumps(result, allow_nan=False)


class ResultContentTests(SimpleTestCase):
    def test_meta_includes_latex_and_substitution_template(self):
        result = run(["3*x - cos(y) - 1 = 0", "4*y - sin(x) - 2 = 0"], ["x", "y"])
        self.assertEqual(result["category"], "nonlinear_system")
        self.assertEqual(result["method"], "punto-fijo")
        self.assertEqual(result["variables"], ["x", "y"])
        self.assertEqual(result["variables_latex"], ["x", "y"])
        first = result["equations"][0]
        self.assertEqual(first["variable"], "x")
        self.assertEqual(first["equation_latex"], r"3 x - \cos{\left(y \right)} - 1 = 0")
        self.assertIn(r"\cos{\left(y \right)}", first["g_latex"])
        self.assertIn("@@1@@", first["g_template"])
        self.assertNotIn("@@0@@", first["g_template"])
        self.assertEqual(first["dependencies"], [1])

    def test_template_uses_explicit_products(self):
        result = run(["x1 - x2*x3 - 1 = 0", "x2 = (x1 + x3)/4", "x3 = x1*x2/2"],
                     ["x1", "x2", "x3"])
        self.assertIn(r"@@1@@ \cdot @@2@@", result["equations"][0]["g_template"])

    def test_every_example_converges_to_a_root(self):
        for example in EXAMPLES["punto-fijo"]:
            with self.subTest(example=example["id"]):
                result = run(example["equations"], example["variables"], example["x0"],
                             example["tolerance"], example["max_iterations"])
                self.assertTrue(result["converged"])
                self.assertEqual(result["warnings"], [])
                variables = example["variables"]
                symbols = list(make_symbols(variables).values())
                for text in example["equations"]:
                    f = sp.lambdify(symbols, parse_function(text, variables)[1], "math")
                    self.assertAlmostEqual(f(*result["solution"]), 0, places=5)

    def test_burden_faires_example_reaches_the_known_solution(self):
        example = next(e for e in EXAMPLES["punto-fijo"] if e["id"] == "burden-faires-3x3")
        result = run(example["equations"], example["variables"], example["x0"])
        x1, x2, x3 = result["solution"]
        self.assertAlmostEqual(x1, 0.5, places=6)
        self.assertAlmostEqual(x2, 0.0, places=6)
        self.assertAlmostEqual(x3, -math.pi / 6, places=6)


class FixedPointEndpointTests(APITestCase):
    URL = "/api/solve/punto-fijo/"

    def _payload(self, **overrides):
        payload = {
            "equations": ["3*x - cos(y) - 1 = 0", "4*y - sin(x) - 2 = 0"],
            "variables": ["x", "y"],
            "x0": [0, 0],
            "tolerance": 0.000001,
            "max_iterations": 100,
        }
        payload.update(overrides)
        return payload

    def _post(self, **overrides):
        return self.client.post(self.URL, self._payload(**overrides), format="json")

    def _assert_flat_errors(self, response, field):
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn(field, data)
        self.assertIsInstance(data[field], list)
        self.assertTrue(all(isinstance(m, str) for m in data[field]))
        return data[field]

    def test_endpoint_returns_iterations_and_solution(self):
        response = self._post()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["converged"])
        self.assertGreaterEqual(len(data["iterations"]), MIN_ITERATIONS)
        self.assertAlmostEqual(data["solution"][0], 0.6004489, places=6)
        self.assertAlmostEqual(data["solution"][1], 0.6412532, places=6)
        self.assertEqual(data["category"], "nonlinear_system")
        self.assertEqual(data["variables"], ["x", "y"])
        self.assertEqual(len(data["equations"]), 2)
        self.assertIn("inputs", data["iterations"][0]["extra"])

    def test_x0_is_optional(self):
        payload = self._payload()
        del payload["x0"]
        response = self.client.post(self.URL, payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["x0"], [0.0, 0.0])

    def test_examples_by_method(self):
        response = self.client.get("/api/examples/?method=punto-fijo")
        self.assertEqual(response.status_code, 200)
        examples = response.json()
        self.assertEqual(len(examples), 4)
        for example in examples:
            with self.subTest(example=example["id"]):
                payload = {k: example[k] for k in
                           ("equations", "variables", "x0", "tolerance", "max_iterations")}
                data = self.client.post(self.URL, payload, format="json").json()
                self.assertTrue(data["converged"])

    def test_less_than_two_equations_returns_400(self):
        errors = self._assert_flat_errors(
            self._post(equations=["x - 1 = 0"], variables=["x"], x0=[0]), "equations"
        )
        self.assertIn("entre 2 y 6", errors[0])

    def test_too_many_equations_returns_400(self):
        names = [f"x{i}" for i in range(1, 8)]
        self._assert_flat_errors(
            self._post(equations=[f"{v} = 1" for v in names], variables=names, x0=None),
            "equations",
        )

    def test_variable_count_must_match_equations(self):
        errors = self._assert_flat_errors(self._post(variables=["x"]), "variables")
        self.assertIn("una variable por ecuación", errors[0])

    def test_invalid_or_repeated_variable_names_return_400(self):
        for variables in (["x", "x"], ["x", "2y"], ["x", "sin"], ["x", ""], ["x", "import"]):
            with self.subTest(variables=variables):
                self._assert_flat_errors(self._post(variables=variables), "variables")

    def test_empty_or_malformed_equation_returns_400(self):
        for bad in ("", "   ", "3*x +* y", "x = y = 1", "__import__('os').getcwd()", "z + x = 0"):
            with self.subTest(equation=bad):
                errors = self._assert_flat_errors(
                    self._post(equations=["x - 1 = 0", bad]), "equations"
                )
                self.assertTrue(errors[0].startswith("Ecuación 2:"))

    def test_x0_length_must_match(self):
        self._assert_flat_errors(self._post(x0=[0, 0, 0]), "x0")

    def test_negative_tolerance_returns_400(self):
        self._assert_flat_errors(self._post(tolerance=-1), "tolerance")

    def test_isolation_failure_returns_400_with_explanation(self):
        response = self._post(equations=["x^2 - y = 0", "exp(y) + 1 = 0"])
        self.assertEqual(response.status_code, 400)
        detail = response.json()["detail"]
        self.assertEqual(len(detail), 2)
        self.assertIn("ambiguo", detail[0])
        self.assertIn(f"{CANNOT} y de la ecuación 2", detail[1])

    def test_non_finite_iteration_is_reported_not_an_error(self):
        response = self._post(equations=["x = sqrt(y)", "y = x - 3"], x0=[1, 1])
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["converged"])
        self.assertEqual(data["failure"], {"iteration": 2, "variable_index": 0})
