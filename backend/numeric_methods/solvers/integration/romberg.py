"""Integración de Romberg (notación de Chapra y Canale, índices desde 1).

La columna 1 son trapecios con n = 2^(i−1) segmentos, calculados con la
recurrencia del trapecio (R_i,1 = R_(i−1),1/2 + h_i·Σ f(nuevos)); las demás
columnas son extrapolaciones de Richardson:

  R_i,k = (4^(k−1)·R_i,(k−1) − R_(i−1),(k−1)) / (4^(k−1) − 1),  k = 2, …, i

El mejor valor de cada fila es la diagonal R_i,i. Error estimado
|R_i,i − R_(i−1),(i−1)| (criterio de parada, con al menos MIN_ROWS filas) y
error aproximado de Chapra εₐ = |(R_i,i − R_(i−1),(i−1))/R_i,i|·100.

- «Función»: f(x), a, b, tolerancia y máximo de filas (siempre empieza con n = 1).
- «Tabla de datos»: 2ᵐ + 1 puntos igualmente espaciados (el serializer lo
  valida); m + 1 filas, la fila i usa uno de cada 2^(m−i+1) puntos.

Reutiliza del trapecio la recurrencia y su paso a paso, la integral exacta o
de referencia y la comprobación de los datos; de rules.py, la fórmula de
pesos del trapecio y de Simpson 1/3 (identidades de las columnas 1 y 2).

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
from ..differentiation.finite_differences import MACHINE_EPSILON, _Function, _uses_trigonometry, parse_function_of_x
from . import exact as integral_module
from .rules import SIMPSON_13, TRAPEZOID, apply
from .trapezoid import (
    CATEGORY,
    FOLD_FIRST_ROW,
    FOLD_NEW_POINTS,
    MIN_REFINEMENTS,
    SAMPLES,
    ZERO_INTEGRAL,
    IntegrationValidationError,
    _data_checks,
    _first_row_display,
    _first_step,
    _integral,
    _recurrence_display,
    _recurrence_step,
    _step,
    _undefined,
    _where,
    _x_display,
)

METHOD = "romberg"

DEFAULT_TOLERANCE = 0.000001
DEFAULT_MAX_ROWS = 15
MIN_ROWS = MIN_REFINEMENTS
MAX_ROWS = 20
# Modo tabla: 2ᵐ + 1 puntos.
TABLE_POINTS = (3, 5, 9, 17, 33)
MIN_POINTS = TABLE_POINTS[0]
MAX_POINTS = TABLE_POINTS[-1]
# Comparación de costo: el trapecio y Simpson duplican n hasta este límite.
COST_LIMIT = 2 ** 22
# ✔ de las identidades: diferencia ≤ 10⁻¹²·máx(1, |valor|).
IDENTITY_RELATIVE = 1e-12
# Advertencia de función poco suave: razón > 0.1 en las últimas 3 filas, sólo
# entre errores mayores que 1000·ε·máx(1, |R_i,i|) (más chicos son ruido de redondeo).
SMOOTH_RATIO = 0.1
SMOOTH_ROWS = 3
NOISE = 1000 * MACHINE_EPSILON
# Decimales del paso a paso de Richardson (el mínimo que haga coincidir el resultado).
STEP_DECIMALS = (6, 8, 10, 12)

NOT_SMOOTH = (
    "La diagonal mejora lentamente: f puede no ser suave en [a, b] (por ejemplo, una raíz cuadrada en 0 o un "
    "valor absoluto). Romberg funciona mejor con funciones suaves."
)
_SUPERSCRIPTS = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


# --- Columnas ---------------------------------------------------------------------

def column(k):
    """Nombre, orden del error y grado de exactitud de la columna k."""
    order = 2 * k
    return {
        "k": k,
        "name": {1: "Trapecio", 2: "Simpson 1/3", 3: "Boole"}.get(k, f"Nivel {k}"),
        "order": order,
        "order_latex": f"O(h^{{{order}}})",
        "order_text": f"O(h{str(order).translate(_SUPERSCRIPTS)})",
        "degree": order - 1,
    }


# --- Una fila de la tabla triangular --------------------------------------------------

def _extrapolation(k, same, previous, value):
    """R_i,k = (4^(k−1)·R_i,(k−1) − R_(i−1),(k−1))/(4^(k−1) − 1) con los valores visibles.

    Con 6 decimales y, si el resultado de los valores que se ven no coincide
    con el guardado (a 6), con 8, 10 o 12: el mínimo que haga coincidir.
    """
    factor = 4 ** (k - 1)
    target = display.fixed(value)
    for decimals in STEP_DECIMALS:
        same_shown, previous_shown = display.fixed(same, decimals), display.fixed(previous, decimals)
        product = factor * Decimal(same_shown)
        numerator = product - Decimal(previous_shown)
        quotient = _CONTEXT.divide(numerator, factor - 1)
        if display.fixed(float(quotient)) == target:
            break
    return {
        "k": k,
        "factor": factor,
        "divisor": factor - 1,
        "decimals": decimals,
        "same": same_shown,
        "previous": previous_shown,
        "product": _plain(product),
        "numerator": _plain(numerator),
        "quotient": display.fixed(float(quotient), decimals),
        "coherent": display.fixed(float(quotient)) == target,
        "value": value,
    }


def _row(i, n, h_shown, T, step, previous, I, tolerance):
    values, extrapolations = [T], []
    for k in range(2, i + 1):
        same, before = values[-1], previous["values"][k - 2]
        factor = 4 ** (k - 1)
        value = (factor * same - before) / (factor - 1)
        extrapolations.append(_extrapolation(k, same, before, value))
        values.append(value)
    best = values[-1]
    estimated = None if previous is None else abs(best - previous["best"])
    true = None if I is None else I - best + 0.0
    return {
        "i": i,
        "n": n,
        "h": h_shown,
        "evaluations": n + 1,
        "values": values,
        "best": best,
        "previous_best": previous["best"] if previous else None,
        # Eₜ = I − R_i,k de cada celda (la «tabla de errores»).
        "errors": None if I is None else [I - v + 0.0 for v in values],
        "estimated_error": estimated,
        "approx_error": None if estimated is None or abs(best) < ZERO_INTEGRAL else estimated / abs(best) * 100,
        "true_error": true,
        "relative_error": None if true is None or abs(I) < ZERO_INTEGRAL else abs(true) / abs(I) * 100,
        "below_tolerance": None if estimated is None else estimated <= tolerance,
        # La forma de una fila del trapecio: la usa su paso a paso (TrapezoidStepDetail).
        "trapezoid": {"n": n, "h": h_shown, "T": T, "estimated_error": None, "step": step},
        "extrapolations": extrapolations,
    }


def _identity(row, values, h):
    """R_i,1 = trapecio directo (fórmula de pesos) y R_i,2 = Simpson 1/3 (su motor), con n = 2^(i−1)."""
    def check(value, other):
        difference = abs(value - other)
        return {"value": value, "other": other, "difference": difference,
                "ok": difference <= IDENTITY_RELATIVE * max(1.0, abs(other))}

    return {
        "i": row["i"],
        "n": row["n"],
        "trapezoid": check(row["values"][0], apply(TRAPEZOID, values, h)),
        "simpson": check(row["values"][1], apply(SIMPSON_13, values, h)) if row["i"] >= 2 else None,
    }


def _smoothness_warning(rows):
    """True si en las últimas 3 filas la diagonal mejora lentamente (razón > 0.1).

    Hacen falta al menos 2 razones que cuenten: con una sola (una tabla de 9
    datos sólo tiene la de la fila 3) la razón de las primeras filas, todavía
    lejos de la convergencia, no dice nada de la suavidad de f.
    """
    ratios = []
    for index in range(max(1, len(rows) - SMOOTH_ROWS), len(rows)):
        e1, e0 = rows[index]["estimated_error"], rows[index - 1]["estimated_error"]
        noise = NOISE * max(1.0, abs(rows[index]["best"]))
        if e1 is not None and e0 is not None and e1 > noise and e0 > noise:
            ratios.append(e1 / e0)
    return len(ratios) >= 2 and all(r > SMOOTH_RATIO for r in ratios)


def _final(rows, I):
    last = rows[-1]
    return {"R": last["best"], "I": I, "true_error": last["true_error"], "relative_error": last["relative_error"]}


# --- Comparación de costo ------------------------------------------------------------

def _count(n):
    """2049 tal cual; 4194305 como «4 194 305»."""
    return f"{n:,}".replace(",", " ") if n > 9999 else str(n)


def _cost(function, a, b, I, tolerance, rows):
    """Evaluaciones de f de Romberg frente al trapecio (n desde 1) y Simpson 1/3
    (n desde 2) duplicando n hasta |Eₜ| ≤ tolerancia, con n ≤ COST_LIMIT.

    Los trapecios de la columna 1 se reutilizan y luego se sigue con la
    recurrencia; Simpson sale de S_n = (4T_n − T_(n/2))/3 (la columna 2).
    """
    first = next((row for row in rows if abs(I - row["best"]) <= tolerance), None)
    trapezoid = simpson = None
    width = b - a
    n, T, previous, j = 1, rows[0]["values"][0], None, 0
    while True:
        if trapezoid is None and abs(I - T) <= tolerance:
            trapezoid = n + 1
        if simpson is None and previous is not None and abs(I - (4 * T - previous) / 3) <= tolerance:
            simpson = n + 1
        if (trapezoid and simpson) or n >= COST_LIMIT:
            break
        previous, n, j = T, 2 * n, j + 1
        if j < len(rows):
            T = rows[j]["values"][0]
            continue
        h = width / n
        try:
            T = previous / 2 + h * math.fsum(function(a + (2 * m - 1) * h) for m in range(1, n // 2 + 1))
        except TypeError:  # f no definida en un punto nuevo
            break

    used = rows[-1]["evaluations"]
    tol = display.fixed(tolerance, 12)
    more = f"más de {_count(COST_LIMIT + 1)}"
    others = (f"el trapecio habría necesitado {_count(trapezoid) if trapezoid else more} y "
              f"Simpson {_count(simpson) if simpson else more}")
    if first is None:
        text = f"Romberg no llegó a |Eₜ| ≤ {tol} en sus {len(rows)} filas ({_count(used)} evaluaciones); {others}."
    else:
        text = (f"Romberg llegó a |Eₜ| ≤ {tol} en la fila {first['i']}, con {_count(first['evaluations'])} "
                f"evaluaciones; {others}.")
        if first["i"] < rows[-1]["i"]:
            text += (f" Por el mínimo de {MIN_ROWS} filas, el sistema usó {_count(used)}."
                     if first["i"] < MIN_ROWS else
                     f" El error estimado necesitó llegar a la fila {rows[-1]['i']}: el sistema usó {_count(used)}.")
    return {
        "romberg_evaluations": used,
        "first_row": first["i"] if first else None,
        "first_evaluations": first["evaluations"] if first else None,
        "trapezoid_evaluations": trapezoid,
        "simpson_evaluations": simpson,
        "limit": COST_LIMIT,
        "text": text,
    }


# --- Modo función -----------------------------------------------------------------

def _function_info(function):
    """Lo que necesita la vista: Romberg no usa derivadas."""
    return {
        "latex": expression_to_latex(function.typed),
        "text": expression_to_text(function.expr),
        "is_sum": isinstance(function.expr, sp.Add),
        "uses_trigonometry": _uses_trigonometry(function.expr),
        "substitution_terms": integral_module.substituter(function.expr, function.symbol)[0],
    }


def _function_mode(data):
    a, b = float(data["a"]), float(data["b"])
    tolerance, max_rows = data["tolerance"], data["max_iterations"]
    function = _Function(parse_function_of_x(data["function"]), set())

    errors = [
        f"f(x) no está definida en x = {_where(display.data_value(x))} (límite {name})."
        for x, name in ((a, "a"), (b, "b")) if function(x) is None
    ]
    if errors:
        raise IntegrationValidationError(errors)

    warnings, notes = [], []
    integral, check, integral_notes = _integral(function, a, b)
    notes.extend(integral_notes)
    samples = [a + (b - a) * i / (SAMPLES - 1) for i in range(SAMPLES)]
    singular = next((x for x in samples if function(x) is None), None)
    if singular is not None:
        warnings.append(_undefined(display.data_value(singular), a, b))
        integral.update({"kind": None, "value": None, "label": None, "antiderivative": None})
        check = None
    I = integral["value"]

    width = b - a
    _, f_terms = integral_module.substituter(function.expr, function.symbol)
    values = [function(a), function(b)]
    rows, iterations, identities = [], [], []
    converged = stopped = False
    for i in range(1, max_rows + 1):
        n = 2 ** (i - 1)
        h = width / n
        h_number, h_shown = _step(a, b, n)
        previous = rows[-1] if rows else None
        if i == 1:
            T = apply(TRAPEZOID, values, h)
            step = _first_step(TRAPEZOID, values, a, b, h_number, T, f_terms)
        else:
            new = [function(a + (2 * j - 1) * width / n) for j in range(1, n // 2 + 1)]
            if None in new:
                message = _undefined(_x_display(a, b, 2 * new.index(None) + 1, n), a, b)
                if message not in warnings:
                    warnings.append(message)
                stopped = True
                break
            T = previous["values"][0] / 2 + h * math.fsum(new)
            step = _recurrence_step(previous["values"][0], new, a, b, n, h_number, T, f_terms)
            merged = [None] * (n + 1)
            merged[0::2], merged[1::2] = values, new
            values = merged
        row = _row(i, n, h_shown, T, step, previous, I, tolerance)
        rows.append(row)
        identities.append(_identity(row, values, h))
        iterations.append(IterationStep(iteration=i, x=[row["best"]], error=row["estimated_error"], extra=row))
        if i >= MIN_ROWS and row["below_tolerance"]:
            converged = True
            break

    if I is None and singular is None:
        warnings.append(
            "No se pudo calcular la integral exacta ni un valor de referencia: no se muestran el error "
            "verdadero ni el relativo."
        )
    if not converged:
        tolerance_text = display.fixed(tolerance, 12)
        warnings.append(
            f"No se alcanzó la tolerancia del error estimado ({tolerance_text})."
            if stopped else
            f"No se alcanzó la tolerancia del error estimado ({tolerance_text}) en {len(rows)} filas. "
            "Aumenta el máximo de filas o la tolerancia."
        )
    if _smoothness_warning(rows):
        warnings.append(NOT_SMOOTH)

    meta = {
        "mode": "function",
        "a": a,
        "b": b,
        "a_display": display.data_value(a),
        "b_display": display.data_value(b),
        "width_display": display.decimal(display.exact(b) - display.exact(a)),
        "tolerance": tolerance,
        "max_iterations": max_rows,
        "function": _function_info(function),
        "integral": integral,
        "min_rows": MIN_ROWS,
        "columns": [column(k) for k in range(1, len(rows) + 1)],
        "evaluations": rows[-1]["evaluations"],
        "cost": None if I is None else _cost(function, a, b, I, tolerance, rows),
        "notes": notes,
        "verification": {**(check or {}), "kind": integral["kind"], "identities": identities,
                         "final": None if I is None else _final(rows, I)},
    }
    return converged, iterations, warnings, meta


# --- Modo tabla -------------------------------------------------------------------

def _data_point(xs, ys, j, decimals):
    return {"i": j, "x_display": display.data_value(xs[j]), "f": ys[j], "f_display": display.fixed(ys[j], decimals)}


def _table_mode(data):
    xs = [float(x) for x, _ in data["points"]]
    ys = [float(y) for _, y in data["points"]]
    count = len(xs)
    m = (count - 1).bit_length() - 1
    a, b = xs[0], xs[-1]
    text = data.get("compare_function") or ""
    function = _Function(parse_function_of_x(text), set()) if text else None

    warnings = []
    notes = [
        f"Con {count} puntos sólo se pueden armar {m + 1} filas: cada fila duplica los segmentos y la última ya usa "
        f"todos los datos. En el modo tabla no se aplica el mínimo de {MIN_ROWS} filas."
    ]
    integral = check = data_checks = None
    I = None
    if function is not None:
        integral, check, integral_notes = _integral(function, a, b)
        notes.extend(integral_notes)
        if integral["kind"] is None:
            warnings.append(
                "No se pudo calcular la integral exacta ni un valor de referencia de la función para comparar."
            )
        I = integral["value"]
        data_checks = _data_checks(function, xs, ys, warnings)

    width = b - a
    rows, iterations, identities = [], [], []
    for i in range(1, m + 2):
        n = 2 ** (i - 1)
        stride = (count - 1) // n
        used = list(range(0, count, stride))
        h = width / n
        h_number, h_shown = _step(a, b, n)
        previous = rows[-1] if rows else None
        if i == 1:
            ends = [ys[0], ys[-1]]
            T = apply(TRAPEZOID, ends, h)
            step = _first_row_display(TRAPEZOID, ends, h_number, T)
            step["points"] = [_data_point(xs, ys, j, step["decimals"]) for j in (0, count - 1)]
            step.update({"count": 2, "fold": FOLD_FIRST_ROW})
            new_points = used
        else:
            new_points = used[1::2]
            new = [ys[j] for j in new_points]
            T = previous["values"][0] / 2 + h * math.fsum(new)
            step = _recurrence_display(previous["values"][0], new, h_number, T)
            step["points"] = [_data_point(xs, ys, j, step["decimals"]) for j in new_points]
            step.update({"count": len(new), "fold": FOLD_NEW_POINTS})
        row = _row(i, n, h_shown, T, step, previous, I, data["tolerance"])
        row.update({"data_points": used, "new_points": new_points})
        rows.append(row)
        identities.append(_identity(row, ys[::stride], h))
        iterations.append(IterationStep(iteration=i, x=[row["best"]], error=row["estimated_error"], extra=row))

    if _smoothness_warning(rows):
        warnings.append(NOT_SMOOTH)
    meta = {
        "mode": "table",
        "points": [[x, y] for x, y in zip(xs, ys)],
        "a": a,
        "b": b,
        "a_display": display.data_value(a),
        "b_display": display.data_value(b),
        "width_display": display.decimal(display.exact(b) - display.exact(a)),
        "tolerance": data["tolerance"],
        "function": _function_info(function) if function else None,
        "integral": integral,
        "min_rows": MIN_ROWS,
        "columns": [column(k) for k in range(1, len(rows) + 1)],
        "evaluations": count,
        "cost": None,
        "notes": notes,
        "verification": {**(check or {}), "kind": integral["kind"] if integral else None, "data": data_checks,
                         "identities": identities, "final": None if I is None else _final(rows, I)},
    }
    return True, iterations, warnings, meta


# --- Punto de entrada -------------------------------------------------------------

def solve_romberg(data):
    """Punto de entrada del registro: datos ya validados -> SolverResult."""
    mode = _table_mode if data["mode"] == "table" else _function_mode
    converged, iterations, warnings, meta = mode(data)
    return SolverResult(
        method=METHOD,
        category=CATEGORY,
        converged=converged,
        iterations=iterations,
        solution=[iterations[-1].x[0]],
        variables=["R"],
        warnings=warnings,
        meta=meta,
    )
