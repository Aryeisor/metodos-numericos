"""Formato propio de la diferenciación numérica (las dos excepciones a la
regla general de 6 decimales, ver README):

1. El paso h y los puntos x₀ ± h definen el cálculo: se muestran exactos.
   Su decimal exacto es Decimal(str(h₀)) / 2^(k−1); con 12 decimales o menos
   se escribe tal cual, y con más, como h₀/2^(k−1) (≈ 6 decimales).
2. En el paso a paso, f(·) y la resta del numerador llevan
   d = mín(15, 6 + ⌈−log₁₀ h⌉) decimales si h < 1 (6 si h ≥ 1), para que el
   cociente visible sea coherente con los valores que se ven.

No depende de Django: puede usarse y testearse de forma aislada.
"""

import math
from decimal import Context, Decimal

DISPLAY_DECIMALS = 6
MAX_EXACT_DECIMALS = 12
MAX_STEP_DECIMALS = 15
# Holgada: h₀ con 17 cifras entre 2^29 sigue siendo exacto.
_CONTEXT = Context(prec=100)


def fixed(value, decimals=DISPLAY_DECIMALS):
    """Decimal fijo sin ceros finales ni notación científica; −0 → 0."""
    text = f"{value:.{decimals}f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


def exact(value):
    """Decimal exacto de un dato escrito por el usuario (1.8, 0.1...)."""
    return Decimal(repr(float(value)))


def _decimals(number):
    return max(0, -number.normalize(_CONTEXT).as_tuple().exponent)


def _plain(number):
    text = format(number.normalize(_CONTEXT), "f")
    return "0" if text in ("-0", "") else text


def step_size(h0, k):
    """h_k = h₀ / 2^(k−1): su decimal exacto y cómo se muestra."""
    number = _CONTEXT.divide(exact(h0), Decimal(2) ** (k - 1))
    shown = _shown(number)
    if shown is not None:
        return number, shown
    base = _shown(exact(h0))
    base_text = base["text"] if base else fixed(h0)
    if k == 1:
        return number, {"exact": False, "text": base_text, "latex": base_text, "approx": fixed(h0)}
    return number, {
        "exact": False,
        "text": f"{base_text}/2^{k - 1}",
        "latex": f"{base_text}/2^{{{k - 1}}}",
        "approx": fixed(float(number)),
    }


def _shown(number):
    if _decimals(number) > MAX_EXACT_DECIMALS:
        return None
    text = _plain(number)
    return {"exact": True, "text": text, "latex": text, "approx": None}


def point(x0, offset, h_number, h_shown):
    """x₀ + o·h exacto; si tiene más de 12 decimales, «x₀ + h» con ≈."""
    number = exact(x0) + offset * h_number
    shown = _shown(number)
    if shown is not None:
        return shown
    x0_shown = _shown(exact(x0))
    base = x0_shown["text"] if x0_shown else fixed(x0)
    if offset == 0:
        return {"exact": False, "text": base, "latex": base, "approx": fixed(x0)}
    sign = "+" if offset > 0 else "-"
    factor = "" if abs(offset) == 1 else f"{abs(offset)}·"
    factor_latex = "" if abs(offset) == 1 else rf"{abs(offset)} \cdot "
    return {
        "exact": False,
        "text": f"{base} {sign} {factor}{h_shown['text']}",
        "latex": f"{base} {sign} {factor_latex}{h_shown['latex']}",
        "approx": fixed(float(number)),
    }


def decimal(number):
    """Un decimal exacto: tal cual con 12 decimales o menos; si no, a 6 (≈)."""
    shown = _shown(number)
    if shown is not None:
        return shown
    text = fixed(float(number))
    return {"exact": False, "text": text, "latex": text, "approx": text}


def data_value(value):
    """Un dato escrito por el usuario (x₀, xᵢ)."""
    return decimal(exact(value))


def product(weight, shown):
    """wᵢ·f(xᵢ) exacto con el valor visible del paso a paso: «-44.334336»."""
    return _plain(weight * Decimal(shown))


def scaled_step(h_shown, factor):
    """factor·h exacto (el denominador «0.2»); None si h no se muestra exacto."""
    return _plain(factor * Decimal(h_shown["text"])) if h_shown["exact"] else None


def step_decimals(h_number):
    """d = mín(15, 6 + ⌈−log₁₀ h⌉) si h < 1; 6 si h ≥ 1."""
    if h_number >= 1:
        return DISPLAY_DECIMALS
    return min(MAX_STEP_DECIMALS, DISPLAY_DECIMALS + math.ceil(-h_number.log10(_CONTEXT)))


def coherent_step(values, weights, denominator, quotient):
    """Decimales del paso a paso y los textos de f(·) y del numerador.

    Parte de `step_decimals` y, si el cociente de los valores mostrados no
    coincide a 6 decimales con D, agrega decimales (hasta 15) hasta que
    coincida. `denominator` es el decimal exacto de q·h.
    """
    target = fixed(quotient)
    decimals = step_decimals(denominator)
    while True:
        shown = [fixed(v, decimals) for v in values]
        numerator = sum((w * Decimal(s) for w, s in zip(weights, shown)), Decimal(0))
        if decimals >= MAX_STEP_DECIMALS or fixed(_CONTEXT.divide(numerator, denominator)) == target:
            return {"decimals": decimals, "values": shown, "numerator": _plain(numerator)}
        decimals += 1
