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
