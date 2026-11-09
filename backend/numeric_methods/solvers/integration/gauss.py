"""Cuadratura gaussiana (Gauss-Legendre, simple y compuesta; notación de Chapra).

Simple (N = 1), con m puntos:

  I ≈ (b − a)/2 · Σ wᵢ·f(xᵢ),  xᵢ = (b + a)/2 + (b − a)/2·tᵢ

Compuesta: [a, b] en N subintervalos de ancho H = (b − a)/N, centros
c_j = a + (j − ½)H, y la fórmula simple en cada uno:

  I ≈ Σ_j H/2 · Σᵢ wᵢ·f(c_j + H/2·tᵢ)

Los nodos tᵢ son las raíces de P_m(t) (Newton sobre la recurrencia de
Legendre, hasta un cambio < 10⁻¹⁵) y los pesos, wᵢ = 2/[(1 − tᵢ²)·P'_m(tᵢ)²].

Refinamiento: la fila k usa m = k puntos con el N elegido fijo; error
estimado |G_m − G_(m−1)|, Eₜ, εₜ y, para m ≤ 5, la cota
(b − a)·H^(2m)·(m!)⁴/((2m + 1)[(2m)!]³)·M_2m. Se detiene con error estimado
≤ tolerancia y al menos MIN_ROWS filas.

Gauss no evalúa los extremos: f puede no estar definida en a o en b.

Reutiliza del trapecio la integral exacta o de referencia, el criterio de la
marca R, el formato de los límites y la curva; de Romberg, el límite y el
formato de la comparación de costo.

No depende de Django: puede usarse y testearse de forma aislada.
"""

import math
from decimal import Decimal
from fractions import Fraction
from functools import lru_cache

import sympy as sp

from ...expressions.to_latex import expression_to_latex
from ...expressions.to_text import expression_to_text
from ..base import IterationStep, SolverResult
from ..differentiation import display
from ..differentiation.display import _CONTEXT, _plain
from ..differentiation.finite_differences import (
    MACHINE_EPSILON,
    _evaluate,
    _Function,
    _lambdify,
    _uses_trigonometry,
    parse_function_of_x,
)
from . import exact as integral_module
from .romberg import COST_LIMIT, _count
from .trapezoid import (
    CATEGORY,
    MAX_DECIMALS,
    MIN_REFINEMENTS,
    SAMPLES,
    IntegrationValidationError,
    _curve,
    _derivative_steps,
    _errors,
    _integral,
    _undefined,
    _where,
)

METHOD = "gauss"

DEFAULT_TOLERANCE = 0.000001
DEFAULT_MAX_POINTS = 12
MIN_ROWS = MIN_REFINEMENTS
MIN_MAX_POINTS = 6
MAX_MAX_POINTS = 20
DEFAULT_SUBINTERVALS = 1
MIN_SUBINTERVALS = 1
MAX_SUBINTERVALS = 50
NEWTON_TOLERANCE = 1e-15
NEWTON_MAX_STEPS = 100
# La cota sólo se calcula hasta m = 5 (derivada de orden 10).
MAX_BOUND_POINTS = 5
# Derivadas con LaTeX más largo: plegadas en la vista y sin desglose término a término.
LONG_LATEX = 300
# Momentos: Σ wᵢtᵢᵏ coincide con ∫ tᵏ si la diferencia es ≤ 10⁻¹²·máx(1, |∫|).
MOMENT_RELATIVE = 1e-12

TABLE_MESSAGE = (
    "La cuadratura gaussiana necesita evaluar la función en puntos especiales (las raíces de los polinomios de "
    "Legendre), que son números irracionales; por eso no funciona con una tabla de datos. Para datos, usa el "
    "trapecio, Simpson o Romberg."
)
BOUND_UNAVAILABLE = (
    "La cota necesita la derivada de orden 2m de f, que para muchos puntos se vuelve muy larga de calcular; el "
    "error verdadero y el error estimado siguen disponibles."
)

# Formas exactas (LaTeX) de los nodos y pesos para m ≤ 4, en el orden de los nodos (de menor a mayor).
_M4_OUTER = r"\sqrt{\frac{3}{7} + \frac{2}{7}\sqrt{\frac{6}{5}}}"
_M4_INNER = r"\sqrt{\frac{3}{7} - \frac{2}{7}\sqrt{\frac{6}{5}}}"
_M4_W_OUTER = r"\frac{18 - \sqrt{30}}{36}"
_M4_W_INNER = r"\frac{18 + \sqrt{30}}{36}"
EXACT_FORMS = {
    1: (["0"], ["2"]),
    2: ([r"-\frac{1}{\sqrt{3}}", r"\frac{1}{\sqrt{3}}"], ["1", "1"]),
    3: ([r"-\sqrt{\frac{3}{5}}", "0", r"\sqrt{\frac{3}{5}}"], [r"\frac{5}{9}", r"\frac{8}{9}", r"\frac{5}{9}"]),
    4: ([f"-{_M4_OUTER}", f"-{_M4_INNER}", _M4_INNER, _M4_OUTER], [_M4_W_OUTER, _M4_W_INNER, _M4_W_INNER, _M4_W_OUTER]),
}


# --- Nodos y pesos ------------------------------------------------------------------

def _legendre(m, t):
    """(P_m(t), P'_m(t)) con (k + 1)P_(k+1) = (2k + 1)·t·P_k − k·P_(k−1)."""
    previous, current = 1.0, t
    for k in range(1, m):
        previous, current = current, ((2 * k + 1) * t * current - k * previous) / (k + 1)
    return current, m * (t * current - previous) / (t * t - 1)


@lru_cache(maxsize=None)
def nodes_and_weights(m):
    """(nodos, pesos) de Gauss-Legendre con m puntos, de menor a mayor.

    Newton desde cos(π(i − ¼)/(m + ½)) para las raíces positivas; las
    negativas son su reflejo (y 0 si m es impar), así que son simétricas.
    """
    positive = []
    for i in range(1, m // 2 + 1):
        t = math.cos(math.pi * (i - 0.25) / (m + 0.5))
        for _ in range(NEWTON_MAX_STEPS):
            p, dp = _legendre(m, t)
            change = p / dp
            t -= change
            if abs(change) < NEWTON_TOLERANCE:
                break
        positive.append(t)
    nodes = sorted([-t for t in positive] + ([0.0] if m % 2 else []) + positive)
    weights = [2 / ((1 - t * t) * _legendre(m, t)[1] ** 2) for t in nodes]
    return tuple(nodes), tuple(weights)


def bound_constant(m):
    """(m!)⁴ / ((2m + 1)·[(2m)!]³)."""
    return Fraction(math.factorial(m) ** 4, (2 * m + 1) * math.factorial(2 * m) ** 3)


def moments(m):
    """Σ wᵢtᵢᵏ frente a ∫₋₁¹ tᵏ dt (2/(k + 1) si k es par, 0 si es impar), k = 0, …, 2m."""
    nodes, weights = nodes_and_weights(m)
    rows = []
    for k in range(2 * m + 1):
        value = math.fsum(w * t ** k for t, w in zip(nodes, weights)) + 0.0
        exact = 0.0 if k % 2 else 2 / (k + 1)
        difference = abs(value - exact)
        rows.append({
            "k": k,
            "value": value,
            "exact": exact,
            "exact_latex": "0" if k % 2 else ("2" if k == 0 else rf"\frac{{2}}{{{k + 1}}}"),
            "difference": difference,
            "ok": difference <= MOMENT_RELATIVE * max(1.0, abs(exact)),
        })
    return rows


# --- Nombres de las derivadas -------------------------------------------------------

def derivative_name(k):
    """f, f', f'', f''', f^{(4)}, …"""
    return "f" + "'" * k if k <= 3 else f"f^{{({k})}}"


# --- Una fila: G_m y su paso a paso -------------------------------------------------

def _evaluations(function, a, b, n_sub, m):
    """Los nodos de cada subintervalo llevados a [a, b] y f en ellos."""
    nodes, _ = nodes_and_weights(m)
    H = (b - a) / n_sub
    xs = [[a + (j - 0.5) * H + H / 2 * t for t in nodes] for j in range(1, n_sub + 1)]
    return xs, [[function(x) for x in group] for group in xs]


def _value(values, weights, H):
    return H / 2 * math.fsum(w * f for group in values for w, f in zip(weights, group)) + 0.0


def _node_display(nodes, centers, half, xs):
    """Decimales de tᵢ con los que c_j + (H/2)·tᵢ coincide (a 6) con cada xᵢ."""
    for d in range(display.DISPLAY_DECIMALS, MAX_DECIMALS + 1):
        shown = [display.fixed(t, d) for t in nodes]
        if all(display.fixed(float(c + half * Decimal(s))) == display.fixed(x)
               for c, group in zip(centers, xs) for s, x in zip(shown, group)):
            break
    return d, shown


def _product_display(weights, values, half, G):
    """Decimales de wᵢ, f(xᵢ) y wᵢ·f(xᵢ) con los que (H/2)·Σ da G (a 6)."""
    target = display.fixed(G)
    for d in range(display.DISPLAY_DECIMALS, MAX_DECIMALS + 1):
        quantum = Decimal(1).scaleb(-d)
        w_shown = [display.fixed(w, d) for w in weights]
        f_shown = [[display.fixed(f, d) for f in group] for group in values]
        products = [[_CONTEXT.multiply(Decimal(ws), Decimal(fs)).quantize(quantum, context=_CONTEXT)
                     for ws, fs in zip(w_shown, group)] for group in f_shown]
        sums = [sum(group, Decimal(0)) for group in products]
        partials = [half * s for s in sums]
        total = sum(partials, Decimal(0))
        if display.fixed(float(total)) == target:
            break
    return {"decimals": d, "w": w_shown, "f": f_shown, "products": products, "sums": sums,
            "partials": partials, "total": total}


def _step(m, xs, values, f_terms, centers, half, G):
    nodes, weights = nodes_and_weights(m)
    node_decimals, t_shown = _node_display(nodes, centers, half, xs)
    shown = _product_display(weights, values, half, G)
    exact_t, exact_w = EXACT_FORMS.get(m, (None, None))
    return {
        "node_decimals": node_decimals,
        "decimals": shown["decimals"],
        "nodes": [{
            "i": i + 1, "t": t, "t_display": t_shown[i], "t_latex": exact_t[i] if exact_t else None,
            "w": w, "w_display": shown["w"][i], "w_latex": exact_w[i] if exact_w else None,
        } for i, (t, w) in enumerate(zip(nodes, weights))],
        "groups": [{
            "j": j + 1,
            "center": display.decimal(centers[j]),
            "points": [{
                "i": i + 1, "x": x, "x_display": display.fixed(x), "f": f, "f_display": shown["f"][j][i],
                "terms": f_terms(x), "product": _plain(shown["products"][j][i]),
            } for i, (x, f) in enumerate(zip(xs[j], values[j]))],
            "sum": _plain(shown["sums"][j]),
            "partial": display.decimal(shown["partials"][j]),
        } for j in range(len(xs))],
        "count": m * len(xs),
        "total": display.decimal(shown["total"]),
    }


def _chart_row(m, xs, values, weights, H, a, b, G):
    """Rectángulos: en cada nodo, altura f(xᵢ) y ancho wᵢ·H/2, centrado en el nodo."""
    rects = []
    for group, f_values in zip(xs, values):
        for x, f, w in zip(group, f_values, weights):
            width = w * H / 2
            rects.append({"x": x, "left": x - width / 2, "right": x + width / 2, "height": f})
    overlap = any(r["right"] > s["left"] + 1e-12 * max(1.0, abs(s["left"])) for r, s in zip(rects, rects[1:]))
    n_sub = len(xs)
    edges = [a + j * H for j in range(n_sub)] + [b]
    return {"m": m, "rects": rects, "edges": edges, "overlap": overlap, "area": G}


# --- Derivadas y cota -----------------------------------------------------------------

def _derivatives(function, order):
    """[f', …, f⁽ᵒʳᵈᵉʳ⁾] (las que alcanzaron el límite de tiempo) y si se agotó."""
    return integral_module.derivatives(function.expr, function.symbol, order)


def _derivative_info(function, found):
    """Cada derivada con su LaTeX y, si la anterior es corta, el desglose término a término."""
    x = function.symbol
    previous, info = function.expr, []
    for k, expr in enumerate(found, start=1):
        latex = expression_to_latex(expr, order=None)
        steps = None
        if len(expression_to_latex(previous, order=None)) <= LONG_LATEX:
            steps = _derivative_steps(previous, x, derivative_name(k - 1))
            if steps["sum_latex"]:
                steps["sum_latex"] = steps["sum_latex"].replace(
                    f"{derivative_name(k - 1)}'(x)", f"{derivative_name(k)}(x)", 1)
        info.append({"order": k, "name": derivative_name(k), "latex": latex, "text": expression_to_text(expr),
                     "long": len(latex) > LONG_LATEX, "steps": steps, "constant": not expr.has(x)})
        previous = expr
    return info


def _max_abs(function, expr, a, b):
    """(M, x) = máx |expr| en [a, b] con SAMPLES puntos; None si no es finita en alguno."""
    xs = [a + (b - a) * i / (SAMPLES - 1) for i in range(SAMPLES)]
    if function._has_kink(a, b, xs):
        return None
    evaluator = _lambdify(function.symbol, expr)
    values = [_evaluate(evaluator, x) for x in xs]
    if None in values:
        return None
    where = max(range(SAMPLES), key=lambda i: abs(values[i]))
    return abs(values[where]), xs[where]


def _M_info(function, expr, M, x_M):
    x = function.symbol
    short = len(expression_to_latex(expr, order=None)) <= LONG_LATEX
    return {
        "value": M, "x": x_M, "x_display": display.data_value(x_M),
        # f⁽²ᵐ⁾ donde se alcanzó M, término a término (None si es constante o muy larga).
        "substitution": integral_module.substitution(expr, x, x_M, display.data_value(x_M))
        if expr.has(x) and short else None,
    }


# --- Comparación de costo ------------------------------------------------------------

def _newton_cotes_cost(function, a, b, I, tolerance):
    """Evaluaciones del trapecio (n desde 1), Simpson 1/3 (n desde 2) y Romberg
    (primera fila de la diagonal) hasta |Eₜ| ≤ tolerancia, duplicando n ≤ COST_LIMIT."""
    width = b - a
    n, T, previous = 1, width / 2 * (function(a) + function(b)), None
    romberg_row = [T]
    trapezoid = simpson = romberg = None
    while True:
        if trapezoid is None and abs(I - T) <= tolerance:
            trapezoid = n + 1
        if simpson is None and previous is not None and abs(I - (4 * T - previous) / 3) <= tolerance:
            simpson = n + 1
        if romberg is None and abs(I - romberg_row[-1]) <= tolerance:
            romberg = n + 1
        if (trapezoid and simpson and romberg) or n >= COST_LIMIT:
            break
        n *= 2
        h = width / n
        new = [function(a + (2 * j - 1) * h) for j in range(1, n // 2 + 1)]
        if None in new:  # f no definida en un punto interior
            break
        previous, T = T, T / 2 + h * math.fsum(new)
        row = [T]
        for k in range(2, len(romberg_row) + 2):
            factor = 4 ** (k - 1)
            row.append((factor * row[-1] - romberg_row[k - 2]) / (factor - 1))
        romberg_row = row
    return trapezoid, simpson, romberg


def _cost(function, a, b, I, tolerance, rows, n_sub, applicable):
    first = next((row for row in rows if row["true_error"] is not None and abs(row["true_error"]) <= tolerance), None)
    trapezoid = simpson = romberg = None
    if applicable:
        trapezoid, simpson, romberg = _newton_cotes_cost(function, a, b, I, tolerance)
    tol = display.fixed(tolerance, 12)
    total = sum(row["evaluations"] for row in rows)
    where = "" if n_sub == 1 else f" en N = {n_sub} subintervalos"
    if first is None:
        text = f"Gauss no llegó a |Eₜ| ≤ {tol} en sus {len(rows)} filas ({_count(total)} evaluaciones en total)."
    else:
        text = (f"Gauss llegó a |Eₜ| ≤ {tol} con m = {first['m']} puntos{where}: {_count(first['evaluations'])} "
                f"evaluaciones de f.")
    if applicable:
        more = f"más de {_count(COST_LIMIT + 1)}"
        shown = lambda count: _count(count) if count else more  # noqa: E731
        text += (f" Romberg habría necesitado {shown(romberg)}, Simpson 1/3 {shown(simpson)} y el trapecio "
                 f"{shown(trapezoid)}.")
    else:
        text += (" El trapecio, Simpson y Romberg no son aplicables: evalúan f en los extremos, donde no está "
                 "definida.")
    if first is not None and first["m"] < rows[-1]["m"]:
        reason = f"Por el mínimo de {MIN_ROWS} filas" if first["m"] < MIN_ROWS else "Hasta que el error estimado cumplió"
        text += f" {reason}, el sistema hizo {_count(total)} evaluaciones en total."
    return {
        "first_m": first["m"] if first else None,
        "gauss_evaluations": first["evaluations"] if first else None,
        "total_evaluations": total,
        "trapezoid_evaluations": trapezoid,
        "simpson_evaluations": simpson,
        "romberg_evaluations": romberg,
        "applicable": applicable,
        "limit": COST_LIMIT,
        "text": text,
    }


# --- Solver -----------------------------------------------------------------------

def _function_info(function, derivative_info):
    return {
        "latex": expression_to_latex(function.typed),
        "text": expression_to_text(function.expr),
        "is_sum": isinstance(function.expr, sp.Add),
        "uses_trigonometry": _uses_trigonometry(function.expr),
        "substitution_terms": integral_module.substituter(function.expr, function.symbol)[0],
        "derivatives": derivative_info,
    }


def _node_text(x):
    return display.fixed(x)


def solve_gauss(data):
    """Punto de entrada del registro: datos ya validados -> SolverResult."""
    a, b = float(data["a"]), float(data["b"])
    n_sub, tolerance, max_points = data["subintervals"], data["tolerance"], data["max_iterations"]
    function = _Function(parse_function_of_x(data["function"]), set())

    # Fila 1 (m = 1): f debe ser real y finita en todos sus nodos.
    xs, values = _evaluations(function, a, b, n_sub, 1)
    for j, (group, f_values) in enumerate(zip(xs, values), start=1):
        if None in f_values:
            x = group[f_values.index(None)]
            where = "" if n_sub == 1 else f" del subintervalo {j}"
            raise IntegrationValidationError(
                f"f(x) no es real y finita en el nodo{where} de la fila 1 (m = 1), x = {_node_text(x)}: la cuadratura "
                "gaussiana necesita evaluar f en sus nodos."
            )

    warnings, notes = [], []
    undefined_ends = [(x, name) for x, name in ((a, "a"), (b, "b")) if function(x) is None]
    for x, name in undefined_ends:
        notes.append(
            f"f(x) no está definida en x = {_where(display.data_value(x))} (límite {name}). Gauss no evalúa los "
            "extremos, así que puede calcular la integral, pero la convergencia puede ser lenta. Es una ventaja de "
            "Gauss frente al trapecio, Simpson y Romberg, que sí necesitan f(a) y f(b)."
        )
    integral, check, integral_notes = _integral(function, a, b)
    notes.extend(integral_notes)
    interior = [a + (b - a) * i / (SAMPLES - 1) for i in range(1, SAMPLES - 1)]
    singular = next((x for x in interior if function(x) is None), None)
    if singular is not None:
        warnings.append(_undefined(display.data_value(singular), a, b))
        integral.update({"kind": None, "value": None, "label": None, "antiderivative": None})
        check = None
    I = integral["value"]

    A, B = display.exact(a), display.exact(b)
    H = (b - a) / n_sub
    H_number = _CONTEXT.divide(B - A, n_sub)
    half = H_number / 2
    centers = [A + (j - Decimal("0.5")) * H_number for j in range(1, n_sub + 1)]
    _, f_terms = integral_module.substituter(function.expr, function.symbol)

    # Filas: m = 1, 2, …; la parada sólo depende del error estimado.
    raw, chart_rows = [], []
    converged = stopped = False
    for m in range(1, max_points + 1):
        if m > 1:
            xs, values = _evaluations(function, a, b, n_sub, m)
        missing = next(((x, f.index(None)) for x, f in zip(xs, values) if None in f), None)
        if missing:
            message = _undefined({"exact": False, "approx": _node_text(missing[0][missing[1]])}, a, b)
            if message not in warnings:
                warnings.append(message)
            stopped = True
            break
        _, weights = nodes_and_weights(m)
        G = _value(values, weights, H)
        previous = raw[-1]["G"] if raw else None
        estimated = None if previous is None else abs(G - previous)
        raw.append({"m": m, "G": G, "xs": xs, "values": values, "estimated": estimated,
                    "previous": previous, "weights": weights})
        chart_rows.append(_chart_row(m, xs, values, weights, H, a, b, G))
        if m >= MIN_ROWS and estimated <= tolerance:
            converged = True
            break

    # Derivadas para la cota (m ≤ 5), con límite de tiempo.
    bound_rows = min(len(raw), MAX_BOUND_POINTS)
    found, timed_out = _derivatives(function, 2 * bound_rows)
    maxima = {}
    width_number = B - A
    rows, iterations = [], []
    for item in raw:
        m, G = item["m"], item["G"]
        order = 2 * m
        reason, bound, bound_info = None, None, None
        if m > MAX_BOUND_POINTS:
            reason = "order"
        elif len(found) < order:
            reason = "timeout"
        else:
            if order not in maxima:
                maxima[order] = _max_abs(function, found[order - 1], a, b)
            if maxima[order] is None:
                reason = "not_finite"
            else:
                M, x_M = maxima[order]
                constant = bound_constant(m)
                bound = (b - a) * H ** order * float(constant) * M
                bound_info = {
                    "order": order,
                    "constant": [constant.numerator, constant.denominator],
                    "constant_value": float(constant),
                    "width_power": display.decimal(width_number * H_number ** order),
                    "M": _M_info(function, found[order - 1], M, x_M),
                }
        step = _step(m, item["xs"], item["values"], f_terms, centers, half, G)
        # R: redondeo al evaluar f término a término (Σ|términos|, no |f|: en el polinomio de
        # Chapra los términos se cancelan) y al sumar, más el del propio G.
        abs_sum = math.fsum(
            w * (math.fsum(abs(t) for t in p["terms"]) if None not in p["terms"] else abs(p["f"]))
            for group in step["groups"] for w, p in zip(item["weights"], group["points"])
        )
        rounding = 2 * MACHINE_EPSILON * (H / 2 * abs_sum + abs(G))
        true, relative, within, by_rounding, equals = _errors(I, G, bound, rounding)
        row = {
            "m": m,
            "evaluations": m * n_sub,
            "G": G,
            "previous_G": item["previous"],
            "estimated_error": item["estimated"],
            "true_error": true,
            "relative_error": relative,
            "bound": bound,
            "bound_reason": reason,
            "bound_info": bound_info,
            "rounding": rounding,
            "within_bound": within,
            "by_rounding": by_rounding,
            "equals_bound": equals,
            "below_tolerance": None if item["estimated"] is None else item["estimated"] <= tolerance,
            "step": step,
        }
        rows.append(row)
        iterations.append(IterationStep(iteration=m, x=[G], error=item["estimated"], extra=row))

    reasons = {row["bound_reason"] for row in rows}
    if reasons & {"order", "timeout"}:
        limit = (f" (se superó el límite de {integral_module.TIME_LIMIT:g} s al derivar)"
                 if "timeout" in reasons else "")
        notes.append(f"Cota no disponible desde m = {next(r['m'] for r in rows if r['bound_reason'] in ('order', 'timeout'))}"
                     f"{limit}: {BOUND_UNAVAILABLE[0].lower()}{BOUND_UNAVAILABLE[1:]}")
    if "not_finite" in reasons:
        notes.append(
            "La derivada de orden 2m de f no es finita en algún punto de [a, b] (por ejemplo, cerca de un extremo "
            "donde f no está definida): la cota no está disponible. El error verdadero y el estimado sí."
        )
    if I is None and singular is None:
        warnings.append(
            "No se pudo calcular la integral exacta ni un valor de referencia: no se muestran el error verdadero "
            "ni el relativo."
        )
    if not converged:
        tolerance_text = display.fixed(tolerance, 12)
        warnings.append(
            f"No se alcanzó la tolerancia del error estimado ({tolerance_text})."
            if stopped else
            f"No se alcanzó la tolerancia del error estimado ({tolerance_text}) con {len(rows)} puntos. Aumenta el "
            "máximo de puntos, el número de subintervalos N o la tolerancia."
        )

    last = rows[-1]
    failed = [row["m"] for row in rows if row["within_bound"] is False]
    meta = {
        "mode": "function",
        "a": a,
        "b": b,
        "a_display": display.data_value(a),
        "b_display": display.data_value(b),
        "width_display": display.decimal(width_number),
        "subintervals": n_sub,
        "H_display": display.decimal(H_number),
        "half_display": display.decimal(half),
        # Cambio de variable con N = 1: x = (b + a)/2 + (b − a)/2·t.
        "center_display": display.decimal((A + B) / 2),
        "half_width_display": display.decimal((B - A) / 2),
        "centers": [display.decimal(c) for c in centers],
        "undefined_ends": [name for _, name in undefined_ends],
        "tolerance": tolerance,
        "max_iterations": max_points,
        "function": _function_info(function, _derivative_info(function, found)),
        "derivatives_timed_out": timed_out,
        "integral": integral,
        "min_rows": MIN_ROWS,
        "max_bound_points": MAX_BOUND_POINTS,
        "evaluations": sum(row["evaluations"] for row in rows),
        "cost": None if I is None else _cost(function, a, b, I, tolerance, rows, n_sub, not undefined_ends),
        "curve": _curve(function, a, b),
        "chart_rows": chart_rows,
        "notes": notes,
        "sampling_points": SAMPLES,
        "verification": {
            **(check or {}),
            "kind": integral["kind"],
            "final": {"G": last["G"], "I": I, "true_error": last["true_error"],
                      "relative_error": last["relative_error"]},
            "moments": {"m": last["m"], "rows": moments(last["m"])},
            "failed_rows": failed,
            "all_within": I is not None and not failed and any(row["bound"] is not None for row in rows),
        },
    }
    return SolverResult(
        method=METHOD,
        category=CATEGORY,
        converged=converged,
        iterations=iterations,
        solution=[last["G"]],
        variables=["G"],
        warnings=warnings,
        meta=meta,
    )
