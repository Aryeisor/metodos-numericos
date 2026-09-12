"""Método iterativo de Gauss-Seidel para sistemas de ecuaciones lineales Ax = b.

Definición formal
-----------------
Al igual que Jacobi, se parte de A x = b. La diferencia es que, al calcular
x_i^(k+1), se usan los valores YA ACTUALIZADOS de la iteración actual para
las componentes j < i, y los valores de la iteración anterior para j > i:

    x_i^(k+1) = ( b_i - sum_{j<i} a_ij * x_j^(k+1) - sum_{j>i} a_ij * x_j^(k) ) / a_ii

Esto suele acelerar la convergencia respecto a Jacobi. Al igual que Jacobi,
converge (para cualquier x^(0)) si A es diagonalmente dominante (condición
suficiente, no necesaria).

Esta implementación es pura (sin dependencias de Django) y por lo tanto
fácilmente testeable.
"""

import math

from .validation import (
    DEFAULT_MAX_ITERATIONS,
    MIN_ITERATIONS,
    validate_diagonal_nonzero,
    validate_dimensions,
)


def solve(A, b, x0=None, tolerance=1e-6, max_iterations=DEFAULT_MAX_ITERATIONS):
    """Resuelve A x = b con el método de Gauss-Seidel.

    Misma forma de retorno y criterio de parada que `jacobi.solve`. La
    actualización se hace in-place sobre el vector x, de modo que al calcular
    x_i ya se usan los valores nuevos x_1..x_{i-1} calculados en la misma
    iteración.
    """
    n = validate_dimensions(A, b, x0)
    validate_diagonal_nonzero(A)

    if max_iterations < MIN_ITERATIONS:
        max_iterations = MIN_ITERATIONS

    x = list(x0) if x0 is not None else [0.0] * n
    iterations = []
    converged = False

    for k in range(1, max_iterations + 1):
        x_old = list(x)

        for i in range(n):
            s = sum(A[i][j] * x[j] for j in range(n) if j != i)
            x[i] = (b[i] - s) / A[i][i]

        if not all(math.isfinite(v) for v in x):
            iterations.append({"iteration": k, "x": list(x), "error": None})
            converged = False
            break

        error = max(abs(x[i] - x_old[i]) for i in range(n))
        iterations.append({"iteration": k, "x": list(x), "error": error})

        if error < tolerance and k >= MIN_ITERATIONS:
            converged = True
            break

    return {
        "solution": x,
        "iterations": iterations,
        "converged": converged,
        "iterations_used": len(iterations),
    }
