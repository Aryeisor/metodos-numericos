"""Integral exacta (con la antiderivada) o de referencia (numérica de alta
precisión) de f en [a, b]. Lo usan todas las reglas de integración.

1. sympy.integrate(f, x) da la antiderivada F, con un límite de TIME_LIMIT
   segundos: la integración simbólica puede tardar mucho (o no terminar).
2. Si F no contiene Integral, todas sus funciones están en la lista blanca
   del parser y F(a), F(b) son reales y finitos: I = F(b) − F(a), «exacta».
3. Si no (función especial como erf, tiempo agotado, F compleja…), I se
   calcula con mpmath.quad a REFERENCE_DIGITS dígitos: «referencia».
4. Si tampoco hay referencia, kind = None.

Límite de tiempo: sympy.integrate corre en un proceso hijo que se mata al
agotarse el tiempo. Un hilo no puede detenerse (seguiría consumiendo CPU en
el worker) y signal.alarm no existe en Windows ni funciona fuera del hilo
principal (runserver atiende cada petición en un hilo). El proceso se crea con
fork en Linux (gunicorn: casi instantáneo) y con spawn en Windows; el plazo
empieza a contar cuando el hijo avisa que está listo, así que el arranque de
spawn (≈ 2 s importando sympy) no se descuenta de los TIME_LIMIT segundos.
Cada antiderivada se guarda en una caché por expresión.

No depende de Django: puede usarse y testearse de forma aislada.
"""

import math
import multiprocessing
import os
import queue as queue_module

import mpmath
import sympy as sp

from ...expressions.parser import ALLOWED_FUNCTIONS
from ...expressions.to_latex import expression_to_latex, substitution_template_latex
from ...expressions.to_text import expression_to_text
from ..nonlinear.common import to_real

TIME_LIMIT = 3.0
# Espera máxima a que el proceso hijo arranque (spawn importa sympy).
STARTUP_LIMIT = 30.0
REFERENCE_DIGITS = 30
TIMED_OUT = "timed_out"
PLACEHOLDER = "@@0@@"

_ALLOWED_CLASSES = frozenset(f for f in ALLOWED_FUNCTIONS.values() if isinstance(f, type))
_CACHE = {}
_CACHE_SIZE = 256


# --- Antiderivada con límite de tiempo ----------------------------------------

def _worker(expr, symbol, channel):
    channel.put(("ready", None))
    try:
        channel.put(("ok", sp.integrate(expr, symbol)))
    except Exception:  # sympy lanza tipos muy variados
        channel.put(("error", None))


def _integrate_with_timeout(expr, symbol, timeout=TIME_LIMIT):
    """F, None (sympy falló) o TIMED_OUT."""
    context = multiprocessing.get_context("spawn" if os.name == "nt" else "fork")
    channel = context.Queue()
    process = context.Process(target=_worker, args=(expr, symbol, channel), daemon=True)
    process.start()
    try:
        channel.get(timeout=STARTUP_LIMIT)
        status, result = channel.get(timeout=timeout)
        return result if status == "ok" else None
    except queue_module.Empty:
        return TIMED_OUT
    finally:
        if process.is_alive():
            process.kill()
        process.join(1)
        channel.close()


def antiderivative(expr, symbol):
    """F o None, y si se agotó el tiempo. Con caché por expresión."""
    key = sp.srepr(expr)
    if key not in _CACHE:
        if len(_CACHE) >= _CACHE_SIZE:
            _CACHE.clear()
        _CACHE[key] = _integrate_with_timeout(expr, symbol)
    result = _CACHE[key]
    return (None, True) if result == TIMED_OUT else (result, False)


# --- Valor exacto y de referencia -----------------------------------------------

def _rational(expr):
    """Los decimales escritos (0.2) como racionales exactos (1/5): así la
    antiderivada sale con fracciones exactas (200/3) y no con 66.6666666667."""
    return expr.xreplace({f: sp.Rational(str(f)) for f in expr.atoms(sp.Float)})


def _terminating(q):
    d = q.q
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


def _evaluate_exact(F, symbol, x):
    try:
        value = complex(sp.N(F.subs(symbol, sp.Rational(repr(float(x)))), REFERENCE_DIGITS))
    except (TypeError, ValueError, ArithmeticError):
        return None
    if abs(value.imag) > 1e-12 * max(1.0, abs(value.real)):
        return None
    return to_real(value.real)


def _special(F):
    """Nota si F usa algo fuera de la lista blanca (None si no)."""
    if F.has(sp.Integral):
        return "sympy no encontró una antiderivada en forma cerrada"
    for atom in F.atoms(sp.Function):
        if isinstance(atom, sp.Piecewise):
            return "La antiderivada que da sympy está definida por tramos"
        if type(atom) not in _ALLOWED_CLASSES:
            return f"La antiderivada usa {expression_to_text(atom)}, una función especial"
    return None


def reference(expr, symbol, a, b):
    """∫ f en [a, b] con mpmath.quad a REFERENCE_DIGITS dígitos; None si falla."""
    try:
        f = sp.lambdify(symbol, expr, modules="mpmath")
        with mpmath.workdps(REFERENCE_DIGITS):
            value = mpmath.quad(f, [mpmath.mpf(repr(float(a))), mpmath.mpf(repr(float(b)))])
            if isinstance(value, mpmath.mpc):
                if abs(value.imag) > 1e-12 * max(1, abs(value.real)):
                    return None
                value = value.real
            return to_real(value)
    except Exception:  # mpmath/lambdify: tipos de error muy variados
        return None


def definite_integral(expr, symbol, a, b):
    """{"kind": "exact" | "reference" | None, "value", "F", "special", "timed_out"}."""
    F, timed_out = antiderivative(_rational(expr), symbol)
    special = None
    if F is not None:
        special = _special(F)
        if special is None:
            Fa, Fb = _evaluate_exact(F, symbol, a), _evaluate_exact(F, symbol, b)
            if Fa is not None and Fb is not None:
                return {"kind": "exact", "value": Fb - Fa + 0.0, "F": F, "special": None, "timed_out": False}
    value = reference(expr, symbol, a, b)
    return {
        "kind": None if value is None else "reference",
        "value": value,
        "F": None,
        "special": special,
        "timed_out": timed_out,
    }


# --- F(x) en pantalla y sustituida término a término ------------------------------

def display_form(F):
    """F con los racionales de decimal finito como decimales (25/2 → 12.5)."""
    return F.xreplace({
        q: sp.Float(float(q), 15) for q in F.atoms(sp.Rational)
        if not q.is_Integer and _terminating(q)
    })


def _ordered_terms(F, symbol):
    """Términos de F; un polinomio, en grado creciente (como se escribe f)."""
    terms = sp.Add.make_args(F)
    if F.is_polynomial(symbol):
        return sorted(terms, key=lambda t: sp.degree(t, symbol))
    return list(F.as_ordered_terms())


def _coefficient(coeff):
    """(LaTeX, texto) del coeficiente positivo: «\\frac{200}{3}», «12.5», «»."""
    if coeff == 1:
        return "", ""
    if isinstance(coeff, sp.Rational) and not coeff.is_Integer and not _terminating(coeff):
        return rf"\frac{{{coeff.p}}}{{{coeff.q}}}", f"({coeff.p}/{coeff.q})"
    text = format(float(coeff), ".12f").rstrip("0").rstrip(".") if not coeff.is_Integer else str(coeff)
    return text, text


def _term(term, symbol):
    coeff, rest = term.as_coeff_Mul()
    negative = coeff < 0
    coeff_latex, coeff_text = _coefficient(display_form(abs(coeff)) if negative else display_form(coeff))
    if rest == 1:
        latex = template = coeff_latex or "1"
        text = plain = coeff_text or "1"
    else:
        rest_template = substitution_template_latex(rest, {symbol: PLACEHOLDER})
        rest_text = expression_to_text(rest.xreplace({symbol: sp.Symbol(PLACEHOLDER)}))
        latex = f"{coeff_latex} {expression_to_latex(rest, order=None)}".strip()
        template = f"{coeff_latex} \\cdot {rest_template}" if coeff_latex else rest_template
        text = f"{coeff_text}*{rest_text}" if coeff_text else rest_text
        plain = f"{coeff_text}*{expression_to_text(rest)}" if coeff_text else expression_to_text(rest)
    return {"sign": "-" if negative else "+", "latex": latex, "template": template, "text": text, "plain": plain}


def _joined(parts, key="latex"):
    return " ".join(
        (("- " if p["sign"] == "-" else "") if i == 0 else f"{p['sign']} ") + p[key]
        for i, p in enumerate(parts)
    )


def antiderivative_info(F, symbol):
    """F(x) en LaTeX y texto, con coeficientes racionales como fracciones."""
    parts = [_term(t, symbol) for t in _ordered_terms(F, symbol)]
    return {"latex": _joined(parts), "text": _joined(parts, "plain")}


def substituter(expr, symbol):
    """(términos de expr, función x → valor de cada término). Las plantillas y
    los evaluadores se arman una vez y sirven para muchos puntos."""
    parts, evaluators = [], []
    for t in _ordered_terms(expr, symbol):
        part = _term(t, symbol)
        parts.append({"sign": part["sign"], "template": part["template"], "text": part["text"]})
        evaluators.append(sp.lambdify([symbol], t, modules=["math", "mpmath"]))

    def values(x):
        out = []
        for evaluator in evaluators:
            try:
                out.append(to_real(evaluator(float(x))))
            except (ArithmeticError, ValueError, TypeError):
                out.append(None)
        return out

    return parts, values


def substitution_from(parts, values, x, x_display):
    terms = [{**part, "value": value} for part, value in zip(parts, values)]
    total = None if None in values else math.fsum(values) + 0.0
    return {
        "x": float(x),
        "x_display": x_display,
        "terms": terms,
        "value": total,
        "all_zero": total is not None and all(v == 0 for v in values),
    }


def substitution(F, symbol, x, x_display):
    """F(x) término a término (mismo formato que la comprobación de Newton)."""
    parts, values = substituter(F, symbol)
    return substitution_from(parts, values(x), x, x_display)


# --- Antiderivada y su verificación, término a término ---------------------------

def _shown(expr, symbol):
    """Un término con los coeficientes como en F (12.5, \\frac{200}{3}), con su signo."""
    part = _term(expr, symbol)
    return f"- {part['latex']}" if part["sign"] == "-" else part["latex"]


def _times(coeff, symbol):
    """«c \\cdot » delante de un paso intermedio («» si c = 1, «-» si c = −1)."""
    if coeff == 1:
        return ""
    if coeff == -1:
        return "-"
    return f"{_shown(coeff, symbol)} \\cdot "


def symbolic_rule(rule):
    """term_step escribe «derivada directa» cuando no desglosa el término."""
    return "derivada calculada simbólicamente" if rule == "derivada directa" else rule


_POWER_RULE = "regla de la potencia: ∫xⁿ dx = xⁿ⁺¹/(n + 1)"


def _integral_term(term, symbol):
    """(∫ término dx, paso intermedio o None, regla); None si no es una forma simple."""
    coeff, rest = term.as_independent(symbol, as_Add=False)
    if rest == 1:
        return term * symbol, None, "integral de una constante: ∫c dx = c·x"
    if rest == symbol:
        rest = sp.Pow(symbol, 1, evaluate=False)
    if isinstance(rest, sp.Pow) and rest.base == symbol and rest.exp.is_number:
        n = rest.exp
        if n == -1:
            return coeff * sp.log(symbol), None, "∫1/x dx = ln|x|; en [a, b] x > 0, así que ln|x| = ln x"
        n_latex = sp.latex(n)
        middle = rf"{_times(coeff, symbol)}\frac{{x^{{{n_latex} + 1}}}}{{{n_latex} + 1}}"
        return coeff * symbol ** (n + 1) / (n + 1), middle, _POWER_RULE
    if rest == sp.exp(symbol):
        return term, None, "la integral de la exponencial es ella misma: ∫eˣ dx = eˣ"
    if rest == sp.sin(symbol):
        return -coeff * sp.cos(symbol), None, "∫sin x dx = −cos x"
    if rest == sp.cos(symbol):
        return coeff * sp.sin(symbol), None, "∫cos x dx = sin x"
    return None


def antiderivative_steps(expr, F, symbol):
    """∫ f dx término a término con la regla de cada uno.

    {"detailed": False} si algún término no es una forma simple o la suma de
    los resultados no es la F de sympy (sustitución, partes…).
    """
    rows, results = [], []
    for t in _ordered_terms(_rational(expr), symbol):
        item = _integral_term(t, symbol)
        if item is None:
            return {"detailed": False, "terms": []}
        result, middle, rule = item
        results.append(result)
        integrand = _shown(t, symbol)
        if integrand.startswith("-"):
            integrand = rf"\left({integrand}\right)"
        chain = [rf"\int {integrand}\,dx", middle, _shown(result, symbol)]
        rows.append({"latex": " = ".join(c for c in chain if c), "rule": rule})
    if sp.simplify(sp.Add(*results) - F) != 0:
        return {"detailed": False, "terms": []}
    return {"detailed": True, "terms": rows}


def derivative_check(expr, F, symbol):
    """F'(x) término a término (mismas reglas que las derivadas de f) y si da f."""
    from ..nonlinear.derivative_steps import term_step

    rows, results = [], []
    for t in _ordered_terms(F, symbol):
        d = sp.diff(t, symbol)
        results.append(_term(d, symbol))
        coeff, rest = t.as_independent(symbol, as_Add=False)
        middle = None
        if isinstance(rest, sp.Pow) and rest.base == symbol and rest.exp.is_number:
            n = rest.exp
            middle = rf"{_times(coeff, symbol)}{sp.latex(n)} \cdot {sp.latex(symbol ** (n - 1))}"
        chain = [rf"\frac{{d}}{{dx}}\left({_shown(t, symbol)}\right)", middle, _shown(d, symbol)]
        rows.append({"latex": " = ".join(c for c in chain if c),
                     "rule": symbolic_rule(term_step(t, symbol, ordinary=True)["rule"])})
    ok = sp.simplify(sp.diff(F, symbol) - _rational(expr)) == 0
    return {"terms": rows, "sum_latex": f"F'(x) = {_joined(results)}", "ok": bool(ok)}
