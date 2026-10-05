"""Método de Bairstow para las raíces de un polinomio con coeficientes reales.

Definición (notación del curso)
-------------------------------
Se busca un factor cuadrático **x² − r·x − s** del polinomio
f(x) = aₙxⁿ + … + a₀ (grado n ≥ 3). En cada iteración:

  1. Primera división sintética (b) y segunda (c), ver synthetic.py.
  2. Sistema 2×2 (Newton sobre r y s):
         c₂·Δr + c₃·Δs = −b₁
         c₁·Δr + c₂·Δs = −b₀
     resuelto por la regla de Cramer (linalg/cramer.py, el mismo de Newton):
     D = c₂·c₂ − c₃·c₁, D_r, D_s, Δr = D_r / D, Δs = D_s / D.
  3. r ← r + Δr, s ← s + Δs.
  4. Error relativo porcentual con el valor ya actualizado:
     ε_r = |Δr / r_nuevo|·100, ε_s = |Δs / s_nuevo|·100. Si r_nuevo (o s_nuevo)
     es prácticamente 0, se usa el error absoluto |Δ| y se advierte.

Cada factor se detiene cuando ε_r ≤ εs y ε_s ≤ εs (εs en %), con el mínimo
de MIN_ITERATIONS iteraciones y el máximo de iteraciones **por factor**.

Tras converger se recalculan los b con los r y s finales: el cociente
(bₙ … b₂, grado n − 2) es el polinomio sobre el que se repite el método, y
b₁, b₀ quedan como residuo (≈ 0). Cada factor arranca con los mismos r₀ y s₀
que dio el usuario. Un cociente de grado 2 o 1 se resuelve directamente (sin
iteraciones). Antes de todo, las raíces x = 0 se extraen como factor xᵏ.

Las raíces de x² − r·x − s son (r ± √Δ)/2 con Δ = r² + 4s; si Δ < 0 forman un
par complejo con parte real r/2 e imaginaria √(−Δ)/2. El método no usa
aritmética compleja: las partes real e imaginaria se calculan con floats.
Sólo la comprobación final |f(raíz)| usa `complex`, y es informativa.

No depende de Django: puede usarse y testearse de forma aislada.
"""

import math

from ...linalg.cramer import SingularMatrixError, cramer
from ..base import IterationStep, SolverResult
from ..validation import DEFAULT_MAX_ITERATIONS, MIN_ITERATIONS
from .latex import (
    factorization_latex,
    format_number,
    linear_factor_latex,
    polynomial_latex,
    quadratic_factor_latex,
)
from .synthetic import at_power, b_table, c_table
from .validation import DEFAULT_R0, DEFAULT_S0, DEFAULT_TOLERANCE_PERCENT

CATEGORY = "polynomial"
METHOD = "bairstow"
VARIABLES = ["r", "s"]

# Por debajo de este valor, r o s se consideran 0 y su error relativo no
# está definido (se usa el absoluto).
ZERO_THRESHOLD = 1e-12
# Discriminante despreciable frente a la escala de r² y 4s: raíz doble.
DISCRIMINANT_TOLERANCE = 1e-12

METHOD_BAIRSTOW = "bairstow"
METHOD_QUADRATIC = "cuadratica_directa"
METHOD_LINEAR = "lineal_directa"


def _finite(value):
    return value is not None and math.isfinite(value)


def _clean(value):
    """Valores para JSON estricto: lo no finito se reporta como None."""
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clean(v) for v in value]
    if isinstance(value, float):
        return value + 0.0 if math.isfinite(value) else None  # + 0.0: sin −0.0
    return value


def _polynomial_info(coefficients):
    return {
        "degree": len(coefficients) - 1,
        "coefficients": list(coefficients),
        "latex": polynomial_latex(coefficients),
    }


def quadratic_roots(r, s):
    """Raíces de x² − r·x − s. Devuelve (Δ, raíces [{re, im}], raíz_doble)."""
    discriminant = r * r + 4 * s
    double = abs(discriminant) < DISCRIMINANT_TOLERANCE * max(1.0, r * r, abs(4 * s))
    if double:
        discriminant = 0.0
    if discriminant >= 0:
        root = math.sqrt(discriminant)
        roots = [{"re": (r + root) / 2, "im": 0.0}, {"re": (r - root) / 2, "im": 0.0}]
    else:
        imaginary = math.sqrt(-discriminant) / 2
        roots = [{"re": r / 2, "im": imaginary}, {"re": r / 2, "im": -imaginary}]
    return discriminant, roots, double


def _relative_error(delta, new_value):
    """(error, absoluto?) — relativo en % o, si new_value ≈ 0, |delta|."""
    if abs(new_value) < ZERO_THRESHOLD:
        return abs(delta), True
    return abs(delta / new_value) * 100, False


def iterate_factor(coefficients, r0, s0, tolerance, max_iterations):
    """Busca un factor x² − r·x − s de `coefficients` (grado ≥ 3).

    Devuelve {iterations, converged, r, s, failure, note, absolute}, donde cada
    iteración es un dict con todo el paso a paso (`extra`), y `failure` es
    None o {"iteration", "reason": "singular" | "non_finite" | "max_iterations"}.
    """
    max_iterations = max(max_iterations, MIN_ITERATIONS)
    r, s = float(r0), float(s0)
    iterations = []
    met_tolerance = False
    absolute_used = []

    for k in range(1, max_iterations + 1):
        b = b_table(coefficients, r, s)
        c = c_table(b["result"], r, s)
        b0, b1 = at_power(b["result"], 0), at_power(b["result"], 1)
        c1, c2, c3 = (at_power(c["result"], p) for p in (1, 2, 3))
        extra = {
            "r": r, "s": s, "b_table": b, "c_table": c,
            "b0": b0, "b1": b1, "c1": c1, "c2": c2, "c3": c3,
        }

        if not all(_finite(v) for v in (b0, b1, c1, c2, c3)):
            iterations.append({"iteration": k, "x": [None, None], "error": None, "extra": extra})
            return {"iterations": iterations, "converged": False, "r": r, "s": s,
                    "failure": {"iteration": k, "reason": "non_finite"}, "note": None,
                    "absolute": absolute_used}

        matrix = [[c2, c3], [c1, c2]]
        rhs = [-b1, -b0]
        extra.update({"matrix": matrix, "rhs": rhs})
        try:
            step = cramer(matrix, rhs)
        except SingularMatrixError as exc:
            extra["D"] = exc.determinant
            iterations.append({"iteration": k, "x": [None, None], "error": None, "extra": extra})
            if met_tolerance:
                # Ya cumplía la tolerancia (seguía sólo por el mínimo de
                # iteraciones): se cierra con los r y s de la iteración anterior.
                return {"iterations": iterations, "converged": True, "r": r, "s": s, "failure": None,
                        "note": (f"En la iteración {k} el determinante D resultó prácticamente cero, "
                                 "pero el factor ya cumplía la tolerancia: se cierra con los r y s "
                                 "de la iteración anterior."),
                        "absolute": absolute_used}
            return {"iterations": iterations, "converged": False, "r": r, "s": s,
                    "failure": {"iteration": k, "reason": "singular"}, "note": None,
                    "absolute": absolute_used}

        delta_r, delta_s = step.solution
        r_new, s_new = r + delta_r, s + delta_s
        extra.update({
            "D": step.determinant,
            "D_r": step.column_determinants[0],
            "D_s": step.column_determinants[1],
            "matrices": step.column_matrices,
            "delta_r": delta_r, "delta_s": delta_s,
            "r_new": r_new, "s_new": s_new,
        })
        if not all(_finite(v) for v in (delta_r, delta_s, r_new, s_new)):
            iterations.append({"iteration": k, "x": [None, None], "error": None, "extra": extra})
            return {"iterations": iterations, "converged": False, "r": r, "s": s,
                    "failure": {"iteration": k, "reason": "non_finite"}, "note": None,
                    "absolute": absolute_used}

        eps_r, absolute_r = _relative_error(delta_r, r_new)
        eps_s, absolute_s = _relative_error(delta_s, s_new)
        error = max(eps_r, eps_s)
        extra.update({
            "eps_r": eps_r, "eps_s": eps_s,
            "absolute": {"r": absolute_r, "s": absolute_s},
            "meets_tolerance": eps_r <= tolerance and eps_s <= tolerance,
        })
        if absolute_r or absolute_s:
            absolute_used.append({"iteration": k, "r": absolute_r, "s": absolute_s})
        iterations.append({"iteration": k, "x": [r_new, s_new], "error": error, "extra": extra})

        r, s = r_new, s_new
        met_tolerance = extra["meets_tolerance"]
        if met_tolerance and k >= MIN_ITERATIONS:
            return {"iterations": iterations, "converged": True, "r": r, "s": s,
                    "failure": None, "note": None, "absolute": absolute_used}

    return {"iterations": iterations, "converged": False, "r": r, "s": s,
            "failure": {"iteration": max_iterations, "reason": "max_iterations"}, "note": None,
            "absolute": absolute_used}


def _quadratic_closure(index, coefficients):
    """Cociente de grado 2, a·x² + b·x + c, expresado como a·(x² − r·x − s)."""
    a, b, c = coefficients
    r, s = -b / a, -c / a
    discriminant, roots, double = quadratic_roots(r, s)
    return {
        "index": index,
        "method": METHOD_QUADRATIC,
        "dividend": _polynomial_info(coefficients),
        "converged": True,
        "r": r, "s": s,
        "factor_latex": quadratic_factor_latex(r, s),
        "discriminant": discriminant,
        "double_root": double,
        "roots": roots,
    }


def _linear_closure(index, coefficients):
    """Cociente de grado 1, a₁·x + a₀: x = −a₀ / a₁."""
    a1, a0 = coefficients
    root = -a0 / a1
    return {
        "index": index,
        "method": METHOD_LINEAR,
        "dividend": _polynomial_info(coefficients),
        "converged": True,
        "factor_latex": linear_factor_latex(root),
        "roots": [{"re": root, "im": 0.0}],
    }


def _check(coefficients, root):
    """|f(raíz)| con el polinomio original (Horner con `complex`, informativo)."""
    z = complex(root["re"], root["im"])
    value = 0j
    for a in coefficients:
        value = value * z + a
    return abs(value)


def _failure_warning(factor_number, failure, tolerance, max_iterations):
    k = failure["iteration"]
    if failure["reason"] == "singular":
        return (
            f"Factor {factor_number}, iteración {k}: el determinante D del sistema 2×2 es "
            "(prácticamente) cero, no se puede continuar. Prueba con otros r₀ y s₀. Se muestran "
            "las raíces encontradas hasta ese momento."
        )
    if failure["reason"] == "non_finite":
        return (
            f"Factor {factor_number}, iteración {k}: aparecieron valores no finitos (los valores "
            "crecieron sin control). Prueba con otros r₀ y s₀. Se muestran las raíces encontradas "
            "hasta ese momento."
        )
    return (
        f"El factor {factor_number} no alcanzó la tolerancia εs = {tolerance} % en "
        f"{max(max_iterations, MIN_ITERATIONS)} iteraciones. Se muestran las raíces encontradas "
        "hasta ese momento."
    )


def solve_bairstow(data):
    """Punto de entrada del registro: datos ya validados -> SolverResult."""
    coefficients = [float(a) for a in data["coefficients"]]
    r0 = data.get("r0", DEFAULT_R0)
    s0 = data.get("s0", DEFAULT_S0)
    tolerance = data.get("tolerance", DEFAULT_TOLERANCE_PERCENT)
    max_iterations = data.get("max_iterations", DEFAULT_MAX_ITERATIONS)

    warnings, notes = [], []
    iterations, factors, roots = [], [], []
    failure = None

    # Paso previo: raíces x = 0 (a₀ = 0, quizá también a₁, …).
    zero_roots = 0
    while zero_roots < len(coefficients) - 1 and coefficients[len(coefficients) - 1 - zero_roots] == 0:
        zero_roots += 1
    current = coefficients[: len(coefficients) - zero_roots]
    roots += [{"re": 0.0, "im": 0.0, "source": "paso_previo"} for _ in range(zero_roots)]
    if zero_roots:
        notes.append(
            f"Paso previo: se extrajo el factor x^{zero_roots} ({zero_roots} raíz/raíces x = 0) "
            "y se continúa con el polinomio reducido."
        )
        if len(current) - 1 < 3:
            notes.append(
                f"El polinomio reducido es de grado {len(current) - 1}: se resuelve directamente, "
                "sin iteraciones de Bairstow."
            )

    last_rs = []
    while len(current) - 1 >= 3:
        index = len(factors)
        outcome = iterate_factor(current, r0, s0, tolerance, max_iterations)
        start = len(iterations)
        for row in outcome["iterations"]:
            iterations.append(IterationStep(
                iteration=row["iteration"], x=row["x"], error=row["error"],
                extra={"factor": index, **row["extra"]},
            ))
        factor = {
            "index": index,
            "method": METHOD_BAIRSTOW,
            "dividend": _polynomial_info(current),
            "r0": float(r0), "s0": float(s0),
            "iteration_indices": list(range(start, len(iterations))),
            "iterations_used": len(outcome["iterations"]),
            "converged": outcome["converged"],
            "r": outcome["r"], "s": outcome["s"],
        }
        for item in outcome["absolute"]:
            both = item["r"] and item["s"]
            which = "r y s quedaron" if both else f"{'r' if item['r'] else 's'} quedó"
            warnings.append(
                f"Factor {index + 1}, iteración {item['iteration']}: {which} prácticamente en 0, "
                f"así que {'sus errores relativos no están definidos' if both else 'su error relativo no está definido'}; "
                "se usó el error absoluto |Δ|."
            )
        if outcome["note"]:
            factor["note"] = outcome["note"]
            notes.append(f"Factor {index + 1}: {outcome['note']}")

        if not outcome["converged"]:
            failure = {"factor": index, **outcome["failure"]}
            warnings.append(_failure_warning(index + 1, outcome["failure"], tolerance, max_iterations))
            factors.append(factor)
            break

        r, s = outcome["r"], outcome["s"]
        last_rs = [r, s]
        final_b = b_table(current, r, s)
        quotient = final_b["result"][:-2]
        discriminant, factor_roots, double = quadratic_roots(r, s)
        if double:
            notes.append(f"Factor {index + 1}: el discriminante es prácticamente 0; se toma como raíz doble.")
        factor.update({
            "factor_latex": quadratic_factor_latex(r, s),
            "discriminant": discriminant,
            "double_root": double,
            "roots": factor_roots,
            "final_b": final_b,
            "quotient": _polynomial_info(quotient),
            "residue": {"b1": at_power(final_b["result"], 1), "b0": at_power(final_b["result"], 0)},
        })
        factors.append(factor)
        roots += [{**root, "factor": index} for root in factor_roots]
        current = quotient

    if failure is None and len(current) - 1 == 2:
        factor = _quadratic_closure(len(factors), current)
        if factor["double_root"]:
            notes.append(f"Factor {len(factors) + 1}: el discriminante es prácticamente 0; se toma como raíz doble.")
        factors.append(factor)
        roots += [{**root, "factor": factor["index"]} for root in factor["roots"]]
    elif failure is None and len(current) - 1 == 1:
        factor = _linear_closure(len(factors), current)
        factors.append(factor)
        roots += [{**root, "factor": factor["index"]} for root in factor["roots"]]

    if factors and any(f["method"] == METHOD_BAIRSTOW for f in factors):
        notes.append(
            f"Cada factor obtenido por Bairstow arranca con los mismos valores iniciales "
            f"r₀ = {format_number(r0)} y s₀ = {format_number(s0)} dados por el usuario."
        )

    for root in roots:
        root["check"] = _check(coefficients, root)

    converged = failure is None
    factor_latex = [f["factor_latex"] for f in factors if "factor_latex" in f]
    return SolverResult(
        method=METHOD,
        category=CATEGORY,
        converged=converged,
        iterations=[_clean_step(step) for step in iterations],
        # r y s del último factor obtenido por Bairstow; las raíces van en `roots`.
        solution=_clean(last_rs),
        variables=list(VARIABLES),
        warnings=warnings,
        meta=_clean({
            "polynomial": {
                **_polynomial_info(coefficients),
                "text": data.get("polynomial") or None,
                "input_mode": "text" if data.get("polynomial") else "coefficients",
            },
            "r0": float(r0),
            "s0": float(s0),
            "tolerance_percent": tolerance,
            "zero_roots": zero_roots,
            "factors": factors,
            "roots": roots,
            "factorization": factorization_latex(coefficients[0], zero_roots, factor_latex)
            if converged else None,
            "notes": notes,
            "failure": failure,
        }),
    )


def _clean_step(step):
    step.x = _clean(step.x)
    step.error = _clean(step.error)
    step.extra = _clean(step.extra)
    return step
