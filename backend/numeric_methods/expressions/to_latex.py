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


class _FractionPrinter(LatexPrinter):
    def _print_Mul(self, expr):
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
    return _FractionPrinter({"order": "none", **settings}).doprint(expr)


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
