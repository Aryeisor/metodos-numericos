"""Búsqueda de un reordenamiento de filas que logre dominancia diagonal.

Reordenar filas de A junto con sus términos independientes de b no altera el
sistema de ecuaciones ni su solución: es la misma información escrita en otro
orden. Las columnas (y por tanto el orden de las variables, la solución y el
vector inicial x0) no se tocan.

Es un paso de preprocesamiento: no modifica el algoritmo de Jacobi ni el de
Gauss-Seidel.
"""

from itertools import permutations
from typing import NamedTuple

from .validation import check_diagonal_dominance

# Con n > 8 la búsqueda exhaustiva (n! permutaciones) deja de ser viable, así
# que se conserva el comportamiento actual sin intentar reordenar.
MAX_BRUTE_FORCE_SIZE = 8


class OrderingResult(NamedTuple):
    """Resultado de la búsqueda.

    reordered: True sólo si se encontró y aplicó una permutación distinta.
    row_order: row_order[i] = índice de la fila original ubicada en la posición i.
    A, b: el sistema ya reordenado (o el original si no hubo reordenamiento).
    """

    reordered: bool
    row_order: list | None
    A: list
    b: list


def _dominance_margins(A):
    """margins[r][i] = |a_ri| - sum_{j!=i} |a_rj| si la fila r se ubica en la posición i.

    Equivale a 2*|a_ri| - sum_j |a_rj|. Un margen > 0 es exactamente la misma
    condición de dominancia estricta que verifica `check_diagonal_dominance`.
    """
    n = len(A)
    margins = []
    for row in A:
        total = sum(abs(value) for value in row)
        margins.append([2 * abs(row[i]) - total for i in range(n)])
    return margins


def find_dominant_ordering(A, b, max_size=MAX_BRUTE_FORCE_SIZE):
    """Busca una permutación de filas que haga a A diagonalmente dominante.

    Si el sistema ya es dominante en el orden dado, o si no existe ninguna
    permutación válida, devuelve el sistema intacto con reordered=False.

    Entre varias permutaciones válidas se elige la que maximiza el margen
    mínimo de dominancia, porque suele traducirse en convergencia más rápida.
    """
    n = len(A)

    is_dominant, _ = check_diagonal_dominance(A)
    if is_dominant:
        return OrderingResult(False, None, A, b)

    if n > max_size:
        return OrderingResult(False, None, A, b)

    margins = _dominance_margins(A)

    # Si alguna posición no admite ninguna fila, no existe permutación válida.
    for position in range(n):
        if not any(margins[row][position] > 0 for row in range(n)):
            return OrderingResult(False, None, A, b)

    best_order = None
    best_margin = 0.0

    for order in permutations(range(n)):
        min_margin = min(margins[row][position] for position, row in enumerate(order))
        if min_margin > best_margin:
            best_margin = min_margin
            best_order = order

    if best_order is None:
        return OrderingResult(False, None, A, b)

    row_order = list(best_order)
    reordered_A = [list(A[row]) for row in row_order]
    reordered_b = [b[row] for row in row_order]

    return OrderingResult(True, row_order, reordered_A, reordered_b)
