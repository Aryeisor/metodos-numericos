"""Fórmula de 5 puntos para aproximar f'(x₀): punto medio y extremos, O(h⁴).

Usa el mismo motor que las diferencias y la de 3 puntos (finite_differences.py)
con sus fórmulas (formulas.py), la regla de redondeo y el paso a paso con
productos de la de 3 puntos (three_point.py), y agrega lo propio:

- la comparación con el punto medio de 3 puntos, la progresiva y la regresiva;
- la identidad de Richardson del punto medio, D₅(h) = (4·D₃(h) − D₃(2h))/3
  (los extremos no tienen identidad: sólo error ≤ cota);
- en el modo tabla, el punto medio de 3 puntos como columna de referencia y
  la columna «Recomendada» (medio 5 → extremo 5 → medio 3);
- los datos del paso a paso explicado (three_point.explain: h⁴, signo de
  f⁽⁵⁾, lado de la aproximación) y el patrón entre derivadas seguidas.

No depende de Django: puede usarse y testearse de forma aislada.
"""

from decimal import Decimal

import sympy as sp

from ...expressions.to_latex import expression_to_latex
from . import display
from .finite_differences import _function_mode, _table_points, bound_check_equal, build_result
from .formulas import (
    BACKWARD_ENDPOINT_5,
    FIVE_POINT,
    FIVE_POINT_CHOICES,
    FORWARD_ENDPOINT_5,
    MIDPOINT,
    MIDPOINT_3_REFERENCE,
    MIDPOINT_5,
)
from .three_point import (
    DIFFERENCE_REFERENCES,
    IDENTITY_RELATIVE,
    ROUNDING_TEXT,
    _comparison,
    _decorate,
    explain,
    rounding,
)

METHOD = "cinco-puntos"
DEFAULT_TOLERANCE = 1e-6
MIN_POINTS = 5
# f'' a f⁽⁴⁾ se calculan además de f⁽⁵⁾ (la de la cota), para el desglose
# término a término de cada derivada desde la anterior.
DERIVATIVE_ORDERS = (2, 3, 4)
COMPARISON_REFERENCES = (
    (MIDPOINT, "midpoint_3", "fórmula de 3 puntos (punto medio)", "fórmula de 3 puntos"),
    *DIFFERENCE_REFERENCES,
)
COMPARISON_TITLE = "Comparación con la fórmula de 3 puntos y las diferencias progresiva y regresiva"
# Columnas del modo tabla: las pedidas y el punto medio de 3 puntos de referencia.
TABLE_CHOICES = {key: formulas + (MIDPOINT_3_REFERENCE,) for key, formulas in FIVE_POINT_CHOICES.items()}
_UNIT = Decimal("0.000001")


def _richardson(f, h, D):
    """D₅(h) = (4·D₃(h) − D₃(2h))/3, con D₃(h) = [f(x₀ + h) − f(x₀ − h)]/(2h).

    `f` da f(x₀ + o·h) por desplazamiento o; None si falta un valor. El ✔ se
    decide sin redondear; el resultado mostrado se calcula con los valores
    mostrados (6 decimales) y, si difiere de D₅ mostrado en una unidad del
    sexto decimal, se marca como diferencia por redondeo.
    """
    if any(f.get(o) is None for o in (-2, -1, 1, 2)):
        return None
    base = (f[1] - f[-1]) / (2 * h)
    double = (f[2] - f[-2]) / (4 * h)
    value = (4 * base - double) / 3
    shown = {name: display.fixed(v) for name, v in (("base", base), ("double", double), ("D", D))}
    value_shown = display.fixed((4 * Decimal(shown["base"]) - Decimal(shown["double"])) / 3)
    units = abs(Decimal(value_shown) - Decimal(shown["D"])) / _UNIT
    return {
        "key": MIDPOINT_5.key,
        "name": MIDPOINT_5.name,
        "kind": "romberg",
        "base": base,
        "double": double,
        "value": value,
        "D": D,
        "base_display": shown["base"],
        "double_display": shown["double"],
        "value_display": value_shown,
        "D_display": shown["D"],
        "rounding_difference": units == 1,
        "ok": abs(value - D) <= IDENTITY_RELATIVE * max(1.0, abs(value)),
    }


def _pattern(function):
    """f⁽ⁿ⁺¹⁾ − f⁽ⁿ⁾ si es la misma expresión (≠ 0) de f′ a f⁽⁵⁾, para la frase
    del patrón (en x·eˣ cada derivada es la anterior más eˣ); si no, None."""
    d = function.derivatives
    differences = {sp.simplify(d[n + 1] - d[n]) for n in range(1, 5)}
    if len(differences) != 1:
        return None
    (difference,) = differences
    return None if difference == 0 else {"latex": expression_to_latex(difference, order=None)}


def _function(data):
    function, formulas, converged, iterations, warnings, meta = _function_mode(
        data, FIVE_POINT_CHOICES, rounding, derivative_orders=DERIVATIVE_ORDERS, bound_check=bound_check_equal
    )
    for step in iterations:
        for formula in formulas:
            _decorate(step.extra[formula.key], step.extra["h"], formula)

    x0, identities = data["x0"], []
    if iterations and MIDPOINT_5 in formulas:
        first = iterations[0].extra
        h = first["h"]["value"]
        item = _richardson({o: function(x0 + o * h) for o in (-2, -1, 1, 2)}, h, first[MIDPOINT_5.key]["D"])
        identities = [item] if item else []
    meta["verification"]["identities"] = identities
    meta["comparison"] = _comparison(
        function, formulas, x0, iterations, meta["exact"], COMPARISON_REFERENCES, "la fórmula de 5 puntos"
    ) if iterations else []
    meta["comparison_title"] = COMPARISON_TITLE
    meta["rounding_text"] = ROUNDING_TEXT["function"]
    meta["derivative_pattern"] = _pattern(function)
    explain(function, formulas, iterations, meta, data)
    return function, formulas, converged, iterations, warnings, meta


def _recommended(extra):
    """Punto medio de 5 puntos; si no, el extremo de 5 puntos (adelante si
    existe, si no atrás); si no hay ninguna de 5 puntos, el medio de 3."""
    order = (MIDPOINT_5, FORWARD_ENDPOINT_5, BACKWARD_ENDPOINT_5, MIDPOINT_3_REFERENCE)
    formula = next(f for f in order if extra[f.key])
    return {"key": formula.key, "name": formula.name, "D": extra[formula.key]["D"]}


def _table(data):
    # Se calculan todas siempre: la columna «Recomendada» y la identidad las usan.
    function, formulas, xs, iterations, warnings, verification = _table_points(
        data, TABLE_CHOICES, FIVE_POINT + (MIDPOINT_3_REFERENCE,), rounding, derivative_orders=DERIVATIVE_ORDERS,
        bound_check=bound_check_equal,
    )
    ys = [float(y) for _, y in data["points"]]
    identities = []
    for step in iterations:
        i, extra = step.iteration - 1, step.extra
        for formula in FIVE_POINT + (MIDPOINT_3_REFERENCE,):
            if extra[formula.key]:
                _decorate(extra[formula.key], extra[formula.key]["h"], formula)
        extra["recommended"] = _recommended(extra)
        row = extra[MIDPOINT_5.key]
        items = []
        if row:
            f = {o: ys[i + o] for o in (-2, -1, 1, 2)}
            items.append(_richardson(f, row["h"]["value"], row["D"]))
        identities.append({"i": step.iteration, "x_display": extra["x_display"], "items": items})

    meta = {
        "mode": "table",
        "points": [[x, y] for x, y in zip(xs, ys)],
        "uniform": True,
        "verification": {**verification, "identities": identities},
        "rounding_text": ROUNDING_TEXT["table"],
        "derivative_pattern": _pattern(function) if function else None,
    }
    explain(function, FIVE_POINT + (MIDPOINT_3_REFERENCE,), iterations, meta, data)
    return function, formulas, True, iterations, warnings, meta


def solve_five_point(data):
    """Punto de entrada del registro: datos ya validados -> SolverResult."""
    mode = _table if data["mode"] == "table" else _function
    return build_result(METHOD, data, mode(data))
