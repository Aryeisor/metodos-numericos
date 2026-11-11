"""Datos de la gráfica de la aproximación (diferencias, 3 y 5 puntos).

La derivada es la pendiente de la tangente; cada fórmula toma la pendiente en
x₀ del polinomio que pasa por sus puntos (incluido x₀): la secante en
diferencias, la parábola en 3 puntos y el polinomio de grado 4 en 5 puntos.
Para cada fila 1 a 4 (modo función) o cada punto xᵢ (modo tabla) y cada
fórmula se envían: ventana, puntos, curva interpolante muestreada, rectas
tangente y aproximada (dos puntos en los bordes), la cuerda (recta del primer
al último punto, para sombrear cuánto se curva la interpolante) y la frase de
lectura. La fila 1 del modo función trae además la «vista ilustrativa»: los
mismos datos con h = m·h₀ (m = 2, 5, 10), sólo para ver la forma de la curva.

Sólo lee lo que el solver ya calculó (D, h, f'(x₀)): no cambia ningún cálculo.
No depende de Django: puede usarse y testearse de forma aislada.
"""

import math

from . import display
from .formulas import BACKWARD, FORWARD

CHART_ROWS = 4
CURVE_POINTS = 300
# 97 muestras: el ancho de cada ventana es 3h, 4h o 6h y 96 es múltiplo de los
# tres, así que los puntos de la fórmula son muestras exactas del interpolante.
PIECE_INTERVALS = 96
# Margen de la ventana del modo tabla, en fracción del rango de los datos.
TABLE_MARGIN = 0.05
# |D − f'| ≤ SAME_RELATIVE · máx(1, |f'|): la recta aproximada es la tangente.
SAME_RELATIVE = 1e-12
# Múltiplos de h₀ de la vista ilustrativa (sólo fila 1, modo función).
ILLUSTRATIVE = (2, 5, 10)

PHRASES = {
    "under": "La recta aproximada tiene menos pendiente que la tangente: la fórmula se quedó corta (subestima).",
    "over": "La recta aproximada tiene más pendiente que la tangente: la fórmula se pasó (sobreestima).",
    "equal": "La recta aproximada coincide con la tangente: la fórmula es exacta para esta función.",
}


def lagrange(xs, ys, x):
    """Valor en x del polinomio que pasa por (xs, ys)."""
    total = 0.0
    for j, (xj, yj) in enumerate(zip(xs, ys)):
        term = yj
        for m, xm in enumerate(xs):
            if m != j:
                term *= (x - xm) / (xj - xm)
        total += term
    return total


def lagrange_slope(xs, ys, x):
    """Pendiente en x del polinomio que pasa por (xs, ys): Σ yⱼ·Lⱼ'(x)."""
    total = 0.0
    for j, (xj, yj) in enumerate(zip(xs, ys)):
        slope = 0.0
        for m, xm in enumerate(xs):
            if m == j:
                continue
            term = 1 / (xj - xm)
            for l, xl in enumerate(xs):
                if l not in (j, m):
                    term *= (x - xl) / (xj - xl)
            slope += term
        total += yj * slope
    return total


def side(D, exact):
    """Dónde queda la pendiente D respecto a f'(x₀); None sin derivada exacta."""
    if exact is None:
        return None
    if abs(D - exact) <= SAME_RELATIVE * max(1.0, abs(exact)):
        return "equal"
    return "under" if D < exact else "over"


def _line(x0, y0, slope, a, b):
    return [[a, y0 + slope * (a - x0)], [b, y0 + slope * (b - x0)]]


def _sample(function, a, b):
    xs = [a + (b - a) * i / (CURVE_POINTS - 1) for i in range(CURVE_POINTS)]
    return {"x": xs, "y": [function(x) for x in xs]}


def _label(offset, base):
    if offset == 0:
        return base
    factor = "" if abs(offset) == 1 else str(abs(offset))
    return f"{base} {'+' if offset > 0 else '−'} {factor}h"


def _piece(formula, D, nodes, x0, h_shown, exact, f_x0, window=None, base="x₀"):
    """Una fórmula en una fila: `nodes` = [(desplazamiento, x, y)] con x₀ incluido."""
    h = h_shown["value"]
    nodes = sorted(nodes)
    low, high = nodes[0][0] - 1, nodes[-1][0] + 1
    xs, ys = [x for _, x, _ in nodes], [y for *_, y in nodes]
    y0 = next(y for o, _, y in nodes if o == 0)
    a, b = window or (x0 + low * h, x0 + high * h)
    samples = [x0 + (low + (high - low) * i / PIECE_INTERVALS) * h for i in range(PIECE_INTERVALS + 1)]
    where = side(D, exact)
    # Cuerda del primer al último punto, en las muestras de la interpolante entre ellos.
    # En diferencias (2 puntos) la interpolante es la cuerda: no hay nada que sombrear.
    chord = None
    if len(nodes) > 2:
        (_, xa, ya), (_, xb, yb) = nodes[0], nodes[-1]
        eps = 1e-9 * abs(xb - xa)
        cx = [x for x in samples if xa - eps <= x <= xb + eps]
        chord = {"x": cx, "y": [ya + (yb - ya) * (x - xa) / (xb - xa) for x in cx]}
    return {
        "key": formula.key,
        "name": formula.name,
        "D": D,
        "h": h_shown,
        "window": [a, b],
        "points": [{"x": x, "y": y, "label": _label(o, base), "base": o == 0} for o, x, y in nodes],
        "interpolant": {"x": samples, "y": [lagrange(xs, ys, x) for x in samples]},
        "chord": chord,
        "approx": _line(x0, y0, D, a, b),
        "tangent": None if exact is None else _line(x0, f_x0, exact, a, b),
        "error": None if exact is None else abs(D - exact),
        "side": where,
        "phrase": PHRASES.get(where),
    }


def _join(parts):
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " y " + parts[-1]


def compare_phrase(lines):
    """Lectura de «Comparar»: qué rectas quedan con menos o más pendiente que la tangente."""
    if not lines or lines[0]["side"] is None:
        return None
    def named(name):
        name = name.lower()
        return f"{'el' if name.startswith(('punto', 'extremo')) else 'la'} {name}"

    groups = {where: [named(line["name"]) for line in lines if line["side"] == where]
              for where in ("under", "over", "equal")}
    parts = []
    for where, verb in (("under", "menos pendiente que la tangente (subestima"),
                        ("over", "más pendiente que la tangente (sobreestima"),
                        ("equal", "la misma pendiente que la tangente (exacta")):
        names = groups[where]
        if names:
            plural = len(names) > 1
            ending = "n)" if plural and where != "equal" else "s)" if plural else ")"
            parts.append(f"{_join(names)} {'tienen' if plural else 'tiene'} {verb}{ending}")
    text = "; ".join(parts)
    text = text[0].upper() + text[1:] + "."
    sides = {line["key"]: line["side"] for line in lines}
    if {sides.get(FORWARD.key), sides.get(BACKWARD.key)} == {"under", "over"}:
        text += (" La progresiva y la regresiva quedan una a cada lado de la tangente: por eso su promedio "
                 "(la fórmula de 3 puntos) se acerca tanto.")
    return text


def _row(function, formulas, x0, h_shown, slopes, exact, f_x0, reference):
    """Una fila del modo función: las fórmulas con sus pendientes `slopes`
    (clave → D), la curva f y «Comparar» en la ventana que las cubre a todas."""
    h = h_shown["value"]
    pieces = {}
    for formula in formulas:
        offsets = {o for o, _ in formula.nodes} | {0}
        nodes = [(o, x0 + o * h, function(x0 + o * h)) for o in offsets]
        pieces[formula.key] = _piece(formula, slopes[formula.key], nodes, x0, h_shown, exact, f_x0)
    lines = [{"key": p["key"], "name": p["name"], "D": p["D"], "side": p["side"]} for p in pieces.values()]
    windows = [p["window"] for p in pieces.values()]
    if reference is not None:
        D = _slope(function, reference, x0, h)
        if D is not None:
            lines.append({"key": "reference", "name": reference.name, "D": D, "side": side(D, exact)})
            offsets = [o for o, _ in reference.nodes] + [0]
            windows.append([x0 + (min(offsets) - 1) * h, x0 + (max(offsets) + 1) * h])
    a, b = min(w[0] for w in windows), max(w[1] for w in windows)
    for line in lines:
        line["line"] = _line(x0, f_x0, line["D"], a, b)
    return {
        "h": h_shown,
        "curve": _sample(function, a, b),
        "formulas": pieces,
        "compare": {
            "window": [a, b],
            "tangent": None if exact is None else _line(x0, f_x0, exact, a, b),
            "lines": lines,
            "phrase": compare_phrase(lines),
        },
    }


def _finite(value):
    return value is not None and math.isfinite(value)


def _slope(function, formula, x0, h):
    """D(h) = Σ wᵢ·f(x₀ + oᵢh) / (q·h); None si algún f(xᵢ) no es finito."""
    values = [function(x0 + o * h) for o, _ in formula.nodes]
    if not all(_finite(v) for v in values):
        return None
    return sum(w * v for (_, w), v in zip(formula.nodes, values)) / (formula.divisor * h) + 0.0


def _minus(text):
    return text.replace("-", "−")


def _illustrative(function, formulas, x0, h0, exact, f_x0, reference):
    """Fila 1 con h = m·h₀ para cada m de ILLUSTRATIVE. Una fórmula sólo se
    ofrece si todos sus puntos dan valores finitos y la curva f no es toda no
    finita en la ventana; si no, `reasons` dice por qué. «Comparar» necesita
    todas las fórmulas."""
    views = []
    for m in ILLUSTRATIVE:
        number = display.exact(h0) * m
        h_shown = {"value": float(number), **display.decimal(number)}
        h, h_text = h_shown["value"], _minus(h_shown["text"])
        reasons, slopes = {}, {}
        for formula in formulas:
            for o in sorted({o for o, _ in formula.nodes} | {0}):
                if not _finite(function(x0 + o * h)):
                    x = _minus(display.decimal(display.exact(x0) + o * number)["text"])
                    reasons[formula.key] = f"con h = {h_text} la fórmula necesitaría f({x}), que no está definida"
                    break
            else:
                slopes[formula.key] = _slope(function, formula, x0, h)
        available = [f for f in formulas if f.key in slopes]
        view = {"m": m, "h": h_shown, "formulas": {}, "curve": None, "compare": None}
        if available:
            view.update(_row(function, available, x0, h_shown, slopes, exact, f_x0, reference))
            if not any(_finite(y) for y in view["curve"]["y"]):
                view.update(formulas={}, curve=None, compare=None)
                reasons = {f.key: f"con h = {h_text} la curva f no está definida en la ventana" for f in formulas}
        if reasons:
            view["compare"] = None
            reasons["compare"] = next(iter(reasons.values()))
        view["reasons"] = reasons
        views.append(view)
    return views


def function_chart(function, formulas, iterations, x0, exact, reference=None):
    """Filas 1 a 4 del modo función. `reference`: fórmula que «Comparar» agrega
    con el mismo h (el punto medio de 3 puntos en 5 puntos). None si f(x₀) no
    está definida (las fórmulas centradas no la usan, pero la gráfica sí)."""
    f_x0 = function(x0)
    if f_x0 is None:
        return None
    rows = []
    for step in iterations[:CHART_ROWS]:
        slopes = {f.key: step.extra[f.key]["D"] for f in formulas}
        rows.append({"k": step.iteration,
                     **_row(function, formulas, x0, step.extra["h"], slopes, exact, f_x0, reference)})
    if rows:
        rows[0]["illustrative"] = _illustrative(function, formulas, x0, rows[0]["h"]["value"], exact, f_x0, reference)
    return {"mode": "function", "x0": x0, "f_x0": f_x0, "exact": exact, "rows": rows}


def table_chart(function, computed, iterations, xs, ys):
    """Cada punto xᵢ con las fórmulas `computed` que aplican allí. La ventana
    es todo el rango de los datos con un margen; la fórmula por defecto es la
    «Recomendada» (3 y 5 puntos) o la primera que aplica (diferencias)."""
    margin = (xs[-1] - xs[0]) * TABLE_MARGIN
    window = (xs[0] - margin, xs[-1] + margin)
    rows = []
    for step in iterations:
        i, extra = step.iteration - 1, step.extra
        f_x = function(xs[i]) if function else None
        pieces = {}
        for formula in computed:
            row = extra.get(formula.key)
            if not row:
                continue
            offsets = {o for o, _ in formula.nodes} | {0}
            nodes = [(o, xs[i + o], ys[i + o]) for o in offsets]
            pieces[formula.key] = _piece(formula, row["D"], nodes, xs[i], row["h"], extra["exact"],
                                         ys[i] if f_x is None else f_x, window, base="xᵢ")
        default = extra["recommended"]["key"] if "recommended" in extra else next(iter(pieces))
        rows.append({"i": step.iteration, "x": xs[i], "default": default, "formulas": pieces})
    return {
        "mode": "table",
        "window": list(window),
        "curve": _sample(function, *window) if function else None,
        "default_point": len(xs) // 2 + 1,
        "rows": rows,
    }
