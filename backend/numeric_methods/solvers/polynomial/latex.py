"""LaTeX de polinomios y factores a partir de coeficientes float.

Los números se escriben con el mismo criterio que el frontend
(utils/iterationSteps.formatNumber): hasta 6 decimales sin ceros sobrantes, y
notación científica desde 10⁷.
"""

MAX_DECIMALS = 6
SCIENTIFIC_THRESHOLD = 1e7


def format_number(value):
    """Texto de un número, como formatNumber del frontend."""
    if value == 0:
        return "0"
    if abs(value) >= SCIENTIFIC_THRESHOLD:
        mantissa, exponent = f"{value:.2e}".split("e")
        return f"{mantissa} \\times 10^{{{int(exponent)}}}"
    text = f"{value:.{MAX_DECIMALS}f}".rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


def _power(power):
    if power == 0:
        return ""
    if power == 1:
        return "x"
    return f"x^{{{power}}}"


def polynomial_latex(coefficients):
    """aₙxⁿ + … + a₀ (descendente), omitiendo los términos nulos y los
    coeficientes 1 de las potencias de x."""
    degree = len(coefficients) - 1
    parts = []
    for p, value in enumerate(coefficients):
        text = format_number(abs(value))
        if text == "0":
            continue
        power = degree - p
        body = _power(power)
        if body and text == "1":
            term = body
        else:
            term = f"{text} {body}".strip()
        sign = "-" if value < 0 else "+"
        if not parts:
            parts.append(f"- {term}" if sign == "-" else term)
        else:
            parts.append(f"{sign} {term}")
    return " ".join(parts) if parts else "0"


def quadratic_factor_latex(r, s):
    """x² − r·x − s con los valores sustituidos y los signos resueltos."""
    return polynomial_latex([1.0, -r, -s])


def linear_factor_latex(root):
    """x − p."""
    return polynomial_latex([1.0, -root])


def factorization_latex(leading, zero_roots, factors):
    """aₙ · xᵏ · (x² − r₁x − s₁) · … · (x − p)."""
    parts = [_power(zero_roots)] if zero_roots else []
    parts += [f"\\left({factor}\\right)" for factor in factors]
    body = " ".join(parts) or "1"
    leading_text = format_number(leading)
    if leading_text == "1":
        return body
    if leading_text == "-1":
        return f"-{body}"
    return f"{leading_text} {body}"
