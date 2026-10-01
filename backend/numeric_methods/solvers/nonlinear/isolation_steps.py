"""Paso a paso del despeje automático x_i = g_i(...), como en el tablero.

`sympy.solve` sólo entrega el resultado; los pasos intermedios se construyen
aquí a partir de la misma ecuación ya parseada, y se calculan una sola vez
(al armar el sistema), no en cada iteración.

Tres tipos de desglose (`kind`):

- "linear": la variable aparece con exponente 1 (a·x + r = 0, con a y r sin
  x). Se detecta con la derivada: a = ∂f/∂x no contiene x. Pasos: ecuación
  original → a·x = −r → x = −r / a → forma final.
- "power": la variable aparece en un único término c·x^n (n ≠ 1, numérico).
  Pasos: original → c·x^n = −r → x^n = −r / c → x = (−r / c)^(1/n) → final.
- "symbolic": cualquier otro caso (x dentro de una función, varios términos
  con potencias distintas...). No se inventan pasos: original → "se despejó
  con métodos simbólicos" → final.

Garantía: un desglose "linear" o "power" sólo se muestra si su resultado
coincide numéricamente con la g_i que entregó sympy (se evalúan ambas con
floats en varios puntos). Si no coinciden, se usa "symbolic". Así los pasos
nunca contradicen la función que realmente se itera.
"""

import cmath

import sympy as sp

from ...expressions.to_latex import expression_to_latex
from ...expressions.to_text import expression_to_text

# Valores de prueba para comparar el desglose con g_i (evitan 0, 1 y
# negativos, donde raíces y logaritmos tienen casos especiales).
_SAMPLES = (0.37, 1.13, 0.71, 1.59, 0.53)
_RELATIVE_TOLERANCE = 1e-9

_ROOT_NAMES = {2: "raíz cuadrada", 3: "raíz cúbica"}


def _evaluated(expr):
    """Reconstruye el árbol con evaluación normal de sympy (aplana productos y
    sumas anidados, junta coeficientes). Es barato: el parser ya acota la
    magnitud de los números y los exponentes."""
    if not expr.args:
        return expr
    return expr.func(*[_evaluated(arg) for arg in expr.args])


def _step(description, latex=None):
    return {"description": description, "latex": latex}


def _agrees(candidate, g):
    """True si `candidate` y `g` valen lo mismo en los puntos de prueba."""
    free = sorted(candidate.free_symbols | g.free_symbols, key=lambda s: s.name)
    try:
        f_candidate = sp.lambdify(free, candidate, "mpmath")
        f_g = sp.lambdify(free, g, "mpmath")
    except Exception:
        return False

    checked = 0
    for k in range(len(_SAMPLES)):
        point = [_SAMPLES[(k + j) % len(_SAMPLES)] for j in range(len(free))]
        try:
            a = complex(f_candidate(*point))
            b = complex(f_g(*point))
        except (ArithmeticError, ValueError, TypeError):
            continue
        if not (cmath.isfinite(a) and cmath.isfinite(b)):
            continue
        if abs(a - b) > _RELATIVE_TOLERANCE * (1 + abs(b)):
            return False
        checked += 1
    return checked > 0


def _term_latex(coefficient, term):
    """c·término sin evaluar (3 x, no x·3), con los casos 1 y −1."""
    if coefficient == 1:
        return expression_to_latex(term)
    if coefficient == -1:
        return f"- {expression_to_latex(term)}"
    return expression_to_latex(sp.Mul(coefficient, term, evaluate=False))


def _divided(numerator, denominator):
    """numerador / denominador para mostrar. Con un denominador entero o
    simbólico se deja la fracción sin evaluar (se ve la división); con uno
    numérico no entero (−1/3, 0.5) una fracción dentro de otra se lee mal,
    así que se muestra el cociente ya calculado."""
    if denominator.is_Number and not denominator.is_Integer:
        return numerator / denominator
    return sp.Mul(numerator, sp.Pow(denominator, -1, evaluate=False), evaluate=False)


def _already_grouped(lhs, rhs, symbol):
    """True si la ecuación ya tiene sólo términos con x a la izquierda y
    ninguno a la derecha (ej. "3x = y^2 + 1"): no hay nada que pasar de lado."""
    return not rhs.has(symbol) and _evaluated(lhs).xreplace({symbol: 0}) == 0


def _linear_steps(f, symbol, g):
    a = sp.diff(f, symbol)
    if a == 0 or a.has(symbol):
        return None
    moved = -f.xreplace({symbol: 0})  # −r: lo que queda al otro lado
    if not _agrees(moved / a, g):
        return None

    name, var = symbol.name, sp.latex(symbol)
    steps = [
        _step(
            f"Dejamos los términos con {name} en el lado izquierdo y pasamos los demás "
            "al derecho, cambiando su signo:",
            f"{_term_latex(a, symbol)} = {expression_to_latex(moved)}",
        )
    ]
    if a == -1:
        steps.append(_step("Multiplicamos ambos lados por −1:",
                           f"{var} = {expression_to_latex(-moved)}"))
    elif a != 1:
        steps.append(_step(
            f"Dividimos ambos lados entre el coeficiente de {name}, que es {expression_to_text(a)}:",
            f"{var} = {expression_to_latex(_divided(moved, a))}",
        ))
    return steps


def _root_description(exponent):
    inverse = 1 / exponent
    if exponent.is_Integer and exponent > 1:
        root = _ROOT_NAMES.get(int(exponent), f"raíz de índice {exponent}")
        return f"Aplicamos la {root} en ambos lados:"
    if inverse.is_Integer:
        return f"Elevamos ambos lados a la potencia {inverse}:"
    return f"Elevamos ambos lados a la potencia {expression_to_text(inverse)}:"


def _power_steps(f, symbol, g):
    independent, dependent = f.as_independent(symbol, as_Add=True)
    coefficient, power = dependent.as_independent(symbol, as_Add=False)
    if not (
        isinstance(power, sp.Pow)
        and power.base == symbol
        and power.exp.is_Rational
        and power.exp != 1
    ):
        return None

    exponent = power.exp
    moved = -independent
    isolated = moved / coefficient
    if not _agrees(isolated ** (1 / exponent), g):
        return None

    name, var = symbol.name, sp.latex(symbol)
    power_latex = expression_to_latex(power)
    steps = [
        _step(
            f"Dejamos el término con {name} en el lado izquierdo y pasamos los demás "
            "al derecho, cambiando su signo:",
            f"{_term_latex(coefficient, power)} = {expression_to_latex(moved)}",
        )
    ]
    if coefficient != 1:
        steps.append(_step(
            f"Dividimos ambos lados entre el coeficiente, que es {expression_to_text(coefficient)}:",
            f"{power_latex} = {expression_to_latex(_divided(moved, coefficient))}",
        ))
    base = _divided(moved, coefficient) if coefficient != 1 else moved
    steps.append(_step(
        _root_description(exponent),
        f"{var} = {expression_to_latex(sp.Pow(base, 1 / exponent, evaluate=False))}",
    ))
    return steps


def isolation_steps(lhs, rhs, symbol, g):
    """Pasos para despejar `symbol` de lhs = rhs hasta llegar a `g`.

    Devuelve {"kind": "linear" | "power" | "symbolic",
              "steps": [{"description": str, "latex": str | None}, ...]}.
    """
    name, var = symbol.name, sp.latex(symbol)
    original = f"{expression_to_latex(lhs)} = {expression_to_latex(rhs)}"
    final = f"{var} = {expression_to_latex(g)}"
    steps = [_step("Ecuación original:", original)]

    # Forma evaluada (sin expandir): agrupa términos y reparte el signo de rhs.
    f = _evaluated(sp.Add(lhs, sp.Mul(-1, rhs, evaluate=False), evaluate=False))

    if lhs == symbol and not rhs.has(symbol):
        kind, middle = "linear", []  # ya viene despejada
    else:
        kind, middle = "linear", _linear_steps(f, symbol, g)
        if middle is None:
            kind, middle = "power", _power_steps(f, symbol, g)

    if middle is None:
        steps.append(_step(
            f"{name} no aparece de forma lineal ni como una única potencia, así que no "
            "hay un desglose algebraico simple: se despejó con métodos simbólicos "
            "(sympy), que encontraron una única solución real.",
        ))
        steps.append(_step("Resultado:", final))
        return {"kind": "symbolic", "steps": steps}

    # Si la ecuación ya venía agrupada ("3x = y^2 + 1"), el primer paso sólo
    # reordenaría lo que escribió el usuario; y un paso cuya fórmula repite la
    # anterior no aporta nada.
    if middle and _already_grouped(lhs, rhs, symbol):
        middle = middle[1:]
    for step in middle:
        if step["latex"] != steps[-1]["latex"]:
            steps.append(step)

    if steps[-1]["latex"] != final:
        description = (
            "Ordenamos los términos: esta es la función de iteración."
            if len(steps) == 1
            else "Simplificamos: esta es la función de iteración que se evalúa en cada paso."
        )
        steps.append(_step(description, final))
    return {"kind": kind, "steps": steps}
