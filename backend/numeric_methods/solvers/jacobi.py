"""Método iterativo de Jacobi para sistemas de ecuaciones lineales Ax = b.

Definición formal
-----------------
Dado el sistema A x = b, se descompone A = D + R, donde D es la matriz
diagonal de A y R contiene el resto de los elementos (fuera de la diagonal).
El método de Jacobi construye la sucesión:

    x_i^(k+1) = ( b_i - sum_{j != i} a_ij * x_j^(k) ) / a_ii ,  i = 1..n

Es decir, cada componente de la nueva iteración se calcula usando
EXCLUSIVAMENTE los valores de la iteración anterior x^(k) (a diferencia de
Gauss-Seidel, que reutiliza valores ya actualizados dentro de la misma
iteración). El proceso converge, para cualquier vector inicial x^(0), si A es
diagonalmente dominante (condición suficiente, no necesaria).

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
    """Resuelve A x = b con el método de Jacobi.

    Devuelve un diccionario:
        {
            "solution": [x1, ..., xn],
            "iterations": [
                {"iteration": 1, "x": [...], "error": float}, ...
            ],
            "converged": bool,
            "iterations_used": int,
        }

    Criterio de parada: error (norma infinito entre iteraciones sucesivas)
    menor que `tolerance`, siempre que ya se hayan ejecutado al menos
    MIN_ITERATIONS (6) iteraciones. Se detiene también si se alcanza
    `max_iterations` o si la sucesión deja de ser numéricamente finita
    (indicio de divergencia).
    """
    n = validate_dimensions(A, b, x0)
    validate_diagonal_nonzero(A)

    if max_iterations < MIN_ITERATIONS:
        max_iterations = MIN_ITERATIONS

    x = list(x0) if x0 is not None else [0.0] * n
    iterations = []
    converged = False

    for k in range(1, max_iterations + 1):
        x_new = [0.0] * n
        for i in range(n):
            s = sum(A[i][j] * x[j] for j in range(n) if j != i)
            x_new[i] = (b[i] - s) / A[i][i]

        if not all(math.isfinite(v) for v in x_new):
            iterations.append({"iteration": k, "x": x_new, "error": None})
            converged = False
            break

        error = max(abs(x_new[i] - x[i]) for i in range(n))
        iterations.append({"iteration": k, "x": x_new, "error": error})

        x = x_new

        if error < tolerance and k >= MIN_ITERATIONS:
            converged = True
            break

    return {
        "solution": x,
        "iterations": iterations,
        "converged": converged,
        "iterations_used": len(iterations),
    }
