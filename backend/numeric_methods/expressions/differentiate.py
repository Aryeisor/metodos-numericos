"""Derivación simbólica: derivadas parciales, gradiente y jacobiano.

Las variables pueden pasarse como nombres (str) o como símbolos de sympy; se
construyen con las mismas suposiciones que `parser.make_symbols`, así que
coinciden con los símbolos de las expresiones parseadas.
"""

import sympy as sp

from .parser import make_symbols


def _as_symbols(variables):
    """Símbolos con las mismas suposiciones que los del parser (real=True).

    Todo se normaliza por nombre. Antes, un Symbol("x") sin `real=True` se
    usaba tal cual y sympy lo trataba como una variable distinta de la x del
    parser: la derivada salía 0 sin ningún aviso. Mezclar nombres y símbolos
    también fallaba con un mensaje engañoso.
    """
    names = [v.name if isinstance(v, sp.Symbol) else v for v in variables]
    return list(make_symbols(names).values())


def derivative(expr, variable):
    """Derivada parcial de `expr` respecto de `variable`."""
    (symbol,) = _as_symbols([variable])
    return sp.diff(expr, symbol)


def gradient(expr, variables):
    """Vector de derivadas parciales [∂expr/∂v1, ..., ∂expr/∂vn]."""
    return [sp.diff(expr, symbol) for symbol in _as_symbols(variables)]


def jacobian(exprs, variables):
    """Matriz jacobiana J[i][j] = ∂f_i/∂x_j de un sistema de funciones."""
    return sp.Matrix(list(exprs)).jacobian(_as_symbols(variables))
