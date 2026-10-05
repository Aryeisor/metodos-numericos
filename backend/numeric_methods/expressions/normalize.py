"""Normalización y análisis de expresiones ya parseadas.

El parser conserva la forma escrita (`evaluate=False`): "3x - 1" queda como
Add(Mul(3, x), Mul(-1, 1)), con productos y sumas anidados. Para presentar
fórmulas derivadas (despejes, la función f = lhs − rhs) conviene la forma que
sympy les daría al evaluarlas.
"""

import sympy as sp


def evaluate_tree(expr):
    """Reconstruye el árbol con la evaluación normal de sympy (aplana sumas y
    productos anidados, junta coeficientes, reparte signos). Es barato: el
    parser ya acota la magnitud de los números y los exponentes."""
    if not expr.args:
        return expr
    return expr.func(*[evaluate_tree(arg) for arg in expr.args])


def estimate_degree(expr, symbol):
    """Cota superior del grado de `expr` en `symbol`, sin expandir.

    Suma en productos, máximo en sumas, multiplica en potencias de exponente
    numérico. Dentro de funciones (sin, exp, ...) cuenta el grado de sus
    argumentos, de modo que `exp(x^1000)` también se detecta.
    """
    if not expr.has(symbol):
        return 0
    if expr == symbol:
        return 1
    if isinstance(expr, sp.Add):
        return max(estimate_degree(arg, symbol) for arg in expr.args)
    if isinstance(expr, sp.Mul):
        return sum(estimate_degree(arg, symbol) for arg in expr.args)
    if isinstance(expr, sp.Pow) and expr.exp.is_Number:
        return estimate_degree(expr.base, symbol) * abs(float(expr.exp))
    return max(1, *(estimate_degree(arg, symbol) for arg in expr.args))
