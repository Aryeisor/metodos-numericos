"""Fórmulas de diferencias finitas para aproximar f'(x₀).

Cada fórmula es un dato: los nodos x₀ + o·h con su peso w, el divisor q de
h, el orden del error y su cota. El solver no conoce ninguna fórmula en
particular, así que agregar la de 3 o la de 5 puntos es agregar una entrada
aquí (y a `CHOICES`).

  D(h) = Σ wᵢ · f(x₀ + oᵢ·h) / (q·h)
  |error| ≤ c · h^p · máx |f⁽ⁿ⁾(ξ)|,  ξ en [x₀ + mín(o)·h, x₀ + máx(o)·h]

No depende de Django: puede usarse y testearse de forma aislada.
"""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Formula:
    key: str
    name: str
    symbol_latex: str
    # ((oᵢ, wᵢ), ...) en el orden en que se escriben en el numerador.
    nodes: tuple
    # p: el error es O(h^p); al reducir h a la mitad se divide entre 2^p.
    order: int
    # n y c de la cota c · h^p · máx |f⁽ⁿ⁾|.
    bound_derivative: int
    bound_coefficient: Fraction
    formula_latex: str
    formula_text: str
    bound_latex: str
    divisor: int = 1

    @property
    def expected_ratio(self):
        return 0.5 ** self.order


FORWARD = Formula(
    key="forward",
    name="Progresiva",
    symbol_latex="D^{+}",
    nodes=((1, 1), (0, -1)),
    order=1,
    bound_derivative=2,
    bound_coefficient=Fraction(1, 2),
    formula_latex=r"D^{+}(h) = \frac{f(x_0 + h) - f(x_0)}{h}",
    formula_text="D+(h) = [f(x0 + h) - f(x0)] / h",
    bound_latex=r"|E| \le \frac{h}{2} \max_{\xi \in [x_0,\, x_0 + h]} \left|f''(\xi)\right|",
)

BACKWARD = Formula(
    key="backward",
    name="Regresiva",
    symbol_latex="D^{-}",
    nodes=((0, 1), (-1, -1)),
    order=1,
    bound_derivative=2,
    bound_coefficient=Fraction(1, 2),
    formula_latex=r"D^{-}(h) = \frac{f(x_0) - f(x_0 - h)}{h}",
    formula_text="D-(h) = [f(x0) - f(x0 - h)] / h",
    bound_latex=r"|E| \le \frac{h}{2} \max_{\xi \in [x_0 - h,\, x_0]} \left|f''(\xi)\right|",
)

FORMULAS = {formula.key: formula for formula in (FORWARD, BACKWARD)}

# Opción del selector «Fórmula» -> fórmulas que se calculan.
CHOICES = {
    "forward": (FORWARD,),
    "backward": (BACKWARD,),
    "both": (FORWARD, BACKWARD),
}


def public_formula(formula):
    """Lo que el frontend necesita para dibujar la fórmula y su cota."""
    return {
        "key": formula.key,
        "name": formula.name,
        "symbol_latex": formula.symbol_latex,
        "formula_latex": formula.formula_latex,
        "formula_text": formula.formula_text,
        "bound_latex": formula.bound_latex,
        "order": formula.order,
        "expected_ratio": formula.expected_ratio,
        "bound_derivative": formula.bound_derivative,
        "bound_coefficient": [formula.bound_coefficient.numerator, formula.bound_coefficient.denominator],
        "nodes": [list(node) for node in formula.nodes],
        "divisor": formula.divisor,
    }
