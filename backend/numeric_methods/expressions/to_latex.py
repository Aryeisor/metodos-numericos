"""Conversión de expresiones sympy a LaTeX para el componente MathFormula.

`order="none"` conserva el orden de los términos tal como los escribió el
usuario (sympy los reordena por defecto), de modo que la fórmula que se ve en
el paso a paso se reconoce como la que se ingresó.
"""

import sympy as sp

from .parser import make_symbols


def expression_to_latex(expr):
    return sp.latex(expr, order="none")


def matrix_to_latex(matrix):
    return sp.latex(sp.Matrix(matrix), order="none")


def function_to_latex(name, variables, expr):
    """Ej.: ("f1", ["x", "y"], x**2 + x*y - 10) -> "f_{1}(x, y) = x^{2} + x y - 10"."""
    symbols = list(make_symbols(variables).values())
    args = ", ".join(sp.latex(s) for s in symbols)
    head = sp.latex(sp.Symbol(name)) if name else "f"
    return f"{head}({args}) = {expression_to_latex(expr)}"
