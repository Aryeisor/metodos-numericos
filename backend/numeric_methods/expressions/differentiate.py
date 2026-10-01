"""Derivación simbólica: derivadas parciales, gradiente y jacobiano.

Las variables pueden pasarse como nombres (str) o como símbolos de sympy; se
construyen con las mismas suposiciones que `parser.make_symbols`, así que
coinciden con los símbolos de las expresiones parseadas.
"""

import sympy as sp

from .parser import make_symbols


def _as_symbols(variables):
    if all(isinstance(v, sp.Symbol) for v in variables):
        return list(variables)
    return list(make_symbols(variables).values())


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
