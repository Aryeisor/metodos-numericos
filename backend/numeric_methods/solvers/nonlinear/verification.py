"""Comprobación de un sistema no lineal (Punto Fijo, Newton): la solución
reemplazada en cada ecuación original, escrita f_i = 0.

Sólo es una verificación (no forma parte de ningún método). Cada f_i se
separa en términos aditivos (mismo orden y mismas plantillas que la
sustitución de F en el paso a paso de Newton) y se evalúa cada término.

No depende de Django: puede usarse y testearse de forma aislada.
"""

import math

import sympy as sp
from sympy.functions.elementary.trigonometric import (
    InverseTrigonometricFunction,
    TrigonometricFunction,
)

from ...expressions.to_latex import substitution_template_latex
from ...expressions.to_text import expression_to_text
# Mismo criterio de «se ve entero» y de «≈ 0» que la comprobación lineal.
from ..linear.runner import CHECK_RELATIVE, DISPLAY_DECIMALS
from .common import to_real
from .derivative_steps import signed_sum_latex

# Marcador de la variable j en las plantillas de sustitución.
PLACEHOLDER = "@@{}@@"
_MODULES = ["math", "mpmath"]


def evaluate(function, x):
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


def term_template(term, placeholders):
    """Signo y plantilla (con marcadores @@j@@) de la parte sin signo de un término."""
    negative = term.could_extract_minus_sign()
    return {
        "sign": "-" if negative else "+",
        "template": substitution_template_latex(-term if negative else term, placeholders),
    }


def _is_integer(value):
    """True si el valor se ve entero con DISPLAY_DECIMALS decimales (0.9999997 → 1)."""
    return math.isfinite(value) and round(value, DISPLAY_DECIMALS) == round(value)


def _residuals(term_values):
    return [None if values is None or None in values else sum(values) + 0.0 for values in term_values]


def _max_abs(values):
    return None if not values or None in values else max(abs(v) for v in values)


def verification(functions, symbols, solution):
    """Sustitución de `solution` en cada f_i (expresiones ya evaluadas, f_i = lhs − rhs).

    Cada variable que se ve entera se sustituye como entero, así una solución
    exacta da 0 sin aproximaciones; `raw_max_residual` es el residuo con los
    valores sin redondear de la última iteración.

    Criterio de «≈ 0» (el de la comprobación lineal):
    |rᵢ| ≤ CHECK_RELATIVE · max(1, Σ|términos|).
    """
    placeholders = {s: PLACEHOLDER.format(j) for j, s in enumerate(symbols)}
    integers = [_is_integer(v) for v in solution]
    x = [float(round(v)) if is_int else v for v, is_int in zip(solution, integers)]

    terms = [f.as_ordered_terms() for f in functions]
    evaluate_terms = sp.lambdify(symbols, terms, modules=_MODULES)
    term_values = evaluate(evaluate_terms, x) or [None] * len(functions)
    raw_values = evaluate(evaluate_terms, solution) or [None] * len(functions)
    residuals = _residuals(term_values)

    # Texto plano (PDF) con los mismos marcadores @@j@@ que las plantillas LaTeX.
    text_symbols = {s: sp.Symbol(PLACEHOLDER.format(j)) for j, s in enumerate(symbols)}
    equations = []
    for f, f_terms, values, residual in zip(functions, terms, term_values, residuals):
        scale = max(1.0, sum(abs(v) for v in values)) if residual is not None else None
        equations.append({
            "function_latex": signed_sum_latex(f_terms),
            "function_text": expression_to_text(f),
            "terms": [
                {
                    **term_template(t, placeholders),
                    "text": expression_to_text(
                        (-t if t.could_extract_minus_sign() else t).xreplace(text_symbols)
                    ),
                    "value": None if values is None else values[k],
                }
                for k, t in enumerate(f_terms)
            ],
            "residual": residual,
            "is_zero": residual is not None and abs(residual) <= CHECK_RELATIVE * scale,
        })

    trig = (TrigonometricFunction, InverseTrigonometricFunction)
    return {
        "solution": x,
        "integers": integers,
        "equations": equations,
        "max_residual": _max_abs(residuals),
        "raw_max_residual": _max_abs(_residuals(raw_values)),
        "uses_trigonometry": any(
            isinstance(a, trig) for f in functions for a in f.atoms(sp.Function)
        ),
    }
