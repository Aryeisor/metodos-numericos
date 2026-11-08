"""Método del trapecio (regla simple y compuesta) para aproximar ∫ f en [a, b].

Dos modos de entrada:

- «Función»: f(x), a, b y n₀. Tabla de refinamiento: la fila k usa
  n_k = n₀·2^(k−1) segmentos y h_k = (b − a)/n_k. La fila 1 aplica la regla
  compuesta (rules.py); desde la fila 2 se aprovechan los puntos ya
  evaluados: T_k = T_(k−1)/2 + h_k·Σ f(nuevos), con los nuevos en
  a + (2j − 1)·h_k. En cada fila: error estimado |T_k − T_(k−1)|, error
  verdadero Eₜ = I − T, relativo εₜ = |Eₜ|/|I|·100, error aproximado de
  Chapra Eₐ = −(b − a)h²/12·f̄'' (f̄'' = [f'(b) − f'(a)]/(b − a)), la cota
  (b − a)h²/12·M₂ (M₂ = máx|f''| por muestreo) y la razón Eₜ,k/Eₜ,(k−1).
  Se detiene cuando el error estimado es ≤ tolerancia, con al menos
  MIN_ITERATIONS filas.
- «Tabla de datos»: puntos (xᵢ, yᵢ), con espaciado no uniforme permitido:
  cada segmento es un trapecio con su propio ancho. Con una función para
  comparar se agregan la integral, el error y la cota por segmentos.

La integral exacta o de referencia sale de exact.py; f' y f'' se calculan
simbólicamente una sola vez (el mismo _Function de diferenciación).

No depende de Django: puede usarse y testearse de forma aislada.
"""

import math
from decimal import Decimal

import sympy as sp

from ...expressions.to_latex import expression_to_latex
from ...expressions.to_text import expression_to_text
from ..base import IterationStep, SolverResult
from ..differentiation import display
from ..differentiation.display import _CONTEXT, _plain
from ..differentiation.finite_differences import (
    DATA_RELATIVE,
    MACHINE_EPSILON,
    UNIFORM_RELATIVE,
    _evaluate,
    _Function,
    _uses_trigonometry,
    parse_function_of_x,
)
from ..nonlinear.derivative_steps import entry_steps
from ..validation import MIN_ITERATIONS, InputValidationError
from . import exact as integral_module
from .rules import TRAPEZOID, apply, public_rule

CATEGORY = "integration"
METHOD = "trapecio"

DEFAULT_TOLERANCE = 0.000001
DEFAULT_MAX_REFINEMENTS = 20
MIN_REFINEMENTS = MIN_ITERATIONS
MAX_REFINEMENTS = 22
DEFAULT_N0 = 1
MIN_N0 = 1
MAX_N0 = 1000
MIN_POINTS = 2
MAX_POINTS = 30
# shortcut: con n₀ grande y muchas filas, n_k crecería a miles de millones; se corta aquí.
MAX_SEGMENTS = 2 ** 21

# Puntos equiespaciados (extremos incluidos) para estimar máx|f''|.
SAMPLES = 2001
SEGMENT_SAMPLES = 401
CURVE_POINTS = 300
# Filas que se pueden ver en el gráfico de trapecios.
CHART_MAX_N = 64
# Por debajo de esto |I| se considera 0 y εₜ no se calcula.
ZERO_INTEGRAL = 1e-12
# Paso a paso: con más puntos se muestran los 8 primeros y los 8 últimos.
FOLD_FIRST_ROW = 17
FOLD_NEW_POINTS = 16
FOLD_KEEP = 8
# Hasta esta cantidad de puntos llegan todos (botón «Mostrar todos los puntos»);
# con más sólo los 8 primeros y los 8 últimos.
FULL_POINTS = 1024
# |Eₜ| ≤ cota·(1 + 10⁻⁹) es «dentro de la cota» sin redondeo; |Eₜ| y la cota
# con diferencia relativa ≤ 10⁻⁹ son iguales.
EQUAL_RELATIVE = 1e-9
MAX_DECIMALS = 15

REFERENCE_LABEL = "valor de referencia (cálculo numérico de alta precisión)"


class IntegrationValidationError(InputValidationError):
    """Entrada que no permite aplicar la regla de integración."""


# --- Puntos, h y formato ----------------------------------------------------------

def _x(a, b, i, n):
    return b if i == n else a + i * (b - a) / n


def _x_display(a, b, i, n):
    """xᵢ = a + i·(b − a)/n: exacto con ≤ 12 decimales; si no, a 6 (≈)."""
    A, B = display.exact(a), display.exact(b)
    return display.decimal(A + _CONTEXT.divide(i * (B - A), n))


def _paren(latex):
    return f"({latex})" if latex.startswith("-") else latex


def _step(a, b, n):
    """h = (b − a)/n exacto; si no, la forma \\frac{b − a}{n} con su aproximación."""
    number = _CONTEXT.divide(display.exact(b) - display.exact(a), n)
    shown = display.decimal(number)
    if not shown["exact"]:
        A, B = display.data_value(a), display.data_value(b)
        shown = {
            "exact": False,
            "text": f"({B['text']} − {_paren(A['text'])})/{n}",
            "latex": rf"\frac{{{B['latex']} - {_paren(A['latex'])}}}{{{n}}}",
            "approx": display.fixed((b - a) / n),
        }
    return number, {"value": (b - a) / n, **shown}


def _where(shown):
    return shown["text"] if shown["exact"] else shown["approx"]


def _undefined(shown, a, b):
    return (
        f"f(x) no está definida en x = {_where(shown)}, dentro de "
        f"[{_where(display.data_value(a))}, {_where(display.data_value(b))}]: la integral puede no existir."
    )


def _shown_indices(count, limit):
    if count <= max(limit, FULL_POINTS):
        return list(range(count))
    return list(range(FOLD_KEEP)) + list(range(count - FOLD_KEEP, count))


def _rounded_sum(values, d):
    return display.fixed(math.fsum(round(v, d) for v in values), d)


def _first_row_display(rule, values, h_number, T):
    """Decimales y textos de (h/2)·[f(x₀) + 2·Σ + f(xₙ)] coherentes con T.

    Empieza con 6 decimales y agrega hasta que el resultado de los valores
    que se ven coincida con T a 6 decimales.
    """
    n = len(values) - 1
    weights = rule.weights(n)
    factor = Decimal(rule.factor.numerator) / Decimal(rule.factor.denominator)
    target = display.fixed(T)
    for d in range(display.DISPLAY_DECIMALS, MAX_DECIMALS + 1):
        groups = {}
        for i in range(1, n):
            groups.setdefault(weights[i], []).append(values[i])
        sums = [{"weight": w, "display": _rounded_sum(vs, d)} for w, vs in groups.items()]
        ends = [display.fixed(values[0], d), display.fixed(values[n], d)]
        bracket = (Decimal(ends[0]) * rule.ends + Decimal(ends[1]) * rule.ends
                   + sum((w["weight"] * Decimal(w["display"]) for w in sums), Decimal(0)))
        visible = factor * h_number * bracket
        if display.fixed(float(visible)) == target or d == MAX_DECIMALS:
            return {
                "kind": "formula",
                "decimals": d,
                "ends": ends,
                "sums": sums,
                "bracket": _plain(bracket),
                "factor_h": display.decimal(factor * h_number),
            }


def _recurrence_display(previous_T, new_values, h_number, T):
    """T_(k−1)/2 + h_k·Σ coherente con T_k (mismo criterio)."""
    target = display.fixed(T)
    for d in range(display.DISPLAY_DECIMALS, MAX_DECIMALS + 1):
        previous = display.fixed(previous_T, d)
        new_sum = _rounded_sum(new_values, d)
        half = Decimal(previous) / 2
        product = h_number * Decimal(new_sum)
        visible = half + product
        if display.fixed(float(visible)) == target or d == MAX_DECIMALS:
            return {
                "kind": "recurrence",
                "decimals": d,
                "previous": previous,
                "half": _plain(half),
                "sum": new_sum,
                "product": display.decimal(product)["text"],
            }


def _first_step(rule, values, a, b, h_number, T, f_terms):
    """Paso a paso de la fila 1: la fórmula de pesos con cada punto sustituido."""
    n = len(values) - 1
    step = _first_row_display(rule, values, h_number, T)
    weights = rule.weights(n)
    step.update({"count": n + 1, "fold": FOLD_FIRST_ROW, "points": []})
    for i in _shown_indices(n + 1, FOLD_FIRST_ROW):
        f_display = display.fixed(values[i], step["decimals"])
        step["points"].append({
            "i": i, "x": _x(a, b, i, n), "x_display": _x_display(a, b, i, n), "f": values[i],
            "f_display": f_display, "terms": f_terms(_x(a, b, i, n)), "weight": weights[i],
            "product": display.product(weights[i], f_display),
        })
    return step


def _recurrence_step(previous_T, new_values, a, b, n, h_number, T, f_terms):
    """Paso a paso de T_k = T_(k−1)/2 + h_k·Σ f(nuevos), con los puntos nuevos (i impar)."""
    width = b - a
    step = _recurrence_display(previous_T, new_values, h_number, T)
    step.update({"count": len(new_values), "fold": FOLD_NEW_POINTS})
    step["points"] = [
        {"i": 2 * j + 1, "x": a + (2 * j + 1) * width / n, "x_display": _x_display(a, b, 2 * j + 1, n),
         "f": new_values[j], "f_display": display.fixed(new_values[j], step["decimals"]),
         "terms": f_terms(a + (2 * j + 1) * width / n)}
        for j in _shown_indices(len(new_values), FOLD_NEW_POINTS)
    ]
    return step


# --- f'' en [a, b] ----------------------------------------------------------------

def _second_derivative(function, a, b, samples, order=2):
    """(M, x donde se alcanza, valores muestreados) de |f⁽ᵒʳᵈᵉʳ⁾| (M₂ en el
    trapecio, M₄ en Simpson); M None si la derivada no es finita."""
    xs = [a + (b - a) * i / (samples - 1) for i in range(samples)]
    if function._has_kink(a, b, xs):
        return None, None, None
    values = [_evaluate(function.evaluators[order], x) for x in xs]
    if None in values:
        return None, None, None
    where = max(range(samples), key=lambda i: abs(values[i]))
    return abs(values[where]), xs[where], values


def _concavity_note(values):
    if not values:
        return None
    if all(v <= 0 for v in values) and any(v < 0 for v in values):
        return "f'' < 0 en [a, b] (curva cóncava): el trapecio subestima la integral."
    if all(v >= 0 for v in values) and any(v > 0 for v in values):
        return "f'' > 0 en [a, b] (curva convexa): el trapecio sobreestima la integral."
    return None


def _derivative_steps(expr, symbol, name):
    """Desglose término a término de Newton y diferenciación (d/dx de `expr`)."""
    steps = entry_steps(expr, symbol, name, ordinary=True)
    for term in steps["terms"]:
        term["rule"] = integral_module.symbolic_rule(term["rule"])
    return steps


def _info(function):
    second = function.derivatives[2]
    x = function.symbol
    return {
        "latex": expression_to_latex(function.typed),
        "text": expression_to_text(function.expr),
        # ∫ f dx lleva paréntesis sólo si f es una suma o resta.
        "is_sum": isinstance(function.expr, sp.Add),
        "uses_trigonometry": _uses_trigonometry(function.expr),
        "first": {"latex": expression_to_latex(function.first, order=None),
                  "text": expression_to_text(function.first),
                  "steps": _derivative_steps(function.expr, x, "f")},
        "second": {"latex": expression_to_latex(second, order=None), "text": expression_to_text(second),
                   "steps": _derivative_steps(function.first, x, "f'"),
                   "constant": not second.has(x)},
        "substitution_terms": integral_module.substituter(function.expr, x)[0],
    }


def _curve(function, a, b):
    xs = [a + (b - a) * i / (CURVE_POINTS - 1) for i in range(CURVE_POINTS)]
    return {"x": xs, "y": [function(x) for x in xs]}


def _integral(function, a, b):
    """Integral exacta o de referencia, con su rótulo y las notas que genera."""
    result = integral_module.definite_integral(function.expr, function.symbol, a, b)
    notes = []
    if result["kind"] == "reference":
        if result["special"]:
            notes.append(f"{result['special']}: se usa un {REFERENCE_LABEL}.")
        if result["timed_out"]:
            notes.append(
                f"La integración simbólica superó el límite de {integral_module.TIME_LIMIT:g} s: "
                f"se usa un {REFERENCE_LABEL}."
            )
    info = {
        "kind": result["kind"],
        "value": result["value"],
        "label": {"exact": "exacta", "reference": REFERENCE_LABEL}.get(result["kind"]),
        "special": result["special"],
        "timed_out": result["timed_out"],
        "antiderivative": None,
    }
    check = None
    if result["kind"] == "exact":
        F, x = result["F"], function.symbol
        info["antiderivative"] = {
            **integral_module.antiderivative_info(F, x),
            "steps": integral_module.antiderivative_steps(function.expr, F, x),
            "check": integral_module.derivative_check(function.expr, F, x),
        }
        check = {
            "upper": integral_module.substitution(F, x, b, display.data_value(b)),
            "lower": integral_module.substitution(F, x, a, display.data_value(a)),
        }
    return info, check, notes


def _errors(I, T, bound, rounding):
    """Eₜ, εₜ, |Eₜ| ≤ cota (+ R), si hizo falta R y si |Eₜ| = cota (None donde falta un dato).

    R sólo cuenta cuando |Eₜ| > cota·(1 + 10⁻⁹): una diferencia menor es la
    misma cota escrita en punto flotante (x² en [0, 2]: |Eₜ| = cota).
    """
    true = None if I is None else I - T + 0.0
    relative = None if true is None or abs(I) < ZERO_INTEGRAL else abs(true) / abs(I) * 100
    if true is None or bound is None:
        return true, relative, None, False, False
    size, margin = abs(true), bound * EQUAL_RELATIVE
    within = size <= bound + margin or size <= bound + rounding
    by_rounding = within and size > bound + margin
    equals = abs(size - bound) <= margin
    return true, relative, within, by_rounding, equals


# --- Modo función -----------------------------------------------------------------

def _function_mode(data, rule=TRAPEZOID):
    a, b = float(data["a"]), float(data["b"])
    n0, tolerance, max_rows = data["n0"], data["tolerance"], data["max_iterations"]
    function = _Function(parse_function_of_x(data["function"]), {rule.bound_derivative})

    errors = [
        f"f(x) no está definida en x = {_where(display.data_value(x))} (límite {name})."
        for x, name in ((a, "a"), (b, "b")) if function(x) is None
    ]
    if errors:
        raise IntegrationValidationError(errors)
    values = [function(_x(a, b, i, n0)) for i in range(n0 + 1)]
    if None in values:
        raise IntegrationValidationError(_undefined(_x_display(a, b, values.index(None), n0), a, b))

    warnings, notes = [], []
    integral, check, integral_notes = _integral(function, a, b)
    notes.extend(integral_notes)
    M2, x_M, second_values = _second_derivative(function, a, b, SAMPLES)
    concavity = _concavity_note(second_values)
    if concavity:
        notes.append(concavity)
    samples = [a + (b - a) * i / (SAMPLES - 1) for i in range(SAMPLES)]
    singular = next((x for x in samples if function(x) is None), None)
    if singular is not None:
        warnings.append(_undefined(display.data_value(singular), a, b))
        integral.update({"kind": None, "value": None, "label": None, "antiderivative": None})
        check = None
    I = integral["value"]

    fa, fb = _evaluate(function.evaluators[1], a), _evaluate(function.evaluators[1], b)
    mean_second = None if fa is None or fb is None else (fb - fa) / (b - a)
    width = b - a
    width_number = display.exact(b) - display.exact(a)
    _, f_terms = integral_module.substituter(function.expr, function.symbol)

    iterations, chart_rows = [], []
    previous = None
    grid = values if n0 <= CHART_MAX_N else None
    abs_sum = sum(w * abs(v) for w, v in zip(rule.weights(n0), values))
    converged = stopped = False

    for k in range(1, max_rows + 1):
        n = n0 * 2 ** (k - 1)
        if n > MAX_SEGMENTS:
            warnings.append(
                f"Se alcanzó el máximo de {MAX_SEGMENTS} segmentos (fila {k}): se detuvo el refinamiento."
            )
            stopped = True
            break
        h = width / n
        h_number, h_shown = _step(a, b, n)
        if k == 1:
            T = apply(rule, values, h)
            step = _first_step(rule, values, a, b, h_number, T, f_terms)
        else:
            new_values = [function(a + (2 * j - 1) * width / n) for j in range(1, n // 2 + 1)]
            if None in new_values:
                missing = 2 * new_values.index(None) + 1
                message = _undefined(_x_display(a, b, missing, n), a, b)
                if message not in warnings:
                    warnings.append(message)
                stopped = True
                break
            T = previous["T"] / 2 + h * math.fsum(new_values)
            abs_sum += 2 * sum(abs(v) for v in new_values)
            step = _recurrence_step(previous["T"], new_values, a, b, n, h_number, T, f_terms)
            if grid is not None and n <= CHART_MAX_N:
                grid = [grid[i // 2] if i % 2 == 0 else new_values[i // 2] for i in range(n + 1)]
            else:
                grid = None
        if grid is not None:
            chart_rows.append({"k": k, "n": n, "x": [_x(a, b, i, n) for i in range(n + 1)], "y": list(grid)})

        coefficient = width * h * h / 12
        bound = None if M2 is None else coefficient * M2
        rounding = 2 * MACHINE_EPSILON * float(rule.factor) * h * abs_sum
        true, relative, within, by_rounding, equals = _errors(I, T, bound, rounding)
        previous_true = previous["true_error"] if previous else None
        estimated = None if previous is None else abs(T - previous["T"])
        row = {
            "n": n,
            "h": h_shown,
            "T": T,
            "previous_T": previous["T"] if previous else None,
            "estimated_error": estimated,
            "true_error": true,
            "relative_error": relative,
            "approx_error": None if mean_second is None else -coefficient * mean_second + 0.0,
            "bound": bound,
            "rounding": rounding,
            "within_bound": within,
            "by_rounding": by_rounding,
            "equals_bound": equals,
            "below_tolerance": None if estimated is None else estimated <= tolerance,
            # (b − a)·h², el numerador de Eₐ y de la cota.
            "coefficient_numerator": display.decimal(width_number * h_number * h_number),
            "ratio": true / previous_true if true is not None and previous_true else None,
            "step": step,
        }
        iterations.append(IterationStep(iteration=k, x=[T], error=estimated, extra=row))
        previous = row
        if k >= MIN_REFINEMENTS and estimated is not None and estimated <= tolerance:
            converged = True
            break

    if I is None and singular is None:
        warnings.append(
            "No se pudo calcular la integral exacta ni un valor de referencia: no se muestran el error "
            "verdadero, el relativo ni la razón."
        )
    if M2 is None:
        warnings.append("f''(x) no es finita en todo [a, b]: no se muestra la cota del error.")
    if mean_second is None:
        notes.append("f'(a) o f'(b) no es finita: no se muestra el error aproximado Eₐ.")
    if not converged:
        tolerance_text = display.fixed(tolerance, 12)
        warnings.append(
            f"No se alcanzó la tolerancia del error estimado ({tolerance_text})."
            if stopped else
            f"No se alcanzó la tolerancia del error estimado ({tolerance_text}) en {len(iterations)} "
            "refinamientos. Aumenta el máximo de refinamientos o la tolerancia."
        )
    last = iterations[-1].extra
    if last["bound"] and last["rounding"] > last["bound"]:
        warnings.append(
            "El error de redondeo ya es comparable con el de truncamiento: aumentar n no mejora la aproximación."
        )

    failed = [step.iteration for step in iterations if step.extra["within_bound"] is False]
    verification = {
        **(check or {}),
        "kind": integral["kind"],
        "final": {key: last[key] for key in ("T", "true_error", "relative_error", "bound", "rounding",
                                              "within_bound", "by_rounding", "equals_bound")},
        "failed_rows": failed,
        "all_within": I is not None and M2 is not None and not failed,
    }
    meta = {
        "mode": "function",
        "a": a,
        "b": b,
        "a_display": display.data_value(a),
        "b_display": display.data_value(b),
        "width_display": display.decimal(display.exact(b) - display.exact(a)),
        "n0": n0,
        "tolerance": tolerance,
        "max_iterations": max_rows,
        "function": _info(function),
        "integral": integral,
        "min_rows": MIN_REFINEMENTS,
        "mean_second": None if mean_second is None else {
            "fa": fa, "fb": fb, "value": mean_second,
            # f'(a) y f'(b) sustituidas término a término.
            "fa_substitution": integral_module.substitution(function.first, function.symbol, a, display.data_value(a)),
            "fb_substitution": integral_module.substitution(function.first, function.symbol, b, display.data_value(b)),
        },
        "M2": None if M2 is None else {
            "value": M2, "x": x_M, "x_display": display.data_value(x_M),
            # f''(x) donde se alcanzó M₂, término a término (None si f'' es constante).
            "substitution": None if not function.derivatives[2].has(function.symbol) else
            integral_module.substitution(function.derivatives[2], function.symbol, x_M, display.data_value(x_M)),
        },
        "curve": _curve(function, a, b),
        "chart_rows": chart_rows,
        "notes": notes,
        "verification": verification,
    }
    return converged, iterations, warnings, meta


# --- Modo tabla -------------------------------------------------------------------

def _segment_bound(function, a, b, width):
    M, x_M, _ = _second_derivative(function, a, b, SEGMENT_SAMPLES)
    return (None, None, None) if M is None else (width ** 3 / 12 * M, M, x_M)


def _data_checks(function, xs, ys, warnings):
    """Cada dato contra la función para comparar; agrega una advertencia por dato que no coincide."""
    checks = []
    for i, (x, y) in enumerate(zip(xs, ys)):
        fx = function(x)
        ok = fx is not None and abs(y - fx) <= DATA_RELATIVE * max(1.0, abs(fx))
        checks.append({"i": i, "x_display": display.data_value(x), "y": y, "f": fx,
                       "difference": None if fx is None else abs(y - fx), "ok": ok})
        if not ok:
            warnings.append(
                f"Punto {i}: el dato no coincide con la función (y = {display.fixed(y)}, "
                f"f(x) = {'no definida' if fx is None else display.fixed(fx)}); puede ser un error de captura."
            )
    return checks


def _table_mode(data, rule=TRAPEZOID):
    xs = [float(x) for x, _ in data["points"]]
    ys = [float(y) for _, y in data["points"]]
    n = len(xs) - 1
    text = data.get("compare_function") or ""
    function = _Function(parse_function_of_x(text), {rule.bound_derivative}) if text else None

    iterations, warnings, notes = [], [], []
    cumulative, areas = 0.0, []
    bounds = []
    for i in range(n):
        width = xs[i + 1] - xs[i]
        area = width * (ys[i] + ys[i + 1]) / 2
        areas.append(area)
        cumulative = math.fsum(areas)
        width_number = display.exact(xs[i + 1]) - display.exact(xs[i])
        pair = display.exact(ys[i]) + display.exact(ys[i + 1])
        segment = {
            "i": i,
            "x": [xs[i], xs[i + 1]],
            "x_display": [display.data_value(xs[i]), display.data_value(xs[i + 1])],
            "width": {"value": width, **display.decimal(width_number)},
            "y": [ys[i], ys[i + 1]],
            "y_display": [display.data_value(ys[i]), display.data_value(ys[i + 1])],
            "pair_sum": display.decimal(pair)["text"],
            "area": area,
            "area_display": display.fixed(area),
            "cumulative": cumulative,
            "bound": None,
            "M": None,
        }
        if function is not None:
            bound, M, x_M = _segment_bound(function, xs[i], xs[i + 1], width)
            bounds.append(bound)
            segment.update({"bound": bound, "M": M, "x_M": x_M})
        iterations.append(IterationStep(iteration=i + 1, x=[cumulative], error=None, extra=segment))

    total = math.fsum(areas) + 0.0
    steps = [xs[i + 1] - xs[i] for i in range(n)]
    uniform = all(abs(s - steps[0]) <= UNIFORM_RELATIVE * abs(steps[0]) for s in steps)
    composite = None
    if uniform:
        h = steps[0]
        value = apply(rule, ys, h)
        h_number = display.exact(xs[1]) - display.exact(xs[0])
        interior = sum((display.exact(y) for y in ys[1:-1]), Decimal(0))
        bracket = display.exact(ys[0]) + 2 * interior + display.exact(ys[-1])
        composite = {
            "h": {"value": h, **display.decimal(h_number)},
            "value": value,
            "interior_sum": display.decimal(interior)["text"],
            "bracket": display.decimal(bracket)["text"],
            "half_h": display.decimal(h_number / 2)["text"],
            "equal": abs(value - total) <= 1e-12 * max(1.0, abs(total)),
        }
        notes.append(f"Espaciado uniforme (h = {composite['h']['text']}): se muestra también la fórmula compuesta.")
    else:
        notes.append("Espaciado no uniforme: cada trapecio usa su propio ancho.")

    integral = check = None
    data_checks = None
    final = None
    if function is not None:
        integral, check, integral_notes = _integral(function, xs[0], xs[-1])
        notes.extend(integral_notes)
        if integral["kind"] is None:
            warnings.append(
                "No se pudo calcular la integral exacta ni un valor de referencia de la función para comparar."
            )
        data_checks = _data_checks(function, xs, ys, warnings)
        bound = None if None in bounds else math.fsum(bounds)
        if bound is None:
            warnings.append("f''(x) no es finita en algún segmento: no se muestra la cota del error.")
        rounding = 2 * MACHINE_EPSILON * math.fsum(abs(s) * (abs(ys[i]) + abs(ys[i + 1])) / 2
                                                    for i, s in enumerate(steps))
        true, relative, within, by_rounding, equals = _errors(integral["value"], total, bound, rounding)
        final = {"T": total, "I": integral["value"], "true_error": true, "relative_error": relative,
                 "bound": bound, "rounding": rounding, "within_bound": within, "by_rounding": by_rounding,
                 "equals_bound": equals}

    verification = {
        **(check or {}),
        "kind": integral["kind"] if integral else None,
        # Áreas a 6 decimales: si su suma no da el total visible, la vista escribe «≈».
        "areas": [s.extra["area_display"] for s in iterations],
        "areas_sum": _plain(sum((Decimal(s.extra["area_display"]) for s in iterations), Decimal(0))),
        "total_display": display.fixed(total),
        "data": data_checks,
        "final": final,
        "all_within": bool(final) and final["within_bound"] is True,
    }
    meta = {
        "mode": "table",
        "points": [[x, y] for x, y in zip(xs, ys)],
        "a": xs[0],
        "b": xs[-1],
        "a_display": display.data_value(xs[0]),
        "b_display": display.data_value(xs[-1]),
        "total": total,
        "uniform": uniform,
        "composite": composite,
        "function": _info(function) if function else None,
        "integral": integral,
        "curve": _curve(function, xs[0], xs[-1]) if function else None,
        "chart_rows": [{"k": 1, "n": n, "x": xs, "y": ys}],
        "notes": notes,
        "verification": verification,
    }
    return True, iterations, warnings, meta


# --- Punto de entrada -------------------------------------------------------------

def solve_trapezoid(data):
    """Punto de entrada del registro: datos ya validados -> SolverResult."""
    mode = _table_mode if data["mode"] == "table" else _function_mode
    converged, iterations, warnings, meta = mode(data)
    return SolverResult(
        method=METHOD,
        category=CATEGORY,
        converged=converged,
        iterations=iterations,
        solution=[iterations[-1].x[0]],
        variables=["T"],
        warnings=warnings,
        meta={
            **meta,
            "rule": public_rule(TRAPEZOID),
            "sampling_points": SAMPLES if data["mode"] != "table" else SEGMENT_SAMPLES,
        },
    )
