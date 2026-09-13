from django.test import SimpleTestCase

from numeric_methods.solvers import gauss_seidel, jacobi
from numeric_methods.solvers.dominance import find_dominant_ordering
from numeric_methods.solvers.validation import check_diagonal_dominance

# No es dominante en el orden dado, pero sí lo es reordenando las filas.
REORDERABLE_A = [
    [1, 5, 1],
    [10, 2, 1],
    [2, 3, 10],
]
REORDERABLE_B = [-8, 9, 22]

# Ninguna permutación de filas logra dominancia diagonal.
UNFIXABLE_A = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 10],
]
UNFIXABLE_B = [6, 15, 25]


class FindDominantOrderingTests(SimpleTestCase):
    def test_finds_ordering_for_reorderable_system(self):
        result = find_dominant_ordering(REORDERABLE_A, REORDERABLE_B)
        self.assertTrue(result.reordered)
        self.assertEqual(result.row_order, [1, 0, 2])
        self.assertEqual(result.A, [[10, 2, 1], [1, 5, 1], [2, 3, 10]])
        self.assertEqual(result.b, [9, -8, 22])

    def test_reordered_system_is_diagonally_dominant(self):
        result = find_dominant_ordering(REORDERABLE_A, REORDERABLE_B)
        self.assertTrue(check_diagonal_dominance(result.A)[0])

    def test_already_dominant_system_is_left_untouched(self):
        A = [[10, -1, 2], [-1, 11, -1], [2, -1, 10]]
        b = [6, 22, -10]
        result = find_dominant_ordering(A, b)
        self.assertFalse(result.reordered)
        self.assertIsNone(result.row_order)
        self.assertEqual(result.A, A)
        self.assertEqual(result.b, b)

    def test_system_without_valid_ordering_is_left_untouched(self):
        result = find_dominant_ordering(UNFIXABLE_A, UNFIXABLE_B)
        self.assertFalse(result.reordered)
        self.assertIsNone(result.row_order)
        self.assertEqual(result.A, UNFIXABLE_A)
        self.assertEqual(result.b, UNFIXABLE_B)

    def test_skips_brute_force_for_large_systems(self):
        n = 9
        A = [[1] * n for _ in range(n)]
        result = find_dominant_ordering(A, [1] * n)
        self.assertFalse(result.reordered)

    def test_prefers_ordering_with_largest_minimum_margin(self):
        # Ambas filas pueden ir en cualquier posición, pero una asignación deja
        # un margen mínimo mayor que la otra.
        A = [
            [20, 1, 1],
            [1, 8, 1],
            [1, 1, 30],
        ]
        b = [1, 2, 3]
        # Ya es dominante: se comprueba que no lo altera.
        self.assertFalse(find_dominant_ordering(A, b).reordered)

        shuffled_A = [A[2], A[0], A[1]]
        shuffled_b = [b[2], b[0], b[1]]
        result = find_dominant_ordering(shuffled_A, shuffled_b)
        self.assertTrue(result.reordered)
        margins = [
            abs(result.A[i][i]) - sum(abs(result.A[i][j]) for j in range(3) if j != i)
            for i in range(3)
        ]
        self.assertEqual(min(margins), 6)  # la fila [1, 8, 1] es la más ajustada


class ReorderedSystemConvergesTests(SimpleTestCase):
    def test_original_order_diverges_but_reordered_converges(self):
        diverged = jacobi.solve(
            REORDERABLE_A, REORDERABLE_B, tolerance=1e-6, max_iterations=100
        )
        self.assertFalse(diverged["converged"])

        ordering = find_dominant_ordering(REORDERABLE_A, REORDERABLE_B)
        converged = jacobi.solve(
            ordering.A, ordering.b, tolerance=1e-6, max_iterations=100
        )
        self.assertTrue(converged["converged"])

    def test_reordering_preserves_the_solution(self):
        ordering = find_dominant_ordering(REORDERABLE_A, REORDERABLE_B)
        by_jacobi = jacobi.solve(ordering.A, ordering.b, tolerance=1e-10, max_iterations=200)
        by_gauss = gauss_seidel.solve(
            ordering.A, ordering.b, tolerance=1e-10, max_iterations=200
        )

        # Ambos métodos llegan a la misma solución, y ésta satisface el sistema
        # ORIGINAL (reordenar filas no cambia el sistema de ecuaciones).
        for computed, expected in zip(by_jacobi["solution"], by_gauss["solution"]):
            self.assertAlmostEqual(computed, expected, places=6)

        for i, row in enumerate(REORDERABLE_A):
            left = sum(row[j] * by_jacobi["solution"][j] for j in range(3))
            self.assertAlmostEqual(left, REORDERABLE_B[i], places=5)
