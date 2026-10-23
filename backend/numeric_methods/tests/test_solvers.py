from django.test import SimpleTestCase

from numeric_methods.examples_data import EXAMPLES
from numeric_methods.solvers.linear import gauss_seidel, jacobi
from numeric_methods.solvers.linear.runner import solve_gauss_seidel, solve_jacobi
from numeric_methods.solvers.linear.validation import (
    MatrixValidationError,
    check_diagonal_dominance,
)

# Sistema diagonalmente dominante con solución exacta conocida x = (1, 2, -1)
DOMINANT_A = [
    [10, -1, 2],
    [-1, 11, -1],
    [2, -1, 10],
]
DOMINANT_B = [6, 22, -10]
DOMINANT_SOLUTION = [1.0, 2.0, -1.0]

# Sistema NO diagonalmente dominante que diverge con ambos métodos.
DIVERGENT_A = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 10],
]
DIVERGENT_B = [6, 15, 25]


class DiagonalDominanceTests(SimpleTestCase):
    def test_dominant_matrix_detected(self):
        is_dominant, offending = check_diagonal_dominance(DOMINANT_A)
        self.assertTrue(is_dominant)
        self.assertEqual(offending, [])

    def test_non_dominant_matrix_detected(self):
        is_dominant, offending = check_diagonal_dominance(DIVERGENT_A)
        self.assertFalse(is_dominant)
        self.assertEqual(offending, [1, 2, 3])


class JacobiSolverTests(SimpleTestCase):
    def test_converges_on_diagonally_dominant_system(self):
        result = jacobi.solve(DOMINANT_A, DOMINANT_B, tolerance=1e-6, max_iterations=100)
        self.assertTrue(result["converged"])
        for computed, expected in zip(result["solution"], DOMINANT_SOLUTION):
            self.assertAlmostEqual(computed, expected, places=4)

    def test_runs_at_least_six_iterations_even_if_tolerance_reached_early(self):
        result = jacobi.solve(
            DOMINANT_A, DOMINANT_B, tolerance=10, max_iterations=100
        )
        self.assertGreaterEqual(result["iterations_used"], 6)

    def test_does_not_converge_on_non_dominant_system(self):
        result = jacobi.solve(DIVERGENT_A, DIVERGENT_B, tolerance=1e-6, max_iterations=30)
        self.assertFalse(result["converged"])

    def test_raises_on_zero_diagonal(self):
        A = [[0, 1, 1], [1, 5, 1], [1, 1, 5]]
        b = [1, 2, 3]
        with self.assertRaises(MatrixValidationError):
            jacobi.solve(A, b)

    def test_raises_on_non_square_matrix(self):
        A = [[1, 2, 3], [4, 5, 6]]
        b = [1, 2]
        with self.assertRaises(MatrixValidationError):
            jacobi.solve(A, b)

    def test_raises_on_less_than_three_variables(self):
        A = [[4, 1], [1, 3]]
        b = [1, 2]
        with self.assertRaises(MatrixValidationError):
            jacobi.solve(A, b)

    def test_iterations_are_recorded_with_error(self):
        result = jacobi.solve(DOMINANT_A, DOMINANT_B, tolerance=1e-6, max_iterations=100)
        self.assertGreater(len(result["iterations"]), 0)
        first = result["iterations"][0]
        self.assertEqual(first["iteration"], 1)
        self.assertEqual(len(first["x"]), 3)
        self.assertIsInstance(first["error"], float)


class GaussSeidelSolverTests(SimpleTestCase):
    def test_converges_on_diagonally_dominant_system(self):
        result = gauss_seidel.solve(DOMINANT_A, DOMINANT_B, tolerance=1e-6, max_iterations=100)
        self.assertTrue(result["converged"])
        for computed, expected in zip(result["solution"], DOMINANT_SOLUTION):
            self.assertAlmostEqual(computed, expected, places=4)

    def test_converges_faster_or_equal_than_jacobi(self):
        r_jacobi = jacobi.solve(DOMINANT_A, DOMINANT_B, tolerance=1e-6, max_iterations=100)
        r_gs = gauss_seidel.solve(DOMINANT_A, DOMINANT_B, tolerance=1e-6, max_iterations=100)
        self.assertLessEqual(r_gs["iterations_used"], r_jacobi["iterations_used"])

    def test_runs_at_least_six_iterations_even_if_tolerance_reached_early(self):
        result = gauss_seidel.solve(
            DOMINANT_A, DOMINANT_B, tolerance=10, max_iterations=100
        )
        self.assertGreaterEqual(result["iterations_used"], 6)

    def test_does_not_converge_on_non_dominant_system(self):
        result = gauss_seidel.solve(DIVERGENT_A, DIVERGENT_B, tolerance=1e-6, max_iterations=30)
        self.assertFalse(result["converged"])

    def test_raises_on_zero_diagonal(self):
        A = [[5, 1, 1], [1, 0, 1], [1, 1, 5]]
        b = [1, 2, 3]
        with self.assertRaises(MatrixValidationError):
            gauss_seidel.solve(A, b)

    def test_respects_custom_initial_vector(self):
        result = gauss_seidel.solve(
            DOMINANT_A, DOMINANT_B, x0=[1.0, 2.0, -1.0], tolerance=1e-6, max_iterations=100
        )
        self.assertTrue(result["converged"])
        self.assertGreaterEqual(result["iterations_used"], 6)


def _linear_data(A, b, max_iterations=100, auto_reorder=True):
    return {
        "A": A,
        "b": b,
        "x0": [0.0] * len(A),
        "tolerance": 0.000001,
        "max_iterations": max_iterations,
        "auto_reorder": auto_reorder,
    }


class LinearVerificationTests(SimpleTestCase):
    """Comprobación: la solución reemplazada en cada ecuación del sistema original."""

    # 4x + 2z = −16, 4y − 2z = −4, 2x + 2y + 5z = −20 → (−3, −2, −2).
    EXACT_A = [[4, 0, 2], [0, 4, -2], [2, 2, 5]]
    EXACT_B = [-16, -4, -20]

    def verification(self, solver, A, b, **kwargs):
        return solver(_linear_data(A, b, **kwargs)).to_dict()["verification"]

    def test_exact_system_terms_and_left_sides_with_both_methods(self):
        for solver in (solve_jacobi, solve_gauss_seidel):
            with self.subTest(solver=solver.__name__):
                check = self.verification(solver, self.EXACT_A, self.EXACT_B)
                self.assertEqual(check["solution"], [-3, -2, -2])
                self.assertEqual(
                    [[t["term"] for t in eq["terms"]] for eq in check["equations"]],
                    [[-12, -4], [-8, 4], [-6, -4, -10]],
                )
                self.assertEqual([eq["lhs"] for eq in check["equations"]], [-16, -4, -20])
                self.assertEqual([eq["residual"] for eq in check["equations"]], [0, 0, 0])
                self.assertTrue(all(eq["is_zero"] for eq in check["equations"]))
                self.assertEqual(check["max_residual"], 0)
                self.assertFalse(check["reordered"])

    def test_solution_that_looks_integer_is_checked_with_integers(self):
        # Jacobi y Gauss-Seidel llegan a ≈ (0.9999997, …), que se ve (1, 1, 1).
        A, b = [[4, 1, 1], [2, 5, 2], [1, 2, 4]], [6, 9, 7]
        for solver in (solve_jacobi, solve_gauss_seidel):
            with self.subTest(solver=solver.__name__):
                result = solver(_linear_data(A, b)).to_dict()
                check = result["verification"]
                self.assertNotEqual(result["solution"], [1, 1, 1])
                self.assertEqual(check["solution"], [1, 1, 1])
                self.assertTrue(check["rounded_to_integers"])
                self.assertEqual(
                    [[t["term"] for t in eq["terms"]] for eq in check["equations"]],
                    [[4, 1, 1], [2, 5, 2], [1, 2, 4]],
                )
                self.assertEqual([eq["lhs"] for eq in check["equations"]], b)
                self.assertEqual(check["max_residual"], 0)

    def test_decimal_solution_is_not_rounded(self):
        example = next(e for e in EXAMPLES["jacobi"] if e["id"] == "decimales-3x3")
        result = solve_jacobi(_linear_data(example["A"], example["b"])).to_dict()
        self.assertEqual(result["verification"]["solution"], result["solution"])
        self.assertFalse(result["verification"]["rounded_to_integers"])

    def test_zero_coefficient_is_left_out(self):
        check = self.verification(solve_jacobi, self.EXACT_A, self.EXACT_B)
        first = check["equations"][0]["terms"]
        self.assertEqual([t["variable"] for t in first], ["x1", "x3"])
        self.assertEqual([t["coefficient"] for t in first], [4, 2])
        self.assertEqual([t["value"] for t in first], [-3, -2])

    def test_gauss_seidel_second_exercise(self):
        # 4x − 2z = −16, −2x + 4y − z = −4, −x + y + 4z = 9 → (−3, −2, 2).
        check = self.verification(
            solve_gauss_seidel, [[4, 0, -2], [-2, 4, -1], [-1, 1, 4]], [-16, -4, 9]
        )
        self.assertEqual(check["solution"], [-3, -2, 2])
        self.assertEqual([eq["residual"] for eq in check["equations"]], [0, 0, 0])

    def test_non_integer_solution_is_approximately_b(self):
        example = next(e for e in EXAMPLES["jacobi"] if e["id"] == "decimales-3x3")
        check = self.verification(solve_jacobi, example["A"], example["b"])
        self.assertTrue(all(eq["is_zero"] for eq in check["equations"]))
        self.assertLess(check["max_residual"], 1e-5)

    def test_reordered_system_is_checked_in_original_order(self):
        A = [[1, 5, 1], [10, 2, 1], [2, 3, 10]]
        b = [-8, 9, 22]
        result = solve_gauss_seidel(_linear_data(A, b)).to_dict()
        check = result["verification"]
        self.assertTrue(result["reordered"])
        self.assertTrue(check["reordered"])
        self.assertEqual([eq["row"] for eq in check["equations"]], [0, 1, 2])
        self.assertEqual([eq["b"] for eq in check["equations"]], b)
        self.assertEqual([t["coefficient"] for t in check["equations"][0]["terms"]], [1, 5, 1])
        self.assertTrue(all(eq["is_zero"] for eq in check["equations"]))

    def test_not_converged_still_has_verification_with_residue(self):
        result = solve_jacobi(
            _linear_data(DIVERGENT_A, DIVERGENT_B, max_iterations=6, auto_reorder=False)
        ).to_dict()
        check = result["verification"]
        self.assertFalse(result["converged"])
        self.assertEqual(len(check["equations"]), 3)
        self.assertFalse(all(eq["is_zero"] for eq in check["equations"]))
        self.assertGreater(check["max_residual"], 1e-3)
