import json
import math

import sympy as sp
from django.test import SimpleTestCase
from rest_framework.test import APITestCase

from numeric_methods.examples_data import EXAMPLES
from numeric_methods.expressions.differentiate import derivative, jacobian
from numeric_methods.expressions.normalize import evaluate_tree
from numeric_methods.expressions.parser import make_symbols, parse_function
from numeric_methods.linalg.cramer import (
    MAX_SIZE,
    SingularMatrixError,
    cramer,
    determinant,
    is_singular,
    replace_column,
)
from numeric_methods.solvers.nonlinear.newton import solve_newton
from numeric_methods.solvers.validation import MIN_ITERATIONS, InputValidationError

XY = ["x", "y"]
ALGEBRAIC = ["3*x - y**2 - 1 = 0", "x**2 + 4*y - 2 = 0"]
SINGULAR_MESSAGE = "El Jacobiano es singular en la iteración 1, no se puede continuar"


def run(equations, variables=XY, x0=None, tolerance=1e-6, max_iterations=100):
    data = {"equations": equations, "variables": variables,
            "tolerance": tolerance, "max_iterations": max_iterations}
    if x0 is not None:
        data["x0"] = x0
    return solve_newton(data).to_dict()


class DeterminantTests(SimpleTestCase):
    def test_small_matrices(self):
        self.assertEqual(determinant([[7]]), 7)
        self.assertEqual(determinant([[3, 1], [2, 4]]), 10)
        self.assertEqual(determinant([[2, -3, 1], [2, 0, -1], [1, 4, 5]]), 49)
        self.assertEqual(determinant([[2, 0, 0, 0], [0, 3, 0, 0], [0, 0, 4, 0], [0, 0, 0, 5]]), 120)

    def test_matches_sympy_on_a_dense_4x4(self):
        matrix = [[1.5, -2, 0.3, 4], [2, 1, -1, 0.5], [0, 3, 2, -1], [1, 1, 1, 1]]
        self.assertAlmostEqual(determinant(matrix), float(sp.Matrix(matrix).det()), places=10)

    def test_zero_determinant_has_no_sign(self):
        self.assertEqual(str(determinant([[0.0, 0.0], [1.0, -1.0]])), "0.0")

    def test_rejects_non_square_and_too_large(self):
        with self.assertRaises(ValueError):
            determinant([[1, 2]])
        with self.assertRaises(ValueError):
            determinant([[float(i == j) for j in range(MAX_SIZE + 1)] for i in range(MAX_SIZE + 1)])

    def test_replace_column(self):
        self.assertEqual(replace_column([[1, 2], [3, 4]], 1, [9, 8]), [[1, 9], [3, 8]])


class CramerTests(SimpleTestCase):
    def test_solves_a_known_system(self):
        # 2x + y = 5, x − y = 1 → D = −3, Dx = −6, Dy = −3 → (2, 1)
        result = cramer([[2, 1], [1, -1]], [5, 1])
        self.assertEqual(result.determinant, -3)
        self.assertEqual(result.column_determinants, [-6, -3])
        self.assertEqual(result.column_matrices, [[[5, 1], [1, -1]], [[2, 5], [1, 1]]])
        self.assertEqual(result.solution, [2, 1])

    def test_singular_matrix_raises_with_its_determinant(self):
        with self.assertRaises(SingularMatrixError) as ctx:
            cramer([[1, 2], [2, 4]], [1, 1])
        self.assertEqual(ctx.exception.determinant, 0)

    def test_singularity_is_relative_to_the_scale(self):
        # Determinante diminuto pero matriz bien condicionada: no es singular.
        self.assertFalse(is_singular([[1e-10, 0], [0, 1e-10]]))
        # Filas casi paralelas: singular aunque el determinante no sea 0 exacto.
        self.assertTrue(is_singular([[1, 1], [1, 1 + 1e-14]]))


class DifferentiateFixesTests(SimpleTestCase):
    """Problemas encontrados en expressions/differentiate.py al usarlo en Newton."""

    def test_symbols_without_real_assumption_no_longer_give_zero(self):
        f = parse_function("x^2 + y", XY)[1]
        x = make_symbols(XY)["x"]
        self.assertEqual(derivative(f, sp.Symbol("x")), 2 * x)
        J = jacobian([f], [sp.Symbol("x"), sp.Symbol("y")])
        self.assertEqual(J.tolist(), [[2 * x, 1]])

    def test_names_and_symbols_can_be_mixed(self):
        f = parse_function("x*y", XY)[1]
        x, y = make_symbols(XY).values()
        self.assertEqual(jacobian([f], ["x", sp.Symbol("y")]).tolist(), [[y, x]])

    def test_evaluate_tree_flattens_what_the_parser_kept(self):
        f = parse_function("3*x - y**2 - 1 = 0", XY)[1]
        self.assertEqual(str(evaluate_tree(f)), "3*x - y**2 - 1")


class HandComputedIterationTests(SimpleTestCase):
    """Sistema 3x − y² − 1 = 0, x² + 4y − 2 = 0 desde (0, 0), calculado a mano.

    J(x, y) = [[3, −2y], [2x, 4]].
    Iteración 1, en (0, 0): F = (−1, −2), J = [[3, 0], [0, 4]], D = 12,
      Dx = |1 0; 2 4| = 4, Dy = |3 1; 0 2| = 6 → Δ = (1/3, 1/2) → x¹ = (1/3, 1/2).
    Iteración 2, en (1/3, 1/2): F = (−1/4, 1/9), J = [[3, −1], [2/3, 4]],
      D = 38/3, Dx = |1/4 −1; −1/9 4| = 8/9, Dy = |3 1/4; 2/3 −1/9| = −1/2
      → Δ = (4/57, −3/76) → x² = (23/57, 35/76).
    """

    def setUp(self):
        self.result = run(ALGEBRAIC, x0=[0, 0])
        self.first, self.second = self.result["iterations"][:2]

    def test_symbolic_jacobian(self):
        self.assertEqual(self.result["jacobian"]["latex"], [["3", "- 2 y"], ["2 x", "4"]])
        self.assertEqual(self.result["jacobian"]["text"], [["3", "-2*y"], ["2*x", "4"]])
        self.assertEqual([e["function_text"] for e in self.result["equations"]],
                         ["3*x - y^2 - 1", "x^2 + 4*y - 2"])

    def test_first_iteration(self):
        extra = self.first["extra"]
        self.assertEqual(extra["point"], [0.0, 0.0])
        self.assertEqual(extra["F"], [-1.0, -2.0])
        self.assertEqual(extra["J"], [[3.0, 0.0], [0.0, 4.0]])
        self.assertEqual(extra["minus_F"], [1.0, 2.0])
        self.assertEqual(extra["D"], 12.0)
        self.assertEqual(extra["matrices"], [[[1.0, 0.0], [2.0, 4.0]], [[3.0, 1.0], [0.0, 2.0]]])
        self.assertEqual(extra["D_i"], [4.0, 6.0])
        self.assertAlmostEqual(extra["delta"][0], 1 / 3, places=15)
        self.assertEqual(extra["delta"][1], 0.5)
        self.assertAlmostEqual(self.first["x"][0], 1 / 3, places=15)
        self.assertEqual(self.first["x"][1], 0.5)
        self.assertEqual(self.first["error"], 0.5)

    def test_second_iteration(self):
        extra = self.second["extra"]
        self.assertAlmostEqual(extra["F"][0], -0.25, places=14)
        self.assertAlmostEqual(extra["F"][1], 1 / 9, places=14)
        for got, expected in zip(sum(extra["J"], []), [3, -1, 2 / 3, 4]):
            self.assertAlmostEqual(got, expected, places=14)
        self.assertAlmostEqual(extra["D"], 38 / 3, places=12)
        self.assertAlmostEqual(extra["D_i"][0], 8 / 9, places=12)
        self.assertAlmostEqual(extra["D_i"][1], -1 / 2, places=12)
        self.assertAlmostEqual(extra["delta"][0], 4 / 57, places=12)
        self.assertAlmostEqual(extra["delta"][1], -3 / 76, places=12)
        self.assertAlmostEqual(self.second["x"][0], 23 / 57, places=12)
        self.assertAlmostEqual(self.second["x"][1], 35 / 76, places=12)
        self.assertAlmostEqual(self.second["error"], 4 / 57, places=12)

    def test_converges_to_the_solution(self):
        self.assertTrue(self.result["converged"])
        self.assertEqual(self.result["iterations_used"], MIN_ITERATIONS)
        x, y = self.result["solution"]
        self.assertAlmostEqual(3 * x - y**2 - 1, 0, places=12)
        self.assertAlmostEqual(x**2 + 4 * y - 2, 0, places=12)


class FailureTests(SimpleTestCase):
    def test_singular_jacobian_stops_without_crashing(self):
        # J = [[2x, 2y], [1, −1]] es singular en (0, 0).
        result = run(["x^2 + y^2 - 4 = 0", "x - y = 0"], x0=[0, 0])
        self.assertFalse(result["converged"])
        self.assertEqual(result["failure"], {"iteration": 1, "reason": "singular"})
        self.assertEqual(len(result["warnings"]), 1)
        self.assertIn(SINGULAR_MESSAGE, result["warnings"][0])
        last = result["iterations"][-1]
        self.assertEqual(last["extra"]["D"], 0.0)
        self.assertEqual(last["extra"]["J"], [[0.0, 0.0], [1.0, -1.0]])
        self.assertNotIn("D_i", last["extra"])
        self.assertEqual(last["x"], [None, None])
        self.assertIsNone(last["error"])
        self.assertEqual(result["solution"], [0.0, 0.0])
        json.dumps(result, allow_nan=False)

    def test_domain_error_is_non_convergence(self):
        # ln(0) en el punto inicial.
        result = run(["ln(x) + y - 1 = 0", "x - y = 0"], x0=[0, 0])
        self.assertFalse(result["converged"])
        self.assertEqual(result["failure"], {"iteration": 1, "reason": "non_finite"})
        self.assertIn("no dieron números reales finitos", result["warnings"][0])
        json.dumps(result, allow_nan=False)

    def test_complex_value_is_non_convergence(self):
        # sqrt(−1) al evaluar F en el punto inicial.
        result = run(["sqrt(x) - y = 0", "x + y - 1 = 0"], x0=[-1, 0])
        self.assertEqual(result["failure"], {"iteration": 1, "reason": "non_finite"})
        self.assertIsNone(result["iterations"][0]["extra"]["F"])

    def test_no_real_root_does_not_converge(self):
        result = run(["x^2 + 1 = 0", "y - 1 = 0"], x0=[0.5, 0], max_iterations=20)
        self.assertFalse(result["converged"])
        self.assertTrue(result["warnings"])
        json.dumps(result, allow_nan=False)

    def test_default_initial_point_is_zero(self):
        result = run(ALGEBRAIC)
        self.assertEqual(result["x0"], [0.0, 0.0])
        self.assertEqual(result["iterations"][0]["extra"]["point"], [0.0, 0.0])


class StructureTests(SimpleTestCase):
    def test_unused_variable_is_rejected(self):
        with self.assertRaises(InputValidationError) as ctx:
            run(["x - 1 = 0", "x + 2 = 0"])
        self.assertIn("La variable y no aparece en ninguna ecuación", ctx.exception.errors[0])

    def test_equation_without_variables_is_rejected(self):
        with self.assertRaises(InputValidationError) as ctx:
            run(["x + y - 1 = 0", "2 = 3"])
        self.assertIn("La ecuación 2 no contiene ninguna de las variables", ctx.exception.errors[0])

    def test_variable_order_is_the_declared_one(self):
        # Mismas ecuaciones, variables en otro orden: cambian las columnas de J.
        result = run(ALGEBRAIC, variables=["y", "x"])
        self.assertEqual(result["jacobian"]["latex"], [["- 2 y", "3"], ["4", "2 x"]])
        y, x = result["solution"]
        self.assertAlmostEqual(3 * x - y**2 - 1, 0, places=10)


class ExampleTests(SimpleTestCase):
    def test_every_example_converges_to_a_root(self):
        for example in EXAMPLES["newton"]:
            with self.subTest(example=example["id"]):
                result = run(example["equations"], example["variables"], example["x0"],
                             example["tolerance"], example["max_iterations"])
                self.assertTrue(result["converged"])
                self.assertEqual(result["warnings"], [])
                symbols = list(make_symbols(example["variables"]).values())
                for text in example["equations"]:
                    f = sp.lambdify(symbols, parse_function(text, example["variables"])[1], "math")
                    self.assertAlmostEqual(f(*result["solution"]), 0, places=9)

    def test_known_solutions(self):
        by_id = {e["id"]: e for e in EXAMPLES["newton"]}
        chapra = by_id["newton-chapra-2x2"]
        x, y = run(chapra["equations"], chapra["variables"], chapra["x0"])["solution"]
        self.assertAlmostEqual(x, 2, places=10)
        self.assertAlmostEqual(y, 3, places=10)
        burden = by_id["newton-burden-faires-3x3"]
        x1, x2, x3 = run(burden["equations"], burden["variables"], burden["x0"])["solution"]
        self.assertAlmostEqual(x1, 0.5, places=8)
        self.assertAlmostEqual(x2, 0, places=8)
        self.assertAlmostEqual(x3, -math.pi / 6, places=8)


class NewtonEndpointTests(APITestCase):
    URL = "/api/solve/newton/"

    def _post(self, **overrides):
        payload = {"equations": ALGEBRAIC, "variables": XY, "x0": [0, 0],
                   "tolerance": 0.000001, "max_iterations": 100}
        payload.update(overrides)
        return self.client.post(self.URL, payload, format="json")

    def _flat_errors(self, response, field):
        self.assertEqual(response.status_code, 400)
        messages = response.json()[field]
        self.assertTrue(all(isinstance(m, str) for m in messages))
        return messages

    def test_endpoint_returns_iterations_and_detail(self):
        response = self._post()
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["method"], "newton")
        self.assertEqual(data["category"], "nonlinear_system")
        self.assertTrue(data["converged"])
        self.assertEqual(data["variables"], XY)
        self.assertEqual(set(data["iterations"][0]["extra"]),
                         {"point", "F", "J", "minus_F", "D", "D_i", "matrices", "delta"})
        self.assertIn("latex", data["jacobian"])

    def test_examples_by_method(self):
        response = self.client.get("/api/examples/?method=newton")
        self.assertEqual(response.status_code, 200)
        examples = response.json()
        self.assertEqual(len(examples), 3)
        for example in examples:
            payload = {k: example[k] for k in ("equations", "variables", "x0", "tolerance", "max_iterations")}
            self.assertTrue(self.client.post(self.URL, payload, format="json").json()["converged"])

    def test_x0_is_optional(self):
        payload = {"equations": ALGEBRAIC, "variables": XY}
        response = self.client.post(self.URL, payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["x0"], [0.0, 0.0])

    def test_singular_jacobian_is_200_with_warning(self):
        response = self._post(equations=["x^2 + y^2 - 4 = 0", "x - y = 0"])
        self.assertEqual(response.status_code, 200)
        self.assertIn(SINGULAR_MESSAGE, response.json()["warnings"][0])

    def test_validation_errors(self):
        self.assertIn("una variable por ecuación", self._flat_errors(self._post(variables=["x"]), "variables")[0])
        self._flat_errors(self._post(variables=["x", "x"]), "variables")
        self._flat_errors(self._post(variables=["x", "sin"]), "variables")
        self._flat_errors(self._post(x0=[0, 0, 0]), "x0")
        self._flat_errors(self._post(tolerance=-1), "tolerance")
        self.assertIn("entre 2 y 6", self._flat_errors(
            self._post(equations=["x - 1 = 0"], variables=["x"], x0=[0]), "equations")[0])
        self.assertTrue(self._flat_errors(
            self._post(equations=["x - 1 = 0", ""]), "equations")[0].startswith("Ecuación 2:"))
        self.assertTrue(self._flat_errors(
            self._post(equations=["x - 1 = 0", "y +* 2"]), "equations")[0].startswith("Ecuación 2:"))
        self.assertIn("La variable y no aparece", self._flat_errors(
            self._post(equations=["x - 1 = 0", "x + 2 = 0"]), "equations")[0])

    def test_preview_endpoint_works_for_newton_equations(self):
        response = self.client.post("/api/expressions/preview",
                                    {"equation": "y + 3*x*y^2 - 57 = 0", "variables": XY}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["latex"], "y + 3 x y^{2} - 57 = 0")
