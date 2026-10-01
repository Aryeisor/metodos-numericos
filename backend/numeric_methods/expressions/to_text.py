"""Expresiones sympy como texto plano, con la sintaxis que acepta el parser.

Se usa donde no hay LaTeX: mensajes de error (por ejemplo, los despejes
posibles de una ecuación ambigua) y el PDF. El texto se puede volver a
escribir tal cual en un campo de ecuación:

  - potencias con `^` (no `**`),
  - logaritmo natural como `ln(x)` (sympy lo escribe `log(x)`, que en el
    parser es base 10),
  - log(a)/log(10), la forma en que se guarda `log(a)`, de nuevo como `log(a)`,
  - valor absoluto como `abs(x)` (sympy escribe `Abs(x)`).
"""

from sympy.printing.str import StrPrinter

from .to_latex import group_log_bases


class _UserTextPrinter(StrPrinter):
    def _print_log(self, expr):
        return f"ln({self._print(expr.args[0])})"

    def _print_Abs(self, expr):
        return f"abs({self._print(expr.args[0])})"

    def _print_Mul(self, expr):
        grouped = group_log_bases(expr)
        if grouped is not None:
            return self._print(grouped)
        return super()._print_Mul(expr)


def expression_to_text(expr):
    return _UserTextPrinter().doprint(expr).replace("**", "^")
