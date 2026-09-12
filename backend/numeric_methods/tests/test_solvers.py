from django.test import SimpleTestCase

from numeric_methods.solvers import gauss_seidel, jacobi
from numeric_methods.solvers.validation import (
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
