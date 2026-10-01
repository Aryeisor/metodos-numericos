"""Punto de entrada de los métodos para sistemas lineales.

Envuelve los solvers puros (`jacobi.solve`, `gauss_seidel.solve`) con el
preprocesamiento común de la familia —verificación de dominancia diagonal y
reordenamiento automático de filas— y empaqueta el resultado en un
`SolverResult`. Es la función que el registro de métodos despacha.

No depende de Django: puede usarse y testearse de forma aislada.
"""

from ..base import IterationStep, SolverResult
from . import gauss_seidel, jacobi
from .dominance import OrderingResult, find_dominant_ordering
from .validation import check_diagonal_dominance

CATEGORY = "linear_system"


def run_linear_system(solve, method, data):
    """Resuelve un sistema A x = b con `solve` a partir de datos ya validados.

    Lanza MatrixValidationError si el sistema no cumple las restricciones.
    """
    A = data["A"]
    b = data["b"]
    x0 = data.get("x0")
    tolerance = data["tolerance"]
    max_iterations = data["max_iterations"]
    auto_reorder = data["auto_reorder"]

    is_dominant, offending_rows = check_diagonal_dominance(A)

    # Preprocesamiento: si no es dominante, se intenta reordenar las filas.
    # Sólo se reordenan ecuaciones (filas de A junto con b); las columnas no
    # se tocan, así que x0 y el vector solución siguen indexados igual.
    ordering = OrderingResult(False, None, A, b)
    if not is_dominant and auto_reorder:
        ordering = find_dominant_ordering(A, b)
        if ordering.reordered:
            A, b = ordering.A, ordering.b
            is_dominant, offending_rows = check_diagonal_dominance(A)

    warnings = []
    if not is_dominant:
        warnings.append(
            "La matriz no es diagonalmente dominante en la(s) fila(s) "
            f"{offending_rows}. Esta es una condición suficiente (no necesaria) "
            "de convergencia: el método puede converger o no."
        )

    raw = solve(A, b, x0=x0, tolerance=tolerance, max_iterations=max_iterations)

    if not raw["converged"]:
        warnings.append(
            f"El método no alcanzó la tolerancia solicitada ({tolerance}) "
            f"dentro de {raw['iterations_used']} iteraciones."
        )

    return SolverResult(
        method=method,
        category=CATEGORY,
        converged=raw["converged"],
        iterations=[
            IterationStep(iteration=row["iteration"], x=row["x"], error=row["error"])
            for row in raw["iterations"]
        ],
        solution=raw["solution"],
        variables=[f"x{i + 1}" for i in range(len(A))],
        warnings=warnings,
        meta={
            "n": len(A),
            "is_diagonally_dominant": is_dominant,
            # A y b tal como se usaron realmente en el cálculo (ya reordenadas
            # si hubo reordenamiento), para que el paso a paso del frontend
            # coincida con las iteraciones devueltas.
            "A": A,
            "b": b,
            "reordered": ordering.reordered,
            "row_order": ordering.row_order,
        },
    )


def solve_jacobi(data):
    return run_linear_system(jacobi.solve, "jacobi", data)


def solve_gauss_seidel(data):
    return run_linear_system(gauss_seidel.solve, "gauss-seidel", data)
