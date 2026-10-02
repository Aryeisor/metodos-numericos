"""Normalización de expresiones ya parseadas.

El parser conserva la forma escrita (`evaluate=False`): "3x - 1" queda como
Add(Mul(3, x), Mul(-1, 1)), con productos y sumas anidados. Para presentar
fórmulas derivadas (despejes, la función f = lhs − rhs) conviene la forma que
sympy les daría al evaluarlas.
"""


def evaluate_tree(expr):
    """Reconstruye el árbol con la evaluación normal de sympy (aplana sumas y
    productos anidados, junta coeficientes, reparte signos). Es barato: el
    parser ya acota la magnitud de los números y los exponentes."""
    if not expr.args:
        return expr
    return expr.func(*[evaluate_tree(arg) for arg in expr.args])
