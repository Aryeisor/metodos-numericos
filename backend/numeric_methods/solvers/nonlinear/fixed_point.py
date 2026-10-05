"""Método de Punto Fijo con actualización secuencial para sistemas no lineales.

Definición formal
-----------------
Dado un sistema F(x) = 0 de n ecuaciones f_i(x_1, ..., x_n) = 0, cada
ecuación i se reescribe despejando su propia variable x_i:

    x_i = g_i(x_1, ..., x_{i-1}, x_{i+1}, ..., x_n)

y se itera a partir de x^(0). La actualización es secuencial (el equivalente
no lineal de Gauss-Seidel): al calcular x_i^(k+1) se usan los valores YA
ACTUALIZADOS x_1..x_{i-1} de la iteración actual y los valores x_{i+1}..x_n
de la iteración anterior:

    x_i^(k+1) = g_i(x_1^(k+1), ..., x_{i-1}^(k+1), x_{i+1}^(k), ..., x_n^(k))

Si las g_i son una contracción cerca de la solución (por ejemplo, si la norma
infinito de su jacobiana es menor que 1), el método converge para un x^(0)
suficientemente cercano.

Despeje automático
------------------
g_i se obtiene una sola vez, al inicio, con `sympy.solve(f_i, x_i)`, y sólo se
acepta si hay exactamente un despeje real. Las ecuaciones sin despeje, con
despejes sólo complejos o con varios despejes reales se rechazan con un
mensaje que explica el motivo; no hay forma de ingresar g_i a mano.

`sympy.solve` puede tardar segundos en ecuaciones de grado alto (despejar x de
`x^1000 - y = 0` tarda unos 10 s y devuelve casi mil raíces). Por eso, antes de
llamarlo, se estima el grado de cada ecuación en su variable recorriendo el
árbol, sin expandir nada, y se rechaza si supera MAX_SOLVE_DEGREE.

Evaluación numérica
-------------------
Cada g_i se convierte con `lambdify` en una función de floats (módulo `math`;
`mpmath` sólo para funciones que `math` no tiene, como LambertW). Nunca se
sustituyen valores exactos ni se simplifica en cada iteración: además de ser
lento, con enteros exactos una expresión corta puede colgar el proceso.

Si en alguna iteración un valor sale complejo, infinito, NaN o fuera del
dominio de una función (raíz de un negativo, logaritmo de cero), el método se
detiene y se reporta como no convergente.

No depende de Django: puede usarse y testearse de forma aislada.
"""

import math
from dataclasses import dataclass

import sympy as sp

from ...expressions.normalize import estimate_degree  # noqa: F401  (se reexporta)
from ...expressions.parser import ExpressionError, make_symbols, parse_equation
from ...expressions.to_latex import expression_to_latex, substitution_template_latex
from ...expressions.to_text import expression_to_text
from ..base import IterationStep, SolverResult
from ..validation import DEFAULT_MAX_ITERATIONS, DEFAULT_TOLERANCE, MIN_ITERATIONS
from .common import (  # noqa: F401  (MIN/MAX_EQUATIONS se reexportan)
    CATEGORY,
    MAX_EQUATIONS,
    MIN_EQUATIONS,
    NonlinearValidationError,
    to_real,
)
from .isolation_steps import isolation_steps

METHOD = "punto-fijo"

# Grado máximo de una ecuación en la variable que se despeja. Hasta cuártica
# sympy despeja en menos de un segundo aun con coeficientes simbólicos.
MAX_SOLVE_DEGREE = 4

# Marcador de cada variable en la plantilla de sustitución que se envía al
# frontend (ver `substitution_template_latex`).
PLACEHOLDER = "@@{}@@"


@dataclass
class FixedPointFunction:
    """Despeje x_i = g_i(...) de la ecuación i."""

    index: int
    name: str
    symbol: sp.Symbol
    equation: sp.Expr
    # LaTeX de la ecuación tal como se escribió (lhs = rhs).
    equation_latex: str
    g: sp.Expr
    dependencies: list
    evaluate: object
    # Paso a paso del despeje (ver isolation_steps.py).
    isolation: dict


def _is_real_candidate(solution):
    # Con variables reales, sympy ya descarta los despejes que puede probar
    # complejos; los que no puede decidir (is_real None) y no contienen la
    # unidad imaginaria se aceptan como reales.
    return (
        solution.is_real is not False
        and solution.is_finite is not False
        and not solution.has(sp.I)
    )


def isolate(equation, symbol, index):
    """Despeja `symbol` de `equation` = 0. Devuelve g o lanza NonlinearValidationError.

    `index` es el número de ecuación (1, 2, ...) para los mensajes.
    """
    name = symbol.name
    cannot = (
        f"No fue posible despejar {name} de la ecuación {index} de forma automática."
    )
    rewrite = "Reescribe la ecuación de otra forma."

    degree = estimate_degree(equation, symbol)
    if degree > MAX_SOLVE_DEGREE:
        degree_text = f"{degree:g}" if math.isfinite(degree) else "muy alto"
        raise NonlinearValidationError(
            f"{cannot} {name} aparece con grado {degree_text} y el máximo admitido "
            f"para el despeje automático es {MAX_SOLVE_DEGREE}. {rewrite}"
        )

    try:
        solutions = sp.solve(equation, symbol, rational=False) if degree else []
    except Exception:  # NotImplementedError y otros: sympy no sabe despejarla
        solutions = []

    real = [s for s in solutions if _is_real_candidate(s)]
    if not real:
        raise NonlinearValidationError(f"{cannot} {rewrite}")
    if len(real) > 1:
        options = "; ".join(f"{name} = {expression_to_text(s)}" for s in real)
        raise NonlinearValidationError(
            f"La ecuación {index} admite {len(real)} despejes reales de {name} "
            f"({options}), así que el despeje automático es ambiguo. Reescribe la "
            f"ecuación para que {name} tenga un único despeje, por ejemplo con "
            f"{name} sola en el lado izquierdo: {name} = ..."
        )
    return real[0]


def build_fixed_point_system(equations, variables):
    """Parsea las ecuaciones y obtiene cada g_i despejando la variable i.

    Lanza NonlinearValidationError con un mensaje por cada ecuación que no se
    pueda parsear o despejar.
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

    functions, errors = [], []
    for i, (text, symbol) in enumerate(zip(equations, symbols)):
        try:
            _, lhs, rhs = parse_equation(text, variables)
            if rhs is None:
                equation, rhs = lhs, sp.Integer(0)
            else:
                equation = sp.Add(lhs, sp.Mul(-1, rhs, evaluate=False), evaluate=False)
            g = isolate(equation, symbol, i + 1)
        except ExpressionError as exc:
            errors.append(f"Ecuación {i + 1}: {exc}")
            continue
        except NonlinearValidationError as exc:
            errors.extend(exc.errors)
            continue
        functions.append(
            FixedPointFunction(
                index=i,
                name=symbol.name,
                symbol=symbol,
                equation=equation,
                equation_latex=f"{expression_to_latex(lhs)} = {expression_to_latex(rhs)}",
                g=g,
                dependencies=[j for j, s in enumerate(symbols) if g.has(s)],
                # Una sola función de floats para todo el método; el orden de
                # los argumentos es el de las variables.
                evaluate=sp.lambdify(symbols, g, modules=["math", "mpmath"]),
                isolation=isolation_steps(lhs, rhs, symbol, g),
            )
        )

    if errors:
        raise NonlinearValidationError(errors)
    return functions


def iterate(functions, x0, tolerance=DEFAULT_TOLERANCE, max_iterations=DEFAULT_MAX_ITERATIONS):
    """Itera x_i = g_i(...) con actualización secuencial.

    Devuelve {solution, iterations, converged, iterations_used, failure}.
    Cada iteración guarda en `inputs[i]` los valores de las dependencias de
    g_i con los que se evaluó (en el orden de `dependencies`).
    `failure` es None, o {iteration, variable_index} si un valor salió no real
    o no finito; en ese caso esa iteración queda registrada con los valores
    que sí se calcularon (None en los demás) y error None.
    """
    n = len(functions)
    if max_iterations < MIN_ITERATIONS:
        max_iterations = MIN_ITERATIONS

    x = list(x0)
    iterations = []
    converged = False
    failure = None

    for k in range(1, max_iterations + 1):
        x_old = list(x)
        inputs = []

        for i, function in enumerate(functions):
            # x ya contiene x_1..x_{i-1} de esta iteración y x_{i+1}..x_n de la
            # anterior: eso es exactamente la actualización secuencial.
            inputs.append([x[j] for j in function.dependencies])
            try:
                value = to_real(function.evaluate(*x))
            except (ArithmeticError, ValueError, TypeError):
                value = None
            if value is None:
                failure = {"iteration": k, "variable_index": i}
                break
            x[i] = value

        if failure:
            row = x[: failure["variable_index"]] + [None] * (n - failure["variable_index"])
            iterations.append({"iteration": k, "x": row, "error": None, "inputs": inputs})
            x = x_old
            break

        error = max(abs(x[i] - x_old[i]) for i in range(n))
        iterations.append({"iteration": k, "x": list(x), "error": error, "inputs": inputs})

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


def solve_fixed_point(data):
    """Punto de entrada del registro: datos ya validados -> SolverResult."""
    equations = data["equations"]
    variables = data["variables"]
    x0 = data.get("x0") or [0.0] * len(variables)
    tolerance = data["tolerance"]
    max_iterations = data["max_iterations"]

    functions = build_fixed_point_system(equations, variables)
    symbols = [f.symbol for f in functions]
    placeholders = {s: PLACEHOLDER.format(j) for j, s in enumerate(symbols)}

    raw = iterate(functions, x0, tolerance=tolerance, max_iterations=max_iterations)

    warnings = []
    failure = raw["failure"]
    if failure:
        function = functions[failure["variable_index"]]
        warnings.append(
            f"En la iteración {failure['iteration']}, {function.name} = "
            f"g_{function.index + 1}(...) no dio un número real finito (resultó "
            "complejo, infinito o fuera del dominio de una función). El método se "
            "detuvo sin converger; prueba con otro punto inicial o reescribe las "
            "ecuaciones."
        )
    elif not raw["converged"]:
        warnings.append(
            f"El método no alcanzó la tolerancia solicitada ({tolerance}) "
            f"dentro de {raw['iterations_used']} iteraciones."
        )

    return SolverResult(
        method=METHOD,
        category=CATEGORY,
        converged=raw["converged"],
        iterations=[
            IterationStep(
                iteration=row["iteration"],
                x=row["x"],
                error=row["error"],
                extra={"inputs": row["inputs"]},
            )
            for row in raw["iterations"]
        ],
        solution=raw["solution"],
        variables=list(variables),
        warnings=warnings,
        meta={
            "n": len(functions),
            "x0": list(x0),
            "variables_latex": [sp.latex(s) for s in symbols],
            "equations": [
                {
                    "variable": f.name,
                    # La ecuación tal como se ingresó.
                    "equation_latex": f.equation_latex,
                    # x_i = g_i(...), el despeje que se itera.
                    "g_latex": expression_to_latex(f.g),
                    # El mismo despeje en texto plano (para el PDF).
                    "g_text": expression_to_text(f.g),
                    # g_i con marcadores @@j@@ en lugar de cada variable j.
                    "g_template": substitution_template_latex(f.g, placeholders),
                    "dependencies": f.dependencies,
                    # Cómo se llegó de la ecuación a g_i: {kind, steps}.
                    "isolation": f.isolation,
                }
                for f in functions
            ],
            "failure": failure,
        },
    )
