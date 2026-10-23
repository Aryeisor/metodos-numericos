"""Punto de entrada de los métodos para sistemas lineales.

Envuelve los solvers puros (`jacobi.solve`, `gauss_seidel.solve`) con el
preprocesamiento común de la familia —verificación de dominancia diagonal y
reordenamiento automático de filas— y empaqueta el resultado en un
`SolverResult`. Es la función que el registro de métodos despacha.

No depende de Django: puede usarse y testearse de forma aislada.
"""

import math

from ..base import IterationStep, SolverResult
from . import gauss_seidel, jacobi
from .dominance import OrderingResult, find_dominant_ordering
from .validation import check_diagonal_dominance

CATEGORY = "linear_system"

# Comprobación: |rᵢ| relativo a la escala de la ecuación por debajo del cual
# se muestra «≈ bᵢ» (el mismo umbral que la comprobación de Bairstow).
CHECK_RELATIVE = 1e-6
# Decimales con que el frontend muestra la solución (MAX_DECIMALS en
# utils/iterationSteps.js). Si con ellos toda la solución se ve entera, la
# comprobación se hace con esos enteros (ver _integer_solution).
DISPLAY_DECIMALS = 6


def _integer_solution(x):
    """La solución redondeada a enteros si TODAS sus componentes se ven enteras
    con DISPLAY_DECIMALS decimales (ej. 0.9999997 → 1); si no, None.

    Así una solución entera se comprueba sin aproximaciones: 4(1) = 4, no
    4(0.9999997) ≈ 3.999999. El residuo se calcula con esos enteros, así que
    si el redondeo no fuera la solución verdadera, la comprobación lo muestra.
    """
    if not all(math.isfinite(v) and round(v, DISPLAY_DECIMALS) == round(v) for v in x):
        return None
    return [float(round(v)) for v in x]


def _finite(value):
    """Valores para JSON estricto: lo no finito se reporta como None."""
    return value + 0.0 if math.isfinite(value) else None  # + 0.0: sin −0.0


def _verification(A, b, x, reordered):
    """Sustitución de la solución en cada ecuación del sistema ORIGINAL.

    Sólo es una verificación (no forma parte del método). Por cada ecuación,
    en el orden en que la escribió el usuario: los términos con coeficiente no
    nulo (aᵢⱼ, xⱼ y aᵢⱼ·xⱼ), el lado izquierdo, bᵢ y el residuo
    rᵢ = Σ aᵢⱼ·xⱼ − bᵢ, con los valores sin redondear.

    Criterio de «≈ bᵢ»: |rᵢ| ≤ CHECK_RELATIVE · max(1, |bᵢ|, Σ|aᵢⱼ·xⱼ|). La
    suma de las magnitudes de los términos es la escala natural del redondeo,
    igual que en Bairstow.

    Si la solución se ve entera, se comprueba con los enteros
    (`rounded_to_integers` indica si eso cambió algún valor calculado).
    """
    integers = _integer_solution(x)
    rounded = integers is not None and integers != list(x)
    if integers is not None:
        x = integers

    equations = []
    for i, (row, b_i) in enumerate(zip(A, b)):
        products = [(j, a, a * x[j]) for j, a in enumerate(row) if a != 0]
        lhs = sum(value for _, _, value in products)
        residual = lhs - b_i
        scale = max(1.0, abs(b_i), sum(abs(value) for _, _, value in products))
        equations.append({
            "row": i,
            "terms": [
                {"coefficient": a, "variable": f"x{j + 1}", "value": _finite(x[j]), "term": _finite(value)}
                for j, a, value in products
            ],
            "lhs": _finite(lhs),
            "b": b_i,
            "residual": _finite(residual),
            "is_zero": math.isfinite(residual) and abs(residual) <= CHECK_RELATIVE * scale,
        })

    residuals = [equation["residual"] for equation in equations]
    return {
        "solution": [_finite(value) for value in x],
        "equations": equations,
        # Norma infinito de los residuos (None si alguno no es finito).
        "max_residual": None if None in residuals else max(abs(r) for r in residuals),
        "reordered": reordered,
        "rounded_to_integers": rounded,
    }


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
            # data["A"] y data["b"] siguen siendo el sistema tal como se ingresó.
            "verification": _verification(
                data["A"], data["b"], raw["solution"], ordering.reordered
            ),
        },
    )


def solve_jacobi(data):
    return run_linear_system(jacobi.solve, "jacobi", data)


def solve_gauss_seidel(data):
    return run_linear_system(gauss_seidel.solve, "gauss-seidel", data)
