"""Reglas de integración compuestas, como datos.

Una regla compuesta con n segmentos iguales, h = (b − a)/n y xᵢ = a + i·h es

  I ≈ factor · h · Σ wᵢ · f(xᵢ)

con w₀ = wₙ = `ends` y los pesos interiores repitiendo `interior`:
  trapecio      factor 1/2, pesos 1, 2, 2, …, 2, 1
  Simpson 1/3   factor 1/3, pesos 1, 4, 2, 4, …, 4, 1  (n par)
  Simpson 3/8   factor 3/8, pesos 1, 3, 3, 2, …, 3, 1  (n múltiplo de 3)

El solver no conoce ninguna regla en particular: agregar Simpson es declarar
su CompositeRule aquí.

No depende de Django: puede usarse y testearse de forma aislada.
"""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class CompositeRule:
    key: str
    name: str
    factor: Fraction
    ends: int
    interior: tuple
    # n debe ser múltiplo de esto (2 en Simpson 1/3, 3 en Simpson 3/8).
    segments_multiple: int
    formula_latex: str
    formula_text: str
    # Cota (b − a)·h^p/c · máx|f⁽ᵈ⁾|: p = order, d = bound_derivative, c = bound_divisor.
    order: int
    bound_derivative: int
    bound_divisor: int
    bound_latex: str
    # Sólo Simpson (la respuesta del trapecio no los usa): error de la regla
    # simple, (b − a)^(p+1)/simple_divisor · f⁽ᵈ⁾(ξ), el Eₐ de Chapra y la
    # figura que forma cada grupo de segments_multiple segmentos.
    simple_divisor: int = 0
    error_latex: str = ""
    simple_error_latex: str = ""
    approx_latex: str = ""
    piece: str = ""

    def weight(self, i, n):
        if i in (0, n):
            return self.ends
        return self.interior[(i - 1) % len(self.interior)]

    def weights(self, n):
        return [self.weight(i, n) for i in range(n + 1)]

    @property
    def expected_ratio(self):
        return 0.5 ** self.order


TRAPEZOID = CompositeRule(
    key="trapecio",
    name="Trapecio",
    factor=Fraction(1, 2),
    ends=1,
    interior=(2,),
    segments_multiple=1,
    formula_latex=r"I \approx \frac{h}{2}\Big[f(x_0) + 2\sum_{i=1}^{n-1} f(x_i) + f(x_n)\Big]",
    formula_text="I ~ (h/2)·[f(x0) + 2·Suma f(xi) + f(xn)]",
    order=2,
    bound_derivative=2,
    bound_divisor=12,
    bound_latex=r"|E_t| \le \frac{(b - a)\,h^{2}}{12}\, M_2,\quad M_2 = \max_{x \in [a,\, b]} \left|f''(x)\right|",
)

_M4 = r"M_4 = \max_{x \in [a,\, b]} \left|f^{(4)}(x)\right|"
_MEAN4 = r"\bar{f}^{(4)} = \frac{f'''(b) - f'''(a)}{b - a}"

SIMPSON_13 = CompositeRule(
    key="simpson13",
    name="Simpson 1/3",
    factor=Fraction(1, 3),
    ends=1,
    interior=(4, 2),
    segments_multiple=2,
    formula_latex=(r"I \approx \frac{h}{3}\Big[f(x_0) + 4\sum_{i\ \text{impar}} f(x_i)"
                   r" + 2\sum_{i\ \text{par}} f(x_i) + f(x_n)\Big]"),
    formula_text="I ~ (h/3)·[f(x0) + 4·Suma f(xi impar) + 2·Suma f(xi par) + f(xn)]",
    order=4,
    bound_derivative=4,
    bound_divisor=180,
    bound_latex=rf"|E_t| \le \frac{{(b - a)\,h^{{4}}}}{{180}}\, M_4,\quad {_M4}",
    simple_divisor=2880,
    error_latex=r"E_t = -\frac{(b - a)\,h^{4}}{180}\, f^{(4)}(\xi)",
    simple_error_latex=r"E_t = -\frac{(b - a)^{5}}{2880}\, f^{(4)}(\xi)\quad (n = 2)",
    approx_latex=rf"E_a = -\frac{{(b - a)\,h^{{4}}}}{{180}}\,\bar{{f}}^{{(4)}},\quad {_MEAN4}",
    piece="parábola",
)

SIMPSON_38 = CompositeRule(
    key="simpson38",
    name="Simpson 3/8",
    factor=Fraction(3, 8),
    ends=1,
    interior=(3, 3, 2),
    segments_multiple=3,
    formula_latex=(r"I \approx \frac{3h}{8}\Big[f(x_0) + 3\sum_{i\ \text{no múltiplo de 3}} f(x_i)"
                   r" + 2\sum_{i\ \text{múltiplo de 3}} f(x_i) + f(x_n)\Big]"),
    formula_text="I ~ (3h/8)·[f(x0) + 3·Suma f(xi, i no múltiplo de 3) + 2·Suma f(xi, i múltiplo de 3) + f(xn)]",
    order=4,
    bound_derivative=4,
    bound_divisor=80,
    bound_latex=rf"|E_t| \le \frac{{(b - a)\,h^{{4}}}}{{80}}\, M_4,\quad {_M4}",
    simple_divisor=6480,
    error_latex=r"E_t = -\frac{(b - a)\,h^{4}}{80}\, f^{(4)}(\xi)",
    simple_error_latex=r"E_t = -\frac{(b - a)^{5}}{6480}\, f^{(4)}(\xi)\quad (n = 3)",
    approx_latex=rf"E_a = -\frac{{(b - a)\,h^{{4}}}}{{80}}\,\bar{{f}}^{{(4)}},\quad {_MEAN4}",
    piece="cúbica",
)


def apply(rule, values, h):
    """factor · h · Σ wᵢ·f(xᵢ) con los valores f(x₀), …, f(xₙ)."""
    n = len(values) - 1
    return float(rule.factor) * h * sum(w * v for w, v in zip(rule.weights(n), values))


def public_rule(rule):
    return {
        "key": rule.key,
        "name": rule.name,
        "factor": [rule.factor.numerator, rule.factor.denominator],
        "ends": rule.ends,
        "interior": list(rule.interior),
        "formula_latex": rule.formula_latex,
        "formula_text": rule.formula_text,
        "bound_latex": rule.bound_latex,
        "order": rule.order,
        "expected_ratio": rule.expected_ratio,
    }
