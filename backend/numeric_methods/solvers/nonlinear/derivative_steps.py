"""Paso a paso de cada derivada parcial del Jacobiano, como en el tablero.

sympy sólo da el resultado de `diff`; el desglose se arma aquí. Cada f_i se
separa en sus términos aditivos y se deriva término a término, indicando la
regla que se aplica:

- constante (el término no depende de la variable): derivada 0;
- x respecto de x: 1 (el factor constante se conserva);
- potencia de la variable, c·x^n: c·n·x^(n−1);
- potencia de una expresión, c·u^n: c·n·u^(n−1)·u′ (regla de la cadena);
- función de un argumento, c·g(u): c·g′(u)·u′ (regla de la cadena; si u es
  la propia variable, basta con g′(x));
- producto de factores que dependen de la variable: u′·v + u·v′;
- cualquier otra forma (por ejemplo, la variable en un exponente, 2^x): se
  muestra el resultado sin un paso intermedio inventado.

El resultado de cada término y de la suma sale siempre de `sympy.diff`: el
desglose es sólo presentación y nunca cambia el Jacobiano que se usa.

Si una ecuación tiene más de dos términos que no dependen de la variable, se
agrupan en una sola línea (todos derivan a 0) para no alargar el desglose.
"""

import sympy as sp

from ...expressions.to_latex import expression_to_latex
from ...expressions.to_text import expression_to_text

MAX_SEPARATE_CONSTANTS = 2

_FUNCTION_NAMES = {
    "sin": "seno", "cos": "coseno", "tan": "tangente", "asin": "arcoseno",
    "acos": "arcocoseno", "atan": "arcotangente", "sinh": "seno hiperbólico",
    "cosh": "coseno hiperbólico", "tanh": "tangente hiperbólica",
    "exp": "exponencial", "log": "logaritmo natural", "Abs": "valor absoluto",
}


def _latex(expr):
    return expression_to_latex(expr, order=None)


def _wrapped(expr):
    """LaTeX con paréntesis si el factor es una suma o empieza con signo menos."""
    latex = _latex(expr)
    if isinstance(expr, sp.Add) or expr.could_extract_minus_sign():
        return rf"\left({latex}\right)"
    return latex


def signed_sum_latex(exprs):
    """a + b − c ... con el signo de cada término (no "+ −c").

    Un sumando que es a su vez una suma (la derivada de un término puede
    serlo: −162x₂ − 16.2) no se niega en bloque: va entre paréntesis.
    """
    parts = []
    for k, expr in enumerate(exprs):
        if isinstance(expr, sp.Add):
            parts.append(_latex(expr) if k == 0 else rf"+ \left({_latex(expr)}\right)")
            continue
        negative = expr.could_extract_minus_sign()
        body = _latex(-expr if negative else expr)
        if k == 0:
            parts.append(f"- {body}" if negative else body)
        else:
            parts.append(f"{'-' if negative else '+'} {body}")
    return " ".join(parts)


def _partial(symbol):
    return rf"\frac{{\partial}}{{\partial {sp.latex(symbol)}}}"


def _with_coefficient(coefficient, inner):
    """c · (derivada del resto), omitiendo c = 1 y escribiendo −1 como signo."""
    if coefficient == 1:
        return inner
    if coefficient == -1:
        return f"- {inner}"
    return rf"{_wrapped(coefficient)} \cdot {inner}"


def _constant_note(coefficient, symbol):
    """Aclaración cuando el factor que se conserva no es un número."""
    if coefficient.is_number:
        return ""
    return f" ({expression_to_text(coefficient)} se trata como constante respecto a {symbol.name})"


def _function_name(func):
    return _FUNCTION_NAMES.get(func.__name__, func.__name__)


def term_step(term, symbol):
    """Derivada de un término: {"latex": "∂/∂x(t) = intermedio = resultado", "rule": texto}."""
    head = rf"{_partial(symbol)}\left({_latex(term)}\right)"
    result = sp.diff(term, symbol)

    if not term.has(symbol):
        rule = (
            "derivada de una constante"
            if term.is_number
            else f"no depende de {symbol.name}: se trata como constante"
        )
        return {"latex": f"{head} = 0", "rule": rule}

    coefficient, rest = term.as_independent(symbol, as_Add=False)
    note = _constant_note(coefficient, symbol)
    inner, rule = None, None

    if rest == symbol:
        inner = _latex(coefficient) if coefficient != 1 else "1"
        rule = f"la derivada de {symbol.name} respecto a {symbol.name} es 1{note}"
    elif isinstance(rest, sp.Pow) and not rest.exp.has(symbol):
        n, base = rest.exp, rest.base
        if base == symbol:
            inner = _with_coefficient(coefficient, rf"{_wrapped(n)} \cdot {_wrapped(base ** (n - 1))}")
            rule = f"regla de la potencia{note}"
        else:
            inner = _with_coefficient(
                coefficient,
                rf"{_wrapped(n)} \cdot {_wrapped(base ** (n - 1))} \cdot {_wrapped(sp.diff(base, symbol))}",
            )
            rule = f"regla de la cadena: potencia de una expresión por la derivada de la base{note}"
    elif isinstance(rest, sp.Function) and len(rest.args) == 1:
        (argument,) = rest.args
        # Real, como las variables del parser: así d|z|/dz = sign(z).
        z = sp.Dummy("z", real=True)
        outer = sp.diff(rest.func(z), z).subs(z, argument)
        name = _function_name(rest.func)
        if argument == symbol:
            inner = _with_coefficient(coefficient, _wrapped(outer))
            rule = f"derivada de la función {name}{note}"
        else:
            inner = _with_coefficient(
                coefficient, rf"{_wrapped(outer)} \cdot {_wrapped(sp.diff(argument, symbol))}"
            )
            rule = (
                f"regla de la cadena: derivada de la función {name} evaluada en su argumento, "
                f"por la derivada del argumento{note}"
            )
    elif isinstance(rest, sp.Mul):
        first, *others = rest.args
        second = sp.Mul(*others)
        product = (
            rf"{_wrapped(sp.diff(first, symbol))} \cdot {_wrapped(second)} + "
            rf"{_wrapped(first)} \cdot {_wrapped(sp.diff(second, symbol))}"
        )
        inner = _with_coefficient(
            coefficient, product if coefficient == 1 else rf"\left({product}\right)"
        )
        rule = f"regla del producto: (u·v)′ = u′·v + u·v′{note}"
    else:
        rule = "derivada directa"

    result_latex = _latex(result)
    if inner and inner != result_latex:
        return {"latex": f"{head} = {inner} = {result_latex}", "rule": rule}
    return {"latex": f"{head} = {result_latex}", "rule": rule}


def entry_steps(function, symbol, function_latex_name):
    """Desglose de ∂f/∂x: un renglón por término y la suma.

    `function_latex_name` es el nombre de la función en LaTeX (ej. "f_{1}").
    Devuelve {"terms": [{"latex", "rule"}], "sum_latex": str | None}.
    """
    terms = function.as_ordered_terms()
    constants = [t for t in terms if not t.has(symbol)]
    grouped = len(constants) > MAX_SEPARATE_CONSTANTS

    rows = [term_step(t, symbol) for t in terms if t.has(symbol) or not grouped]
    if grouped:
        rows.append({
            "latex": rf"{_partial(symbol)}\left({signed_sum_latex(constants)}\right) = 0",
            "rule": f"ninguno de estos términos depende de {symbol.name}: todos se tratan como constantes",
        })

    total = sp.diff(function, symbol)
    sum_latex = None
    if len(rows) > 1:
        derivatives = [sp.diff(t, symbol) for t in terms if t.has(symbol) or not grouped]
        if grouped:
            derivatives.append(sp.Integer(0))
        head = rf"\frac{{\partial {function_latex_name}}}{{\partial {sp.latex(symbol)}}}"
        sum_latex = f"{head} = {signed_sum_latex(derivatives)} = {_latex(total)}"
    return {"terms": rows, "sum_latex": sum_latex}
