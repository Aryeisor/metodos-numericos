"""Método de Simpson (reglas 1/3 y 3/8, simples y compuestas) para aproximar ∫ f en [a, b].

Las reglas son datos (rules.py: SIMPSON_13 y SIMPSON_38); aquí sólo se
aplican. Reutiliza del trapecio la integral exacta o de referencia, el
criterio de la marca R, el formato de h y de los puntos y el paso a paso de
la suma ponderada.

- «Función»: f(x), a, b, la regla («simpson13», «simpson38» o «both») y un n₀
  por regla (par en 1/3, múltiplo de 3 en 3/8). La fila k usa
  n_k = n₀·2^(k−1) en cada regla y se calcula con la fórmula de pesos; los
  valores de la fila anterior se reutilizan (son los xᵢ con i par). En cada
  fila: S, el error estimado |S_k − S_(k−1)|, Eₜ = I − S, εₜ, el Eₐ de Chapra
  −(b − a)h⁴/C·f̄⁽⁴⁾ (f̄⁽⁴⁾ = [f'''(b) − f'''(a)]/(b − a)), la cota
  (b − a)h⁴/C·M₄, la razón, el trapecio con el mismo n y, en 1/3, la
  identidad S_n = (4T_n − T_(n/2))/3. Se detiene cuando todas las reglas
  pedidas cumplen la tolerancia en la misma fila (con al menos 6 filas).
- «Tabla de datos»: puntos igualmente espaciados (el serializer lo valida).
  Con n segmentos: 1/3 si n es par, 3/8 si n es múltiplo de 3 y, con «both»
  y n impar, la combinación de Chapra (1/3 en los primeros n − 3 segmentos y
  3/8 en los últimos 3).

No depende de Django: puede usarse y testearse de forma aislada.
"""

import math
from decimal import Decimal

from ...expressions.to_latex import expression_to_latex
from ...expressions.to_text import expression_to_text
from ..base import IterationStep, SolverResult
from ..differentiation import display
from ..differentiation.display import _plain
from ..differentiation.finite_differences import MACHINE_EPSILON, _evaluate, _Function, parse_function_of_x
from . import exact as integral_module
from .rules import SIMPSON_13, SIMPSON_38, TRAPEZOID, apply, public_rule
from .trapezoid import (
    CATEGORY,
    CHART_MAX_N,
    FOLD_FIRST_ROW,
    MAX_SEGMENTS,
    MIN_REFINEMENTS,
    SAMPLES,
    IntegrationValidationError,
    _curve,
    _data_checks,
    _derivative_steps,
    _errors,
    _first_row_display,
    _info,
    _integral,
    _second_derivative,
    _shown_indices,
    _step,
    _undefined,
    _where,
    _x,
    _x_display,
)

METHOD = "simpson"

RULES = {rule.key: rule for rule in (SIMPSON_13, SIMPSON_38)}
RULE_CHOICES = {
    "simpson13": (SIMPSON_13,),
    "simpson38": (SIMPSON_38,),
    "both": (SIMPSON_13, SIMPSON_38),
}
N0_FIELDS = {"simpson13": "n0_13", "simpson38": "n0_38"}
DEFAULT_N0 = {"simpson13": 2, "simpson38": 3}
MIN_N0 = {"simpson13": 2, "simpson38": 3}
MAX_N0 = {"simpson13": 1000, "simpson38": 999}
MIN_POINTS = 3
# Puntos de cada parábola o cúbica en el gráfico.
PIECE_SAMPLES = 25
# El ✔ de la identidad con el trapecio: |(4T_n − T_(n/2))/3 − S| ≤ 10⁻⁹·máx(1, |S|).
IDENTITY_RELATIVE = 1e-9


def _public(rule):
    return {
        **public_rule(rule),
        "multiple": rule.segments_multiple,
        "divisor": rule.bound_divisor,
        "simple_divisor": rule.simple_divisor,
        "error_latex": rule.error_latex,
        "simple_error_latex": rule.simple_error_latex,
        "approx_latex": rule.approx_latex,
        "piece": rule.piece,
    }


# --- Piezas del gráfico: la parábola o la cúbica de cada grupo de puntos -------------

def _lagrange(xs, ys, x):
    total = 0.0
    for i, (xi, yi) in enumerate(zip(xs, ys)):
        term = yi
        for j, xj in enumerate(xs):
            if j != i:
                term *= (x - xj) / (xi - xj)
        total += term
    return total


def _pieces(xs, ys, parts):
    """Puntos muestreados del polinomio que pasa por cada grupo de puntos.
    `parts`: [(regla, inicio, fin)] con índices de xs."""
    pieces = []
    for rule, start, end in parts:
        m = rule.segments_multiple
        for s in range(start, end, m):
            px, py = xs[s:s + m + 1], ys[s:s + m + 1]
            sample = [px[0] + (px[-1] - px[0]) * t / (PIECE_SAMPLES - 1) for t in range(PIECE_SAMPLES - 1)] + [px[-1]]
            pieces.append({"rule": rule.key, "x": sample, "y": [_lagrange(px, py, x) for x in sample]})
    return pieces


# --- Datos de la función ---------------------------------------------------------

def _function_info(function):
    x = function.symbol
    third, fourth = function.derivatives[3], function.derivatives[4]
    return {
        **_info(function),
        "third": {"latex": expression_to_latex(third, order=None), "text": expression_to_text(third),
                  "steps": _derivative_steps(function.derivatives[2], x, "f''")},
        "fourth": {"latex": expression_to_latex(fourth, order=None), "text": expression_to_text(fourth),
                   "steps": _derivative_steps(third, x, "f'''"), "constant": not fourth.has(x)},
    }


def _concavity_note(values):
    """Eₜ = −k·f⁽⁴⁾(ξ) con k > 0: el signo de Eₜ es el opuesto al de f⁽⁴⁾."""
    if not values:
        return None
    if all(v <= 0 for v in values) and any(v < 0 for v in values):
        return "f⁽⁴⁾ < 0 en [a, b]: Simpson subestima la integral (Eₜ = −k·f⁽⁴⁾(ξ) con k > 0, así que Eₜ > 0)."
    if all(v >= 0 for v in values) and any(v > 0 for v in values):
        return "f⁽⁴⁾ > 0 en [a, b]: Simpson sobreestima la integral (Eₜ = −k·f⁽⁴⁾(ξ) con k > 0, así que Eₜ < 0)."
    return None


def _mean_fourth(function, a, b):
    """f̄⁽⁴⁾ = [f'''(b) − f'''(a)]/(b − a) con sus sustituciones; None si f''' no es finita."""
    fa, fb = _evaluate(function.evaluators[3], a), _evaluate(function.evaluators[3], b)
    if fa is None or fb is None:
        return None
    x, third = function.symbol, function.derivatives[3]
    return {
        "fa": fa, "fb": fb, "value": (fb - fa) / (b - a),
        "fa_substitution": integral_module.substitution(third, x, a, display.data_value(a)),
        "fb_substitution": integral_module.substitution(third, x, b, display.data_value(b)),
    }


def _M4(function, a, b, M, x_M):
    if M is None:
        return None
    fourth = function.derivatives[4]
    return {
        "value": M, "x": x_M, "x_display": display.data_value(x_M),
        # f⁽⁴⁾(x) donde se alcanzó M₄, término a término (None si f⁽⁴⁾ es constante).
        "substitution": None if not fourth.has(function.symbol) else
        integral_module.substitution(fourth, function.symbol, x_M, display.data_value(x_M)),
    }


def _identity(S, values, h):
    """S_n = (4T_n − T_(n/2))/3 (Simpson 1/3 es el trapecio con Richardson).
    El ✔ usa los valores sin redondear; la sustitución, los visibles."""
    T_n = apply(TRAPEZOID, values, h)
    T_half = apply(TRAPEZOID, values[::2], 2 * h)
    value = (4 * T_n - T_half) / 3
    shown = [display.fixed(T_n), display.fixed(T_half)]
    visible = (4 * Decimal(shown[0]) - Decimal(shown[1])) / 3
    return {
        "n": len(values) - 1,
        "T_n": T_n, "T_half": T_half, "value": value,
        "T_n_display": shown[0], "T_half_display": shown[1],
        "numerator_display": _plain(4 * Decimal(shown[0]) - Decimal(shown[1])),
        "value_display": display.fixed(float(visible)),
        "ok": abs(value - S) <= IDENTITY_RELATIVE * max(1.0, abs(S)),
    }


def _trapezoid_comparison(I, S_true, values, h):
    """El trapecio con el mismo n: T, su Eₜ y cuántas veces menor es el error de Simpson."""
    T = apply(TRAPEZOID, values, h)
    true = None if I is None else I - T + 0.0
    times = None
    if true is not None and S_true is not None and S_true != 0:
        times = abs(true) / abs(S_true)
    return {"T": T, "true_error": true, "times": times}


# --- Modo función -----------------------------------------------------------------

def _function_mode(data):
    a, b = float(data["a"]), float(data["b"])
    tolerance, max_rows = data["tolerance"], data["max_iterations"]
    rules = RULE_CHOICES[data["rule"]]
    function = _Function(parse_function_of_x(data["function"]), {2, 3, 4})

    errors = [
        f"f(x) no está definida en x = {_where(display.data_value(x))} (límite {name})."
        for x, name in ((a, "a"), (b, "b")) if function(x) is None
    ]
    if errors:
        raise IntegrationValidationError(errors)
    tracks = []
    for rule in rules:
        n0 = data[N0_FIELDS[rule.key]]
        values = [function(_x(a, b, i, n0)) for i in range(n0 + 1)]
        if None in values:
            raise IntegrationValidationError(_undefined(_x_display(a, b, values.index(None), n0), a, b))
        tracks.append({"rule": rule, "n0": n0, "values": values, "rows": [], "chart_rows": []})

    warnings, notes = [], []
    integral, check, integral_notes = _integral(function, a, b)
    notes.extend(integral_notes)
    M4, x_M, fourth_values = _second_derivative(function, a, b, SAMPLES, order=4)
    concavity = _concavity_note(fourth_values)
    if concavity:
        notes.append(concavity)
    samples = [a + (b - a) * i / (SAMPLES - 1) for i in range(SAMPLES)]
    singular = next((x for x in samples if function(x) is None), None)
    if singular is not None:
        warnings.append(_undefined(display.data_value(singular), a, b))
        integral.update({"kind": None, "value": None, "label": None, "antiderivative": None})
        check = None
    I = integral["value"]
    mean = _mean_fourth(function, a, b)
    width = b - a
    width_number = display.exact(b) - display.exact(a)
    _, f_terms = integral_module.substituter(function.expr, function.symbol)

    iterations = []
    converged = stopped = False
    for k in range(1, max_rows + 1):
        row_values = []
        for track in tracks:
            rule, n = track["rule"], track["n0"] * 2 ** (k - 1)
            if n > MAX_SEGMENTS:
                warnings.append(
                    f"Se alcanzó el máximo de {MAX_SEGMENTS} segmentos (fila {k}): se detuvo el refinamiento."
                )
                stopped = True
                break
            if k > 1:
                # Los puntos de la fila anterior son los xᵢ con i par: sólo se evalúan los nuevos.
                new = [function(a + (2 * j - 1) * width / n) for j in range(1, n // 2 + 1)]
                if None in new:
                    message = _undefined(_x_display(a, b, 2 * new.index(None) + 1, n), a, b)
                    if message not in warnings:
                        warnings.append(message)
                    stopped = True
                    break
                merged = [None] * (n + 1)
                merged[0::2], merged[1::2] = track["values"], new
                track["values"] = merged
            row_values.append(track["values"])
        if stopped:
            break

        x_row = []
        for track, values in zip(tracks, row_values):
            rule, n = track["rule"], len(values) - 1
            h = width / n
            h_number, h_shown = _step(a, b, n)
            S = apply(rule, values, h)
            weights = rule.weights(n)
            step = _first_row_display(rule, values, h_number, S)
            step.update({"count": n + 1, "fold": FOLD_FIRST_ROW, "points": []})
            for i in _shown_indices(n + 1, FOLD_FIRST_ROW):
                f_display = display.fixed(values[i], step["decimals"])
                step["points"].append({
                    "i": i, "x": _x(a, b, i, n), "x_display": _x_display(a, b, i, n), "f": values[i],
                    "f_display": f_display, "terms": f_terms(_x(a, b, i, n)), "weight": weights[i],
                    "product": display.product(weights[i], f_display),
                })
            if n <= CHART_MAX_N:
                xs = [_x(a, b, i, n) for i in range(n + 1)]
                track["chart_rows"].append({"k": k, "n": n, "x": xs, "y": list(values),
                                            "pieces": _pieces(xs, values, [(rule, 0, n)])})

            coefficient = width * h ** 4 / rule.bound_divisor
            bound = None if M4 is None else coefficient * M4
            abs_sum = math.fsum(w * abs(v) for w, v in zip(weights, values))
            rounding = 2 * MACHINE_EPSILON * float(rule.factor) * h * abs_sum
            true, relative, within, by_rounding, equals = _errors(I, S, bound, rounding)
            previous = track["rows"][-1] if track["rows"] else None
            previous_true = previous["true_error"] if previous else None
            estimated = None if previous is None else abs(S - previous["S"])
            row = {
                "k": k,
                "n": n,
                "h": h_shown,
                "S": S,
                "previous_S": previous["S"] if previous else None,
                "estimated_error": estimated,
                "true_error": true,
                "relative_error": relative,
                "approx_error": None if mean is None else -coefficient * mean["value"] + 0.0,
                "bound": bound,
                "rounding": rounding,
                "within_bound": within,
                "by_rounding": by_rounding,
                "equals_bound": equals,
                "below_tolerance": None if estimated is None else estimated <= tolerance,
                # (b − a)·h⁴, el numerador de Eₐ y de la cota.
                "coefficient_numerator": display.decimal(width_number * h_number ** 4),
                "ratio": true / previous_true if true is not None and previous_true else None,
                "trapezoid": _trapezoid_comparison(I, true, values, h),
                "identity": _identity(S, values, h) if rule is SIMPSON_13 else None,
                "step": step,
            }
            track["rows"].append(row)
            x_row.append(S)

        estimates = [track["rows"][-1]["estimated_error"] for track in tracks]
        iterations.append(IterationStep(iteration=k, x=x_row, error=None if None in estimates else max(estimates)))
        if k >= MIN_REFINEMENTS and None not in estimates and all(e <= tolerance for e in estimates):
            converged = True
            break

    if I is None and singular is None:
        warnings.append(
            "No se pudo calcular la integral exacta ni un valor de referencia: no se muestran el error "
            "verdadero, el relativo ni la razón."
        )
    if M4 is None:
        warnings.append("f⁽⁴⁾(x) no es finita en todo [a, b]: no se muestra la cota del error.")
    if mean is None:
        notes.append("f'''(a) o f'''(b) no es finita: no se muestra el error aproximado Eₐ.")
    if not converged:
        tolerance_text = display.fixed(tolerance, 12)
        warnings.append(
            f"No se alcanzó la tolerancia del error estimado ({tolerance_text})."
            if stopped else
            f"No se alcanzó la tolerancia del error estimado ({tolerance_text}) en {len(iterations)} "
            "refinamientos (todas las reglas deben cumplirla en la misma fila). Aumenta el máximo de "
            "refinamientos o la tolerancia."
        )
    if any(t["rows"][-1]["bound"] and t["rows"][-1]["rounding"] > t["rows"][-1]["bound"] for t in tracks):
        warnings.append(
            "El error de redondeo ya es comparable con el de truncamiento: aumentar n no mejora la aproximación."
        )

    blocks = []
    for track in tracks:
        rows, last = track["rows"], track["rows"][-1]
        failed = [row["k"] for row in rows if row["within_bound"] is False]
        blocks.append({
            "rule": _public(track["rule"]),
            "n0": track["n0"],
            "rows": rows,
            "chart_rows": track["chart_rows"],
            "verification": {
                "final": {key: last[key] for key in ("S", "true_error", "relative_error", "bound", "rounding",
                                                      "within_bound", "by_rounding", "equals_bound")},
                "failed_rows": failed,
                "all_within": I is not None and M4 is not None and not failed,
            },
        })
    meta = {
        "mode": "function",
        "a": a,
        "b": b,
        "a_display": display.data_value(a),
        "b_display": display.data_value(b),
        "width_display": display.decimal(width_number),
        "rule_choice": data["rule"],
        "tolerance": tolerance,
        "max_iterations": max_rows,
        "function": _function_info(function),
        "integral": integral,
        "min_rows": MIN_REFINEMENTS,
        "mean_fourth": mean,
        "M4": _M4(function, a, b, M4, x_M),
        "curve": _curve(function, a, b),
        "rules": blocks,
        "notes": notes,
        "verification": {**(check or {}), "kind": integral["kind"]},
    }
    return converged, iterations, warnings, meta


# --- Modo tabla -------------------------------------------------------------------

def _plan(n, choice):
    """Qué se aplica a una tabla de n segmentos: listas de partes (regla, inicio, fin) y notas."""
    if choice == "simpson13":
        if n % 2:
            raise IntegrationValidationError(
                f"Simpson 1/3 necesita un número par de segmentos, porque cada parábola ocupa 2 segmentos, y la "
                f"tabla tiene n = {n}. Elige «Ambas» (combina 1/3 y 3/8)"
                + (" o «Simpson 3/8» (n es múltiplo de 3)." if n % 3 == 0 else ".")
            )
        return [[(SIMPSON_13, 0, n)]], []
    if choice == "simpson38":
        if n % 3:
            raise IntegrationValidationError(
                f"Simpson 3/8 necesita un número de segmentos múltiplo de 3, porque cada cúbica ocupa 3 "
                f"segmentos, y la tabla tiene n = {n}. Elige "
                + ("«Simpson 1/3» (n es par) o «Ambas»." if n % 2 == 0 else "«Ambas» (combina 1/3 y 3/8).")
            )
        return [[(SIMPSON_38, 0, n)]], []
    plans, notes = [], []
    if n % 2 == 0:
        plans.append([(SIMPSON_13, 0, n)])
        notes.append(f"n = {n} es par: se aplica Simpson 1/3.")
    elif n > 3:
        plans.append([(SIMPSON_13, 0, n - 3), (SIMPSON_38, n - 3, n)])
        notes.append(
            f"n = {n} es impar: se combina Simpson 1/3 en los primeros n − 3 = {n - 3} segmentos y Simpson 3/8 "
            "en los últimos 3 (combinación de Chapra)."
        )
    if n % 3 == 0:
        plans.append([(SIMPSON_38, 0, n)])
        notes.append(
            "n = 3: sólo se aplica Simpson 3/8 (1/3 necesita un número par de segmentos)." if n == 3 else
            f"n = {n} es múltiplo de 3: también se aplica Simpson 3/8 en toda la tabla, por separado."
        )
    else:
        notes.append(f"n = {n} no es múltiplo de 3: no se aplica Simpson 3/8 en toda la tabla.")
    return plans, notes


def _part(rule, start, end, xs, ys, h, h_number, function):
    values = ys[start:end + 1]
    value = apply(rule, values, h)
    part = {
        "rule": rule.key,
        "name": rule.name,
        "start": start,
        "end": end,
        "x_display": [display.data_value(xs[start]), display.data_value(xs[end])],
        "n": end - start,
        "divisor": rule.bound_divisor,
        "width_display": display.decimal(display.exact(xs[end]) - display.exact(xs[start])),
        "value": value,
        "step": _first_row_display(rule, values, h_number, value),
        "abs_sum": math.fsum(w * abs(v) for w, v in zip(rule.weights(end - start), values)),
        "approx_error": None,
        "bound": None,
        "mean_fourth": None,
        "M4": None,
    }
    if function is not None:
        pa, pb = xs[start], xs[end]
        coefficient = (pb - pa) * h ** 4 / rule.bound_divisor
        mean = _mean_fourth(function, pa, pb)
        M, x_M, _ = _second_derivative(function, pa, pb, SAMPLES, order=4)
        part.update({
            "coefficient_numerator": display.decimal(
                (display.exact(pb) - display.exact(pa)) * h_number ** 4),
            "approx_error": None if mean is None else -coefficient * mean["value"] + 0.0,
            "bound": None if M is None else coefficient * M,
            "mean_fourth": mean,
            "M4": _M4(function, pa, pb, M, x_M),
        })
    return part


def _application(parts, xs, ys, h, h_number, function, I):
    single = len(parts) == 1
    computed = [_part(rule, s, e, xs, ys, h, h_number, function) for rule, s, e in parts]
    total = math.fsum(p["value"] for p in computed) + 0.0
    points = []
    for i, (x, y) in enumerate(zip(xs, ys)):
        weights = [{"rule": rule.key, "weight": rule.weight(i - s, e - s)} for rule, s, e in parts if s <= i <= e]
        y_shown = display.data_value(y)
        points.append({
            "i": i, "x_display": display.data_value(x), "y": y, "y_display": y_shown,
            "weights": weights,
            "products": [_plain(w["weight"] * display.exact(y)) for w in weights],
        })
    application = {
        "key": parts[0][0].key if single else "combined",
        "name": parts[0][0].name if single else "Simpson 1/3 + 3/8",
        "parts": computed,
        "points": points,
        "total": total,
        "total_display": display.fixed(total),
        "parts_sum_display": _plain(sum((Decimal(display.fixed(p["value"])) for p in computed), Decimal(0))),
        "identity": _identity(total, ys, h) if single and parts[0][0] is SIMPSON_13 else None,
        "chart_row": {"k": 1, "n": len(xs) - 1, "x": xs, "y": ys, "pieces": _pieces(xs, ys, parts)},
        "final": None,
    }
    if function is not None:
        approx = [p["approx_error"] for p in computed]
        bounds = [p["bound"] for p in computed]
        bound = None if None in bounds else math.fsum(bounds)
        rounding = 2 * MACHINE_EPSILON * math.fsum(float(RULES[p["rule"]].factor) * h * p["abs_sum"] for p in computed)
        true, relative, within, by_rounding, equals = _errors(I, total, bound, rounding)
        application["final"] = {
            "S": total, "I": I, "true_error": true, "relative_error": relative,
            "approx_error": None if None in approx else math.fsum(approx) + 0.0,
            "bound": bound, "rounding": rounding, "within_bound": within, "by_rounding": by_rounding,
            "equals_bound": equals,
        }
    return application


def _table_mode(data):
    xs = [float(x) for x, _ in data["points"]]
    ys = [float(y) for _, y in data["points"]]
    n = len(xs) - 1
    plans, notes = _plan(n, data["rule"])
    text = data.get("compare_function") or ""
    function = _Function(parse_function_of_x(text), {2, 3, 4}) if text else None

    h = (xs[-1] - xs[0]) / n
    h_number = display.exact(xs[1]) - display.exact(xs[0])
    warnings = []
    integral = check = data_checks = None
    I = None
    if function is not None:
        integral, check, integral_notes = _integral(function, xs[0], xs[-1])
        notes.extend(integral_notes)
        if integral["kind"] is None:
            warnings.append(
                "No se pudo calcular la integral exacta ni un valor de referencia de la función para comparar."
            )
        I = integral["value"]
        data_checks = _data_checks(function, xs, ys, warnings)

    applications = [_application(parts, xs, ys, h, h_number, function, I) for parts in plans]
    if function is not None and any(p["bound"] is None for app in applications for p in app["parts"]):
        warnings.append("f⁽⁴⁾(x) no es finita en alguna parte: no se muestra la cota del error.")
    iterations = [IterationStep(iteration=i + 1, x=[app["total"]], error=None) for i, app in enumerate(applications)]
    meta = {
        "mode": "table",
        "points": [[x, y] for x, y in zip(xs, ys)],
        "a": xs[0],
        "b": xs[-1],
        "a_display": display.data_value(xs[0]),
        "b_display": display.data_value(xs[-1]),
        "n": n,
        "h": {"value": h, **display.decimal(h_number)},
        "rule_choice": data["rule"],
        "applications": applications,
        "function": _function_info(function) if function else None,
        "integral": integral,
        "curve": _curve(function, xs[0], xs[-1]) if function else None,
        "notes": notes,
        "verification": {**(check or {}), "kind": integral["kind"] if integral else None, "data": data_checks},
    }
    return True, iterations, warnings, meta


# --- Punto de entrada -------------------------------------------------------------

def solve_simpson(data):
    """Punto de entrada del registro: datos ya validados -> SolverResult."""
    table = data["mode"] == "table"
    converged, iterations, warnings, meta = (_table_mode if table else _function_mode)(data)
    names = [app["name"] for app in meta["applications"]] if table else [b["rule"]["name"] for b in meta["rules"]]
    return SolverResult(
        method=METHOD,
        category=CATEGORY,
        converged=converged,
        iterations=iterations,
        solution=[step.x[0] for step in iterations] if table else list(iterations[-1].x),
        variables=names,
        warnings=warnings,
        meta={**meta, "sampling_points": SAMPLES},
    )
