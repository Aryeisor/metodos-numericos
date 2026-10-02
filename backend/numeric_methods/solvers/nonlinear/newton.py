"""Método de Newton para sistemas de ecuaciones no lineales F(x) = 0.

Definición formal
-----------------
Dado F(x) = (f_1(x), ..., f_n(x)) y su matriz jacobiana J(x), con
J[i][j] = ∂f_i/∂x_j, cada iteración:

  1. Evalúa F(x^(k)) y J(x^(k)) en el punto actual.
  2. Resuelve el sistema lineal  J(x^(k)) · Δx = −F(x^(k)).
  3. Actualiza  x^(k+1) = x^(k) + Δx.

A diferencia de Punto Fijo no se despeja nada: las ecuaciones se usan tal
como se escribieron (lhs = rhs equivale a f = lhs − rhs = 0) y las variables
las declara el usuario, en orden, por separado de las ecuaciones.

El sistema lineal se resuelve con la regla de Cramer (linalg/cramer.py),
como se hace a mano en el curso: D = det J, D_i = det J_i (J con la columna i
reemplazada por −F) y Δx_i = D_i / D.

Evaluación numérica
-------------------
F y J se derivan y convierten con `lambdify` una sola vez; en cada iteración
se evalúan con floats (nunca se sustituye simbólicamente). Si un valor sale
complejo, infinito o fuera de dominio, o si el jacobiano es singular, el
método se detiene y se reporta como no convergente.

Criterio de parada: ‖Δx‖∞ = max_i |Δx_i| < tolerancia, con al menos
MIN_ITERATIONS iteraciones, o al llegar a max_iterations.

No depende de Django: puede usarse y testearse de forma aislada.
"""

from dataclasses import dataclass

import sympy as sp

from ...expressions.differentiate import jacobian
from ...expressions.normalize import evaluate_tree
from ...expressions.parser import ExpressionError, make_symbols, parse_equation
from ...expressions.to_latex import expression_to_latex
from ...expressions.to_text import expression_to_text
from ...linalg.cramer import SingularMatrixError, cramer
from ..base import IterationStep, SolverResult
from ..validation import DEFAULT_MAX_ITERATIONS, DEFAULT_TOLERANCE, MIN_ITERATIONS
from .common import CATEGORY, NonlinearValidationError, to_real

METHOD = "newton"
_MODULES = ["math", "mpmath"]


@dataclass
class NewtonSystem:
    names: list
    symbols: list
    # f_i = lhs − rhs, la función cuyo cero se busca.
    functions: list
    equations_latex: list
    jacobian: sp.Matrix
    evaluate_f: object
    evaluate_j: object


def structure_errors(functions, symbols):
    """Errores que harían singular al jacobiano en cualquier punto: una
    variable que no aparece en ninguna ecuación (columna de ceros) o una
    ecuación sin variables (fila de ceros)."""
    errors = []
    for i, f in enumerate(functions):
        if not any(f.has(s) for s in symbols):
            errors.append(
                f"La ecuación {i + 1} no contiene ninguna de las variables declaradas: "
                "su fila del Jacobiano sería de ceros."
            )
    for s in symbols:
        if not any(f.has(s) for f in functions):
            errors.append(
                f"La variable {s.name} no aparece en ninguna ecuación: su columna del "
                "Jacobiano sería de ceros y el sistema no tendría solución única."
            )
    return errors


def build_newton_system(equations, variables):
    """Parsea las ecuaciones y construye F y su jacobiano simbólico.

    Lanza NonlinearValidationError con un mensaje por cada problema.
    """
    try:
        symbols = list(make_symbols(variables).values())
    except ExpressionError as exc:
        raise NonlinearValidationError(str(exc)) from exc
    if len(equations) != len(symbols):
        raise NonlinearValidationError(
            "Debe haber tantas ecuaciones como variables "
            f"({len(equations)} ecuaciones, {len(symbols)} variables)."
        )

    functions, equations_latex, errors = [], [], []
    for i, text in enumerate(equations):
        try:
            _, lhs, rhs = parse_equation(text, variables)
        except ExpressionError as exc:
            errors.append(f"Ecuación {i + 1}: {exc}")
            continue
        # f = lhs − rhs en la forma que sympy le da al evaluarla: reparte el
        # signo de rhs y junta coeficientes ("x - (y + 1)" → "x − y − 1").
        if rhs is None:
            functions.append(evaluate_tree(lhs))
            equations_latex.append(f"{expression_to_latex(lhs)} = 0")
        else:
            functions.append(evaluate_tree(sp.Add(lhs, sp.Mul(-1, rhs, evaluate=False), evaluate=False)))
            equations_latex.append(f"{expression_to_latex(lhs)} = {expression_to_latex(rhs)}")
    if errors:
        raise NonlinearValidationError(errors)

    errors = structure_errors(functions, symbols)
    if errors:
        raise NonlinearValidationError(errors)

    J = jacobian(functions, symbols)
    return NewtonSystem(
        names=list(variables),
        symbols=symbols,
        functions=functions,
        equations_latex=equations_latex,
        jacobian=J,
        # Listas (no Matrix): así lambdify devuelve floats y no una matriz de mpmath.
        evaluate_f=sp.lambdify(symbols, functions, modules=_MODULES),
        evaluate_j=sp.lambdify(symbols, J.tolist(), modules=_MODULES),
    )


def _evaluate(function, x):
    """Evalúa y convierte a floats; None en cada valor no real o no finito
    (o en todos, si la evaluación misma falla: raíz de negativo con math,
    log(0), desbordamiento...)."""
    try:
        values = function(*x)
    except (ArithmeticError, ValueError, TypeError):
        return None
    if values and isinstance(values[0], list):
        return [[to_real(v) for v in row] for row in values]
    return [to_real(v) for v in values]


def _has_none(values):
    if values is None:
        return True
    return any(_has_none(v) if isinstance(v, list) else v is None for v in values)


def iterate(system, x0, tolerance=DEFAULT_TOLERANCE, max_iterations=DEFAULT_MAX_ITERATIONS):
    """Itera Newton. Devuelve {solution, iterations, converged, iterations_used, failure}.

    Cada iteración k guarda en `extra` todo el cálculo hecho en el punto
    x^(k−1): F, J, −F, D, cada D_i con su matriz, cada Δx_i. `failure` es
    None, o {iteration, reason: "non_finite" | "singular"}.
    """
    n = len(system.symbols)
    if max_iterations < MIN_ITERATIONS:
        max_iterations = MIN_ITERATIONS

    x = [float(v) for v in x0]
    iterations = []
    converged = False
    failure = None

    for k in range(1, max_iterations + 1):
        extra = {"point": list(x)}

        F = _evaluate(system.evaluate_f, x)
        J = _evaluate(system.evaluate_j, x)
        extra["F"] = F
        extra["J"] = J
        if _has_none(F) or _has_none(J):
            failure = {"iteration": k, "reason": "non_finite"}
            iterations.append({"iteration": k, "x": [None] * n, "error": None, "extra": extra})
            break

        minus_f = [-v + 0.0 for v in F]  # + 0.0: −(0.0) daría −0.0
        extra["minus_F"] = minus_f
        try:
            step = cramer(J, minus_f)
        except SingularMatrixError as exc:
            extra["D"] = exc.determinant
            failure = {"iteration": k, "reason": "singular"}
            iterations.append({"iteration": k, "x": [None] * n, "error": None, "extra": extra})
            break

        delta = step.solution
        new_x = [xi + di for xi, di in zip(x, delta)]
        extra.update({
            "D": step.determinant,
            "D_i": step.column_determinants,
            "matrices": step.column_matrices,
            "delta": [to_real(d) for d in delta],
        })
        if any(to_real(v) is None for v in delta + new_x):
            failure = {"iteration": k, "reason": "non_finite"}
            iterations.append({"iteration": k, "x": [to_real(v) for v in new_x], "error": None, "extra": extra})
            break

        error = max(abs(d) for d in delta)
        x = new_x
        iterations.append({"iteration": k, "x": list(x), "error": error, "extra": extra})

        if error < tolerance and k >= MIN_ITERATIONS:
            converged = True
            break

    return {
        "solution": x,
        "iterations": iterations,
        "converged": converged,
        "iterations_used": len(iterations),
        "failure": failure,
    }


def _failure_warning(failure):
    k = failure["iteration"]
    point = f"x^({k - 1})"
    if failure["reason"] == "singular":
        return (
            f"El Jacobiano es singular en la iteración {k}, no se puede continuar: "
            f"su determinante en {point} es (prácticamente) cero, así que el sistema "
            "J·Δx = −F no tiene solución única. Prueba con otro punto inicial."
        )
    return (
        f"En la iteración {k}, F, el Jacobiano o el paso Δx no dieron números reales "
        "finitos (resultó complejo, infinito o fuera del dominio de una función). El método "
        "se detuvo sin converger; prueba con otro punto inicial."
    )


def solve_newton(data):
    """Punto de entrada del registro: datos ya validados -> SolverResult."""
    equations = data["equations"]
    variables = data["variables"]
    x0 = data.get("x0") or [0.0] * len(variables)
    tolerance = data["tolerance"]
    max_iterations = data["max_iterations"]

    system = build_newton_system(equations, variables)
    raw = iterate(system, x0, tolerance=tolerance, max_iterations=max_iterations)

    warnings = []
    if raw["failure"]:
        warnings.append(_failure_warning(raw["failure"]))
    elif not raw["converged"]:
        warnings.append(
            f"El método no alcanzó la tolerancia solicitada ({tolerance}) "
            f"dentro de {raw['iterations_used']} iteraciones."
        )

    J = system.jacobian
    return SolverResult(
        method=METHOD,
        category=CATEGORY,
        converged=raw["converged"],
        iterations=[
            IterationStep(iteration=row["iteration"], x=row["x"], error=row["error"], extra=row["extra"])
            for row in raw["iterations"]
        ],
        solution=raw["solution"],
        variables=list(variables),
        warnings=warnings,
        meta={
            "n": len(system.symbols),
            "x0": [float(v) for v in x0],
            "variables_latex": [sp.latex(s) for s in system.symbols],
            "equations": [
                {
                    # La ecuación tal como se ingresó y la función f_i = lhs − rhs.
                    "equation_latex": equation_latex,
                    "function_latex": expression_to_latex(f, order=None),
                    "function_text": expression_to_text(f),
                }
                for equation_latex, f in zip(system.equations_latex, system.functions)
            ],
            # Jacobiano simbólico, calculado una sola vez: J[i][j] = ∂f_i/∂x_j.
            "jacobian": {
                "latex": [[expression_to_latex(v, order=None) for v in row] for row in J.tolist()],
                "text": [[expression_to_text(v) for v in row] for row in J.tolist()],
            },
            "failure": raw["failure"],
        },
    )
