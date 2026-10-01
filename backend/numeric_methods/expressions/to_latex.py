"""Conversión de expresiones sympy a LaTeX para el componente MathFormula.

`order="none"` conserva el orden de los términos tal como los escribió el
usuario (sympy los reordena por defecto), de modo que la fórmula que se ve en
el paso a paso se reconoce como la que se ingresó.

Divisiones: con `evaluate=False`, `a/b` queda guardado como
`Mul(a, Pow(b, -1))`, y el printer estándar de sympy sólo reconoce bien las
fracciones en expresiones ya evaluadas. Sin ajuste, `1/3` se ve como
`1 \\cdot \\frac{1}{3}`, `1/x` como `1 \\frac{1}{x}` y `x*(1/3)` como
`x 1 \\cdot \\frac{1}{3}`. `_FractionPrinter` corrige únicamente eso: cómo se
dibuja un producto que contiene factores recíprocos. No cambia el modo de
evaluación ni el resto de la impresión.
"""

import sympy as sp
from sympy.printing.latex import LatexPrinter

from .parser import make_symbols


def _is_canonical(mul):
    """True si el producto ya está en la forma que sympy le daría al evaluarlo
    (por ejemplo, una derivada calculada). En ese caso se usa el printer
    estándar, para no cambiar en nada cómo se ven las expresiones evaluadas.
    """
    return sp.Mul(*mul.args) == mul


def _split_fraction(mul):
    """Separa un producto sin evaluar en (signo, numerador, denominador).

    Aplana productos anidados conservando el orden en que se escribieron;
    descarta los factores 1 explícitos; extrae los signos negativos.
    """
    sign = 1
    numerator, denominator = [], []

    def visit(factor):
        nonlocal sign
        if isinstance(factor, sp.Mul):
            for arg in factor.args:
                visit(arg)
            return
        if isinstance(factor, sp.Pow) and factor.exp.is_Number and factor.exp.is_negative:
            exponent = -factor.exp
            denominator.append(factor.base if exponent == 1 else sp.Pow(factor.base, exponent, evaluate=False))
            return
        if factor.is_Rational and not factor.is_Integer:
            p, q = factor.p, factor.q
            if p < 0:
                sign, p = -sign, -p
            if p != 1:
                numerator.append(sp.Integer(p))
            denominator.append(sp.Integer(q))
            return
        if factor.is_Number and factor.is_negative:
            sign, factor = -sign, -factor
        if factor == 1:
            return
        numerator.append(factor)

    for arg in mul.args:
        visit(arg)
    return sign, numerator, denominator


class _LogBase(sp.Function):
    r"""Sólo para imprimir: log(a)/log(b) se dibuja como \log_{b}(a) en LaTeX y
    como log(a) / log(a, b) en texto (ver to_text.py)."""

    nargs = 2

    def _latex(self, printer):
        arg, base = self.args
        return rf"\log_{{{printer._print(base)}}}{{\left({printer._print(arg)} \right)}}"

    def _sympystr(self, printer):
        arg, base = self.args
        if base == 10:
            return f"log({printer._print(arg)})"
        return f"log({printer._print(arg)}, {printer._print(base)})"


def _flatten_mul(mul):
    factors = []
    for arg in mul.args:
        factors.extend(_flatten_mul(arg) if isinstance(arg, sp.Mul) else [arg])
    return factors


def group_log_bases(mul):
    """Reescribe cada par log(a)·1/log(b), con b numérico, como _LogBase(a, b).

    Es la forma en que el parser guarda `log(x)` (base 10). Los productos sin
    evaluar pueden venir anidados (`2*log(x)` es Mul(2, Mul(log(x), 1/log(10)))),
    por eso se aplanan. Devuelve None si no hay ningún par.
    """
    factors = _flatten_mul(mul)
    logs = [i for i, f in enumerate(factors) if isinstance(f, sp.log)]
    inverses = [
        i for i, f in enumerate(factors)
        if isinstance(f, sp.Pow) and f.exp == -1
        and isinstance(f.base, sp.log) and f.base.args[0].is_Number
    ]
    pairs = list(zip(logs, inverses))
    if not pairs:
        return None
    used = {i for pair in pairs for i in pair}
    items = [f for i, f in enumerate(factors) if i not in used] + [
        _LogBase(factors[log].args[0], factors[inverse].base.args[0])
        for log, inverse in pairs
    ]
    return items[0] if len(items) == 1 else sp.Mul(*items, evaluate=False)


class _FractionPrinter(LatexPrinter):
    def _print_Mul(self, expr):
        with_base = group_log_bases(expr)
        if with_base is not None:
            return self._print(with_base)

        if _is_canonical(expr):
            return super()._print_Mul(expr)

        sign, numerator, denominator = _split_fraction(expr)
        if not denominator:
            return super()._print_Mul(expr)

        fraction = rf"\frac{{{self._print_factors(numerator)}}}{{{self._print_factors(denominator)}}}"
        return f"- {fraction}" if sign < 0 else fraction

    def _print_factors(self, factors):
        if not factors:
            return "1"
        # Coeficientes numéricos primero, como es habitual (2 y, no y 2).
        ordered = [f for f in factors if f.is_Number] + [f for f in factors if not f.is_Number]
        if len(ordered) == 1:
            return self._print(ordered[0])
        return self._print(sp.Mul(*ordered, evaluate=False))


def _latex(expr, **settings):
    # ln_notation: el logaritmo natural se ve como \ln, igual que se escribe
    # (`log` es base 10 y se ve como \log_{10}).
    return _FractionPrinter({"order": "none", "ln_notation": True, **settings}).doprint(expr)


def expression_to_latex(expr):
    return _latex(expr)


def substitution_template_latex(expr, placeholders):
    """LaTeX de `expr` con cada símbolo reemplazado por un marcador de texto.

    `placeholders` es {Symbol: "marcador"}. El frontend reemplaza cada marcador
    por el valor numérico que corresponda en cada iteración, sin que haga falta
    sustituir ni imprimir nada en el backend por iteración. Los productos se
    escriben con `\\cdot` porque, una vez sustituidos, `x y` se leería como un
    solo número ("0.5 0.3").
    """
    return _latex(expr, symbol_names=placeholders, mul_symbol="dot")


def matrix_to_latex(matrix):
    return _latex(sp.Matrix(matrix))


def function_to_latex(name, variables, expr):
    """Ej.: ("f1", ["x", "y"], x**2 + x*y - 10) -> "f_{1}(x, y) = x^{2} + x y - 10"."""
    symbols = list(make_symbols(variables).values())
    args = ", ".join(sp.latex(s) for s in symbols)
    head = sp.latex(sp.Symbol(name)) if name else "f"
    return f"{head}({args}) = {expression_to_latex(expr)}"


def equation_to_latex(name, lhs, rhs, variables):
    """LaTeX de una ecuación tal como la devuelve `parser.parse_equation`.

    Muestra lo que se escribió, sin interpretarlo para ningún método:
    "f1(x, y) = ..." como función, "lhs = rhs" con sus dos lados y una
    expresión suelta tal cual.
    """
    if name:
        return function_to_latex(name, variables, lhs)
    if rhs is None:
        return expression_to_latex(lhs)
    return f"{expression_to_latex(lhs)} = {expression_to_latex(rhs)}"
