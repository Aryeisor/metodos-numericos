"""Diferencias finitas para aproximar f'(x₀): progresiva y regresiva.

Dos modos de entrada:

- «Función»: f(x), x₀ y h₀. Tabla de refinamiento: la fila k usa
  h_k = h₀ / 2^(k−1). Para cada fórmula pedida se calcula la aproximación D_k,
  el error estimado |D_k − D_(k−1)|, el error real |D_k − f'(x₀)|, la cota
  teórica c·h^p·M_k (M_k = máx |f⁽ⁿ⁾| estimado por muestreo en el intervalo
  de la fila) y la razón entre errores reales consecutivos. Se detiene cuando
  el error estimado de todas las fórmulas es ≤ tolerancia, con al menos
  MIN_ITERATIONS filas.
- «Tabla de datos»: puntos (xᵢ, yᵢ). En cada xᵢ, cada fórmula usa sus
  vecinos, con su propio h. Con una función para comparar se agregan la
  derivada exacta, el error real y la cota.

Las fórmulas son datos (ver formulas.py): este módulo no conoce ninguna en
particular. La derivada exacta f'(x) y f⁽ⁿ⁾(x) se calculan simbólicamente una
sola vez y se evalúan con `lambdify`.

No depende de Django: puede usarse y testearse de forma aislada.
"""

import math
from decimal import Decimal

import sympy as sp
from sympy.functions.elementary.trigonometric import (
    InverseTrigonometricFunction,
    TrigonometricFunction,
)

from ...expressions.differentiate import derivative
from ...expressions.normalize import evaluate_tree
from ...expressions.parser import ExpressionError, make_symbols, parse_equation
from ...expressions.to_latex import expression_to_latex, substitution_template_latex
from ...expressions.to_text import expression_to_text
from ..base import IterationStep, SolverResult
from ..nonlinear.common import to_real
from ..nonlinear.derivative_steps import entry_steps
from ..nonlinear.verification import verification as substitution_check
from ..validation import MIN_ITERATIONS, InputValidationError
from . import display
from .formulas import BACKWARD, CHOICES, FORWARD, public_formula

CATEGORY = "differentiation"
METHOD = "diferencias-finitas"
VARIABLE = "x"

DEFAULT_H0 = 0.1
DEFAULT_TOLERANCE = 0.0001
DEFAULT_MAX_REFINEMENTS = 25
MIN_REFINEMENTS = MIN_ITERATIONS
MAX_REFINEMENTS = 30
MIN_POINTS = 2
MAX_POINTS = 20

# Puntos equiespaciados (extremos incluidos) para estimar máx |f⁽ⁿ⁾|.
SAMPLES = 401
MACHINE_EPSILON = 2.220446049250313e-16
# |yᵢ − f(xᵢ)| ≤ DATA_RELATIVE · máx(1, |f(xᵢ)|) para «el dato coincide».
DATA_RELATIVE = 1e-6
# Espaciado uniforme: |hᵢ − h₁| ≤ UNIFORM_RELATIVE · |h₁|.
UNIFORM_RELATIVE = 1e-9

PLACEHOLDER = "@@0@@"
# sympy deriva |u| como sign(u) y luego como DiracDelta(u), que math y mpmath
# no conocen. Fuera del pliegue vale 0; el pliegue se detecta aparte
# (ver `_has_kink`), así que aquí basta con 0.
_MODULES = [{"DiracDelta": lambda *args: 0.0}, "math", "mpmath"]


class DifferentiationValidationError(InputValidationError):
    """Entrada que no permite aplicar las fórmulas de diferencias."""


# --- Expresiones ---------------------------------------------------------------

def parse_function_of_x(text):
    """f(x) escrita por el usuario, en la forma evaluada de sympy.

    Acepta "ln(x)" o "f(x) = ln(x)"; no una ecuación con dos lados.
    """
    try:
        _, expr, rhs = parse_equation(text, [VARIABLE])
    except ExpressionError as exc:
        raise DifferentiationValidationError(str(exc)) from exc
    if rhs is not None:
        raise DifferentiationValidationError(
            "Escribe sólo la expresión de f(x), sin '=' (o en la forma f(x) = …)."
        )
    return expr


def _lambdify(symbol, expr):
    return sp.lambdify([symbol], expr, modules=_MODULES)


def _evaluate(function, x):
    try:
        return to_real(function(x))
    except (ArithmeticError, ValueError, TypeError):
        return None


def _uses_trigonometry(expr):
    trig = (TrigonometricFunction, InverseTrigonometricFunction)
    return any(isinstance(atom, trig) for atom in expr.atoms(sp.Function))


class _Function:
    """f, sus derivadas simbólicas (calculadas una vez) y sus evaluadores."""

    def __init__(self, typed, bound_orders):
        (self.symbol,) = make_symbols([VARIABLE]).values()
        self.typed = typed
        self.expr = evaluate_tree(typed)
        self.first = derivative(self.expr, self.symbol)
        self.derivatives = {1: self.first}
        for n in sorted(bound_orders):
            expr = self.expr
            for _ in range(n):
                expr = sp.diff(expr, self.symbol)
            self.derivatives[n] = expr
        self.f = _lambdify(self.symbol, self.expr)
        self.evaluators = {n: _lambdify(self.symbol, d) for n, d in self.derivatives.items()}
        self.kinks = [_lambdify(self.symbol, a.args[0]) for a in self.expr.atoms(sp.Abs)]

    def __call__(self, x):
        return _evaluate(self.f, x)

    def exact_derivative(self, x0):
        """f'(x₀), o None si f no es derivable en x₀."""
        value = _evaluate(self.evaluators[1], x0)
        if value is None or any(_evaluate(kink, x0) == 0 for kink in self.kinks):
            return None
        return value

    def _has_kink(self, a, b, samples):
        """Algún |u| con u = 0 o con cambio de signo en [a, b]."""
        for kink in self.kinks:
            values = [_evaluate(kink, x) for x in samples]
            if None in values or 0 in values:
                return True
            if min(values) < 0 < max(values):
                return True
        return False

    def max_abs(self, n, a, b):
        """(M, x) con M = máx |f⁽ⁿ⁾| en [a, b] por muestreo; (None, None) si
        f⁽ⁿ⁾ no es finita en algún punto muestreado."""
        expr = self.derivatives[n]
        samples = [a + (b - a) * i / (SAMPLES - 1) for i in range(SAMPLES)]
        if self._has_kink(a, b, samples):
            return None, None
        if expr.is_number:
            value = to_real(expr)
            return (None, None) if value is None else (abs(value), a)
        best, where = -1.0, a
        for x in samples:
            value = _evaluate(self.evaluators[n], x)
            if value is None:
                return None, None
            if abs(value) > best:
                best, where = abs(value), x
        return best, where

    def info(self):
        x = self.symbol
        return {
            "latex": expression_to_latex(self.typed),
            "text": expression_to_text(self.expr),
            "template": substitution_template_latex(self.typed, {x: PLACEHOLDER}),
            "uses_trigonometry": _uses_trigonometry(self.expr),
            "derivative": {
                "latex": expression_to_latex(self.first, order=None),
                "text": expression_to_text(self.first),
                # Desglose término a término, el mismo de las parciales de Newton.
                "steps": entry_steps(self.expr, x, "f", ordinary=True),
            },
            "higher_derivatives": {
                str(n): {"latex": expression_to_latex(d, order=None), "text": expression_to_text(d)}
                for n, d in self.derivatives.items() if n > 1
            },
        }


def _bound_orders(formulas):
    return {formula.bound_derivative for formula in formulas}


def _interval(formula, x0, h):
    offsets = [offset for offset, _ in formula.nodes]
    return x0 + min(offsets) * h, x0 + max(offsets) * h


def _rounding(formula, values, h):
    """R = 2ε·Σ|wᵢ|·máx|f(·)| / (q·h): 4ε·máx(|f(a)|, |f(b)|)/h en las de dos puntos."""
    weights = sum(abs(w) for _, w in formula.nodes)
    return 2 * MACHINE_EPSILON * weights * max(abs(v) for v in values) / (formula.divisor * h)


def _bound_check(real_error, bound, rounding):
    """(error real ≤ cota + R, sólo gracias a R); (None, False) si falta un dato."""
    if real_error is None or bound is None:
        return None, False
    within = real_error <= bound + rounding
    return within, within and real_error > bound


def _point_role(offset):
    if offset == 0:
        return "x_0"
    sign = "+" if offset > 0 else "-"
    factor = "" if abs(offset) == 1 else str(abs(offset))
    return f"x_0 {sign} {factor}h"


def _point_role_text(offset):
    return _point_role(offset).replace("x_0", "x₀").replace("-", "−")


def _approximation(formula, values, h_number, h):
    """D, el desglose coherente del paso a paso y el valor de cada nodo."""
    weights = [w for _, w in formula.nodes]
    D = sum(w * v for w, v in zip(weights, values)) / (formula.divisor * h) + 0.0
    step = display.coherent_step(values, weights, formula.divisor * h_number, D)
    return D, step


# --- Modo función --------------------------------------------------------------

def _check_domain(function, formulas, x0, h0):
    """Antes de empezar: f definida en x₀ y en los puntos de la fila 1."""
    h_number, h_shown = display.step_size(h0, 1)
    errors, seen = [], set()
    for formula in formulas:
        for offset, _ in formula.nodes:
            if offset in seen:
                continue
            seen.add(offset)
            x = x0 + offset * h0
            if offset != 0 and x == x0:
                errors.append(
                    "h₀ es demasiado pequeño para la precisión de la computadora: "
                    f"x₀ {'+' if offset > 0 else '−'} h₀ es igual a x₀."
                )
            elif function(x) is None:
                shown = display.point(x0, offset, h_number, h_shown)
                where = shown["text"] if shown["exact"] else f"{shown['approx']}"
                errors.append(
                    f"f(x) no está definida en x = {where} (punto {_point_role_text(offset)})."
                )
    if errors:
        raise DifferentiationValidationError(errors)


def _refinement_row(function, formula, x0, h, h_number, h_shown, k, exact, previous):
    points = []
    for offset, weight in formula.nodes:
        x = x0 + offset * h
        points.append({"offset": offset, "weight": weight, "role": _point_role(offset),
                       "x": x, "display": display.point(x0, offset, h_number, h_shown)})
    if any(p["offset"] != 0 and p["x"] == x0 for p in points):
        return None, "tiny"
    values = [function(p["x"]) for p in points]
    if None in values:
        missing = next(p for p, v in zip(points, values) if v is None)
        where = missing["display"]["text"] if missing["display"]["exact"] else missing["display"]["approx"]
        return None, f"f(x) no está definida en x = {where} (punto {_point_role_text(missing['offset'])}, fila {k})"

    D, step = _approximation(formula, values, h_number, h)
    for p, value, shown in zip(points, values, step["values"]):
        p.update({"f": value, "f_display": shown})

    a, b = _interval(formula, x0, h)
    M, x_M = function.max_abs(formula.bound_derivative, a, b)
    bound = None if M is None else float(formula.bound_coefficient) * h ** formula.order * M
    real = None if exact is None else abs(D - exact)
    rounding = _rounding(formula, values, h)
    within, by_rounding = _bound_check(real, bound, rounding)

    previous_D = previous["D"] if previous else None
    previous_real = previous["real_error"] if previous else None
    ratio = None
    if real is not None and previous_real:
        ratio = real / previous_real

    return {
        "D": D,
        "previous_D": previous_D,
        "estimated_error": None if previous_D is None else abs(D - previous_D),
        "real_error": real,
        "bound": bound,
        "M": M,
        # f⁽ⁿ⁾ sustituida en x_M: de dónde sale M en el paso a paso.
        "M_substitution": None if M is None else _substitution(function, x_M, formula.bound_derivative),
        "x_M": x_M,
        "interval": [a, b],
        "interval_display": [
            display.point(x0, min(o for o, _ in formula.nodes), h_number, h_shown),
            display.point(x0, max(o for o, _ in formula.nodes), h_number, h_shown),
        ],
        "ratio": ratio,
        "rounding": rounding,
        "within_bound": within,
        "by_rounding": by_rounding,
        "points": points,
        "decimals": step["decimals"],
        "numerator_display": step["numerator"],
    }, None


def _function_mode(data):
    formulas = CHOICES[data["formula"]]
    x0, h0 = data["x0"], data["h0"]
    tolerance, max_rows = data["tolerance"], data["max_iterations"]
    function = _Function(parse_function_of_x(data["function"]), _bound_orders(formulas))
    _check_domain(function, formulas, x0, h0)

    exact = function.exact_derivative(x0)
    warnings, iterations = [], []
    previous = {formula.key: None for formula in formulas}
    undefined_second = {}
    converged = stopped = False

    for k in range(1, max_rows + 1):
        h = h0 / 2 ** (k - 1)
        h_number, h_shown = display.step_size(h0, k)
        rows, stop = {}, None
        for formula in formulas:
            row, stop = _refinement_row(function, formula, x0, h, h_number, h_shown, k, exact, previous[formula.key])
            if stop:
                break
            rows[formula.key] = row
        if stop == "tiny":
            warnings.append(
                f"h es demasiado pequeño para la precisión de la computadora (fila {k}): x₀ ± h ya es "
                "igual a x₀, así que se detuvo el refinamiento."
            )
        elif stop:
            warnings.append(f"{stop}: se detuvo el refinamiento.")
        if stop:
            stopped = True
            break

        for formula in formulas:
            row = rows[formula.key]
            previous[formula.key] = row
            if row["bound"] is None and formula.key not in undefined_second:
                a, b = row["interval_display"]
                undefined_second[formula.key] = (
                    f"f''(x) no está definida en todo el intervalo [{a['approx'] or a['text']}, "
                    f"{b['approx'] or b['text']}]; la fórmula {formula.name.lower()} puede no ser válida allí."
                )
        estimates = [rows[f.key]["estimated_error"] for f in formulas]
        iterations.append(IterationStep(
            iteration=k,
            x=[rows[f.key]["D"] for f in formulas],
            error=None if None in estimates else max(estimates),
            extra={"h": {"value": h, **h_shown}, **rows},
        ))
        if k >= MIN_REFINEMENTS and None not in estimates and all(e <= tolerance for e in estimates):
            converged = True
            break

    warnings.extend(undefined_second.values())
    if exact is None:
        warnings.append(
            "f no es derivable en x₀: no se muestran el error real ni la razón entre errores."
        )
    if not converged:
        tolerance_text = display.fixed(tolerance, 12)
        warnings.append(
            f"No se alcanzó la tolerancia del error estimado ({tolerance_text})."
            if stopped else
            f"No se alcanzó la tolerancia del error estimado ({tolerance_text}) en {len(iterations)} "
            "refinamientos de h. Aumenta el máximo de refinamientos o la tolerancia."
        )
    if iterations:
        last = iterations[-1].extra
        if any(
            last[f.key]["bound"] and last[f.key]["rounding"] > last[f.key]["bound"]
            for f in formulas
        ):
            warnings.append(
                "El error de redondeo ya es comparable con el de truncamiento: reducir más h no "
                "mejora la aproximación."
            )

    meta = {
        "mode": "function",
        "x0": x0,
        "x0_display": display.data_value(x0),
        "h0": h0,
        "tolerance": tolerance,
        "max_iterations": max_rows,
        "exact": exact,
        "differentiable": exact is not None,
        "verification": _function_verification(function, formulas, iterations, x0, exact),
    }
    return function, formulas, converged, iterations, warnings, meta


def _function_verification(function, formulas, iterations, x0, exact):
    final, failed = {}, {}
    for formula in formulas:
        key = formula.key
        failed[key] = [
            step.iteration for step in iterations if step.extra[key]["within_bound"] is False
        ]
        if iterations:
            row = iterations[-1].extra[key]
            final[key] = {k: row[k] for k in ("D", "real_error", "bound", "rounding", "within_bound", "by_rounding")}
    return {
        "substitution": _substitution(function, x0) if exact is not None else None,
        "final": final,
        "failed_rows": failed,
        "all_within": exact is not None and all(not rows for rows in failed.values()),
    }


def _substitution(function, x, n=1):
    """f⁽ⁿ⁾(x) con x sustituido término a término (la comprobación de Newton).

    n = 1: de dónde sale f'(x₀); n = orden de la cota: de dónde sale M.
    """
    check = substitution_check([function.derivatives[n]], [function.symbol], [x])
    equation = check["equations"][0]
    return {
        "x": check["solution"][0],
        "x_display": display.data_value(x),
        "function_latex": equation["function_latex"],
        "function_text": equation["function_text"],
        "terms": equation["terms"],
        "value": equation["residual"],
    }


# --- Modo tabla ----------------------------------------------------------------

def _neighbor_estimate(function, formula, xs, ys, i, exact):
    """Fórmula en xᵢ con su vecino: None si el vecino no existe."""
    (offset_far, _), = [(o, w) for o, w in formula.nodes if o != 0]
    j = i + offset_far
    if not 0 <= j < len(xs):
        return None
    h = abs(xs[j] - xs[i])
    h_number = abs(display.exact(xs[j]) - display.exact(xs[i]))
    values = [ys[i + o] for o, _ in formula.nodes]
    D, step = _approximation(formula, values, h_number, h)
    points = [
        {"offset": o, "weight": w, "role": _point_role(o), "index": i + o, "x": xs[i + o],
         "display": display.data_value(xs[i + o]), "f": ys[i + o], "f_display": shown}
        for (o, w), shown in zip(formula.nodes, step["values"])
    ]
    row = {
        "D": D,
        "h": {"value": h, **display.decimal(h_number)},
        "points": points,
        "decimals": step["decimals"],
        "numerator_display": step["numerator"],
        "real_error": None, "bound": None, "M": None, "x_M": None, "rounding": _rounding(formula, values, h),
        "within_bound": None, "by_rounding": False,
    }
    if function is not None:
        a, b = sorted((xs[i], xs[j]))
        M, x_M = function.max_abs(formula.bound_derivative, a, b)
        bound = None if M is None else float(formula.bound_coefficient) * h ** formula.order * M
        real = None if exact is None else abs(D - exact)
        within, by_rounding = _bound_check(real, bound, row["rounding"])
        row.update({"real_error": real, "bound": bound, "M": M, "x_M": x_M, "interval": [a, b],
                    "M_substitution": None if M is None else _substitution(function, x_M, formula.bound_derivative),
                    "within_bound": within, "by_rounding": by_rounding})
    return row


def _table_mode(data):
    formulas = CHOICES[data["formula"]]
    xs = [float(x) for x, _ in data["points"]]
    ys = [float(y) for _, y in data["points"]]
    text = data.get("compare_function") or ""
    function = _Function(parse_function_of_x(text), _bound_orders(formulas)) if text else None

    warnings = []
    steps = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
    uniform = all(abs(h - steps[0]) <= UNIFORM_RELATIVE * abs(steps[0]) for h in steps)
    if not uniform:
        warnings.append("El espaciado de los datos no es uniforme: cada fórmula usa su propio h.")

    # La secante entre xᵢ y xᵢ₊₁ es a la vez la progresiva en xᵢ y la regresiva
    # en xᵢ₊₁: se calculan las dos siempre, para la comprobación.
    iterations, data_checks, undefined, not_differentiable = [], [], set(), []
    for i, (x, y) in enumerate(zip(xs, ys)):
        exact = function.exact_derivative(x) if function else None
        if function and exact is None:
            not_differentiable.append(i + 1)
        rows = {f.key: _neighbor_estimate(function, f, xs, ys, i, exact) for f in (FORWARD, BACKWARD)}
        for formula in formulas:
            row = rows[formula.key]
            if function and row and row["bound"] is None:
                undefined.add(formula.key)
        extra = {"x": x, "y": y, "x_display": display.data_value(x), "exact": exact, **rows}
        if function:
            fx = function(x)
            ok = fx is not None and abs(y - fx) <= DATA_RELATIVE * max(1.0, abs(fx))
            data_checks.append({"i": i + 1, "y": y, "f": fx,
                                "difference": None if fx is None else abs(y - fx), "ok": ok})
            if not ok:
                warnings.append(
                    f"Punto {i + 1}: el dato no coincide con la función (y = {display.fixed(y)}, "
                    f"f(x) = {'no definida' if fx is None else display.fixed(fx)}); puede ser un error de captura."
                )
        iterations.append(IterationStep(
            iteration=i + 1,
            x=[None if rows[f.key] is None else rows[f.key]["D"] for f in formulas],
            error=None,
            extra=extra,
        ))

    for key in sorted(undefined):
        warnings.append(
            "f''(x) no está definida en todo el intervalo entre algunos puntos; la fórmula "
            f"{next(f.name.lower() for f in formulas if f.key == key)} puede no ser válida allí."
        )
    if not_differentiable:
        warnings.append(
            "f no es derivable en x = "
            + ", ".join(display.fixed(xs[i - 1]) for i in not_differentiable)
            + ": no se muestra el error real allí."
        )

    secant = []
    for i in range(len(xs) - 1):
        forward = iterations[i].extra["forward"]["D"]
        backward = iterations[i + 1].extra["backward"]["D"]
        secant.append({
            "i": i + 1,
            "forward": forward,
            "backward": backward,
            "equal": abs(forward - backward) <= 1e-12 * max(1.0, abs(forward)),
        })

    failed = {
        f.key: [step.iteration for step in iterations
                if step.extra[f.key] and step.extra[f.key]["within_bound"] is False]
        for f in formulas
    }
    meta = {
        "mode": "table",
        "points": [[x, y] for x, y in zip(xs, ys)],
        "uniform": uniform,
        "verification": {
            "secant": secant,
            "data": data_checks if function else None,
            "substitutions": [
                None if step.extra["exact"] is None else _substitution(function, step.extra["x"])
                for step in iterations
            ] if function else None,
            "failed_rows": failed if function else None,
            "all_within": bool(function) and not not_differentiable and all(not r for r in failed.values()),
        },
    }
    return function, formulas, True, iterations, warnings, meta


# --- Punto de entrada ----------------------------------------------------------

def solve_finite_differences(data):
    """Punto de entrada del registro: datos ya validados -> SolverResult."""
    mode = _table_mode if data["mode"] == "table" else _function_mode
    function, formulas, converged, iterations, warnings, meta = mode(data)
    return SolverResult(
        method=METHOD,
        category=CATEGORY,
        converged=converged,
        iterations=iterations,
        solution=list(iterations[-1].x) if iterations and data["mode"] == "function" else [],
        variables=[f.key for f in formulas],
        warnings=warnings,
        meta={
            **meta,
            "formula": data["formula"],
            "formulas": [public_formula(f) for f in formulas],
            "function": function.info() if function else None,
            "sampling_points": SAMPLES,
        },
    )

