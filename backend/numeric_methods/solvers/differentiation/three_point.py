"""Fórmula de 3 puntos para aproximar f'(x₀): punto medio y extremos.

Usa el mismo motor que las diferencias progresiva y regresiva
(finite_differences.py) con sus propias fórmulas (formulas.py) y su regla de
redondeo, y agrega lo propio de este método:

- en el paso a paso, cada producto cᵢ·f(xᵢ) y el denominador factor·h;
- la comparación con la progresiva y la regresiva con el h₀ de la fila 1 y
  el h de la última fila;
- las identidades de la comprobación: punto medio = (D⁺ + D⁻)/2 y extremo =
  2·D(h) − D(2h) (extrapolación de Richardson);
- en el modo tabla, datos igualmente espaciados (lo valida el serializer),
  cada fórmula donde hay datos y la columna «Recomendada».

No depende de Django: puede usarse y testearse de forma aislada.
"""

from . import display
from .finite_differences import MACHINE_EPSILON, _evaluate, _function_mode, _table_points, build_result
from .formulas import (
    BACKWARD,
    BACKWARD_ENDPOINT,
    FORWARD,
    FORWARD_ENDPOINT,
    MIDPOINT,
    THREE_POINT,
    THREE_POINT_CHOICES,
)

METHOD = "tres-puntos"
DEFAULT_TOLERANCE = 1e-6
MIN_POINTS = 3
# Identidad cumplida: |valor − D| ≤ IDENTITY_RELATIVE · máx(1, |valor|).
IDENTITY_RELATIVE = 1e-9
ROUNDING_TEXT = {
    "function": "R = 2ε·Σ|cᵢ|·(|f(xᵢ)| + |xᵢ·f′(xᵢ)|) / (factor·h)",
    "table": "R = 2ε·Σ|cᵢ·f(xᵢ)| / (factor·h)",
}


def rounding(formula, values, h, function=None, xs=None):
    """R = 2ε·Σ|cᵢ·f(xᵢ)| / (factor·h): redondeo de la suma.

    En modo función se suma el redondeo de cada punto xᵢ = x₀ + dᵢ·h, que en
    binario no es exacto: mueve f(xᵢ) en |f′(xᵢ)|·ε|xᵢ|. Sin ese término, en
    una cúbica (error real = cota) el error real supera cota + R en ~10⁻¹³.
    """
    total = sum(abs(w * v) for (_, w), v in zip(formula.nodes, values))
    if function is not None:
        for (_, w), x in zip(formula.nodes, xs):
            slope = _evaluate(function.evaluators[1], x)
            total += abs(w) * abs(x) * (abs(slope) if slope is not None else 0.0)
    return 2 * MACHINE_EPSILON * total / (formula.divisor * h)


def _decorate(row, h_shown, formula):
    """Productos cᵢ·f(xᵢ) y denominador del paso a paso (sólo en este método,
    para no cambiar la respuesta de diferencias)."""
    row["products_display"] = [display.product(p["weight"], p["f_display"]) for p in row["points"]]
    row["denominator_display"] = display.scaled_step(h_shown, formula.divisor)


# --- Identidades ---------------------------------------------------------------

def _identity(formula, f, h, D):
    """Punto medio = (D⁺ + D⁻)/2; extremo = 2·D(h) − D(2h).

    `f` da f(x₀ + o·h) por desplazamiento o; None si falta un valor.
    """
    if formula is MIDPOINT:
        needed = (-1, 0, 1)
    else:
        s = 1 if formula is FORWARD_ENDPOINT else -1
        needed = (0, s, 2 * s)
    if any(f.get(o) is None for o in needed):
        return None
    if formula is MIDPOINT:
        forward, backward = (f[1] - f[0]) / h, (f[0] - f[-1]) / h
        value = (forward + backward) / 2
        item = {"kind": "average", "forward": forward, "backward": backward}
    else:
        base = s * (f[s] - f[0]) / h
        double = s * (f[2 * s] - f[0]) / (2 * h)
        value = 2 * base - double
        item = {"kind": "richardson", "direction": "+" if s > 0 else "-", "base": base, "double": double}
    return {
        "key": formula.key,
        "name": formula.name,
        **item,
        "value": value,
        "D": D,
        "ok": abs(value - D) <= IDENTITY_RELATIVE * max(1.0, abs(value)),
    }


# --- Comparación con diferencias -----------------------------------------------

_SUPERSCRIPTS = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def _error_text(error):
    """6 decimales; si a 6 decimales sería 0 sin serlo, 1.4×10⁻¹⁰."""
    if error == 0 or error >= 5e-7:
        return display.fixed(error)
    mantissa, exponent = f"{error:.1e}".split("e")
    return f"{mantissa}×10{str(int(exponent)).translate(_SUPERSCRIPTS)}"


def _times(theirs, mine, name):
    """«25 veces menor que el de la progresiva»."""
    if theirs == 0:
        return f"la {name} también es exacta"
    ratio = theirs / mine
    if ratio >= 1:
        return f"{display.fixed(ratio, 0 if ratio >= 10 else 1)} veces menor que el de la {name}"
    return f"{display.fixed(1 / ratio, 0 if 1 / ratio >= 10 else 1)} veces mayor que el de la {name}"


def _difference_at(function, formula, x0, h, exact):
    values = [function(x0 + o * h) for o, _ in formula.nodes]
    if None in values:
        return None, None
    D = sum(w * v for (_, w), v in zip(formula.nodes, values)) / (formula.divisor * h) + 0.0
    return D, None if exact is None else abs(D - exact)


def _join(parts):
    """«A y B», «A, B y C»."""
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " y " + parts[-1]


# (fórmula, campo de la respuesta, nombre al presentarla, nombre al compararla).
DIFFERENCE_REFERENCES = (
    (FORWARD, "forward", "diferencia progresiva", "progresiva"),
    (BACKWARD, "backward", "regresiva", "regresiva"),
)


def _comparison(function, formulas, x0, iterations, exact, references=DIFFERENCE_REFERENCES,
                method_label="la fórmula de 3 puntos"):
    """Qué darían las fórmulas de `references` con el h₀ de la fila 1 y con el
    h de la última fila, y cuántas veces menor es el error de cada fórmula."""
    steps = iterations[:1] + iterations[1:][-1:]
    lines = []
    for step in steps:
        h_shown = step.extra["h"]
        h = h_shown["value"]
        h_text = h_shown["text"] if h_shown["exact"] else f"{h_shown['text']} ≈ {h_shown['approx']}"
        diffs = {f.key: _difference_at(function, f, x0, h, exact) for f, *_ in references}

        def said(formula, label, verb):
            D, error = diffs[formula.key]
            if D is None:
                return f"la {label} no se puede calcular (f no está definida en sus puntos)"
            return f"la {label}{verb} {display.fixed(D)}" + ("" if error is None else f" (error {_error_text(error)})")

        text = f"Con h = {h_text}, " + _join([
            said(f, label, " daría" if i == 0 else "") for i, (f, _, label, _) in enumerate(references)
        ]) + "."
        mine = []
        for formula in formulas:
            row = step.extra[formula.key]
            part = f"{formula.name.lower()} {display.fixed(row['D'])}"
            if row["real_error"] == 0:
                part += " (error 0: exacta)"
            elif row["real_error"] is not None:
                versus = [
                    _times(diffs[f.key][1], row["real_error"], name)
                    for f, _, _, name in references
                    if diffs[f.key][1] is not None
                ]
                part += f" (error {_error_text(row['real_error'])}" + (f": {_join(versus)})" if versus else ")")
            mine.append(part)
        text += f" Con {method_label}: " + "; ".join(mine) + "."
        lines.append({
            "k": step.iteration,
            "h": h_shown,
            **{field: {"D": diffs[f.key][0], "real_error": diffs[f.key][1]} for f, field, *_ in references},
            "text": text,
        })
    return lines


# --- Modos ---------------------------------------------------------------------

def _function(data):
    function, formulas, converged, iterations, warnings, meta = _function_mode(
        data, THREE_POINT_CHOICES, rounding, derivative_orders=(2,)
    )
    for step in iterations:
        for formula in formulas:
            _decorate(step.extra[formula.key], step.extra["h"], formula)

    x0, identities = data["x0"], []
    if iterations:
        first = iterations[0].extra
        h = first["h"]["value"]
        f = {o: function(x0 + o * h) for o in range(-2, 3)}
        identities = [
            item for formula in formulas
            if (item := _identity(formula, f, h, first[formula.key]["D"])) is not None
        ]
    meta["verification"]["identities"] = identities
    meta["comparison"] = _comparison(function, formulas, x0, iterations, meta["exact"]) if iterations else []
    meta["rounding_text"] = ROUNDING_TEXT["function"]
    return function, formulas, converged, iterations, warnings, meta


def _recommended(extra, i):
    """El punto medio donde existe; en el primer punto, el extremo hacia
    adelante; en el último, el extremo hacia atrás."""
    formula = MIDPOINT if extra[MIDPOINT.key] else FORWARD_ENDPOINT if i == 0 else BACKWARD_ENDPOINT
    return {"key": formula.key, "name": formula.name, "D": extra[formula.key]["D"]}


def _table(data):
    # Se calculan las tres fórmulas siempre: la columna «Recomendada» las usa.
    function, formulas, xs, iterations, warnings, verification = _table_points(
        data, THREE_POINT_CHOICES, THREE_POINT, rounding, derivative_orders=(2,)
    )
    ys = [float(y) for _, y in data["points"]]
    identities = []
    for step in iterations:
        i, extra = step.iteration - 1, step.extra
        for formula in THREE_POINT:
            if extra[formula.key]:
                _decorate(extra[formula.key], extra[formula.key]["h"], formula)
        extra["recommended"] = _recommended(extra, i)
        f = {o: ys[i + o] for o in range(-2, 3) if 0 <= i + o < len(ys)}
        items = []
        for formula in formulas:
            row = extra[formula.key]
            if row and (item := _identity(formula, f, row["h"]["value"], row["D"])) is not None:
                items.append(item)
        identities.append({"i": step.iteration, "x_display": extra["x_display"], "items": items})

    meta = {
        "mode": "table",
        "points": [[x, y] for x, y in zip(xs, ys)],
        "uniform": True,
        "verification": {**verification, "identities": identities},
        "rounding_text": ROUNDING_TEXT["table"],
    }
    return function, formulas, True, iterations, warnings, meta


def solve_three_point(data):
    """Punto de entrada del registro: datos ya validados -> SolverResult."""
    mode = _table if data["mode"] == "table" else _function
    return build_result(METHOD, data, mode(data))
