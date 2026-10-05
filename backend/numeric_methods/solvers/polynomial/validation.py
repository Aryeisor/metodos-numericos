"""Lectura y validación de un polinomio para Bairstow.

El polinomio llega como texto (se lee con el parser seguro, con la única
variable `x`) o como lista de coeficientes en orden descendente. En ambos
casos se valida lo mismo: grado entre MIN_DEGREE y MAX_DEGREE, coeficiente
principal distinto de cero y coeficientes reales, finitos y dentro de la
misma magnitud máxima que acepta el parser.

No depende de Django: puede usarse y testearse de forma aislada.
"""

import math

import sympy as sp

from ...expressions.normalize import estimate_degree, evaluate_tree
from ...expressions.parser import MAX_MAGNITUDE, ExpressionError, make_symbols, parse_equation
from ..validation import InputValidationError

MIN_DEGREE = 3
MAX_DEGREE = 10
# Tolerancia por defecto de Bairstow, en porcentaje (error relativo).
DEFAULT_TOLERANCE_PERCENT = 0.0001
DEFAULT_R0 = -1.0
DEFAULT_S0 = -1.0
# Cota del grado (estimada sin expandir) a partir de la cual no se intenta
# expandir el texto: ((x^1000)^1000) tendría grado 10⁶ y expandirlo colgaría
# el proceso. Por debajo se expande y se comprueba el grado real.
MAX_EXPAND_DEGREE = 200

VARIABLE = "x"


class PolynomialValidationError(InputValidationError):
    """Polinomio que no puede resolverse con Bairstow."""


def degree_errors(degree):
    """Mensajes si el grado está fuera de [MIN_DEGREE, MAX_DEGREE]."""
    if degree < 1:
        return ["El polinomio es constante: no tiene raíces que buscar. Bairstow es para grado ≥ 3."]
    if degree == 1:
        return ["El polinomio es de grado 1: se resuelve directamente despejando x. Bairstow es para grado ≥ 3."]
    if degree == 2:
        return [
            "El polinomio es de grado 2: se resuelve directamente con la fórmula cuadrática. "
            "Bairstow es para grado ≥ 3."
        ]
    if degree > MAX_DEGREE:
        return [f"El polinomio es de grado {degree}; esta aplicación admite hasta grado {MAX_DEGREE}."]
    return []


def coefficient_errors(coefficients):
    """Mensajes si algún coeficiente no es real y finito o es desmesurado."""
    errors = []
    for p, value in enumerate(coefficients):
        power = len(coefficients) - 1 - p
        if not math.isfinite(value):
            errors.append(f"El coeficiente de x^{power} no es un número real finito.")
        elif abs(value) > MAX_MAGNITUDE:
            errors.append(
                f"El coeficiente de x^{power} es demasiado grande "
                f"(el máximo permitido es {MAX_MAGNITUDE:.0e})."
            )
    return errors


def validate_coefficients(coefficients):
    """Valida una lista de coeficientes en orden descendente (aₙ … a₀).

    Lanza PolynomialValidationError. Rechaza ceros a la izquierda en lugar de
    quitarlos en silencio: el grado lo fija la cantidad de coeficientes.
    """
    errors = coefficient_errors(coefficients)
    if errors:
        raise PolynomialValidationError(errors)
    if not coefficients:
        raise PolynomialValidationError("Faltan los coeficientes del polinomio.")
    if coefficients[0] == 0:
        raise PolynomialValidationError(
            "El coeficiente principal (el de la potencia más alta) no puede ser 0. Quita los "
            "ceros a la izquierda o baja el grado del polinomio."
        )
    errors = degree_errors(len(coefficients) - 1)
    if errors:
        raise PolynomialValidationError(errors)
    return [float(value) for value in coefficients]


def coefficients_from_text(text):
    """Convierte el texto de un polinomio en x en sus coeficientes
    (descendentes, con ceros explícitos para las potencias que faltan).

    Admite "expresión = 0", "lado = lado" (todo pasa a la izquierda) o una
    expresión sin "=". Lanza PolynomialValidationError con un mensaje claro.
    """
    try:
        _, lhs, rhs = parse_equation(text, [VARIABLE])
    except ExpressionError as exc:
        message = str(exc)
        if "no es una variable declarada" in message:
            message = f"El polinomio sólo puede depender de x: {message}"
        raise PolynomialValidationError(message) from exc

    x = make_symbols([VARIABLE])[VARIABLE]
    expr = lhs if rhs is None else sp.Add(lhs, sp.Mul(-1, rhs, evaluate=False), evaluate=False)
    expr = evaluate_tree(expr)

    if estimate_degree(expr, x) > MAX_EXPAND_DEGREE:
        raise PolynomialValidationError(
            f"El polinomio tiene un grado demasiado alto; esta aplicación admite hasta grado {MAX_DEGREE}."
        )
    if not expr.is_polynomial(x):
        raise PolynomialValidationError(
            "La expresión no es un polinomio en x: sólo se admiten sumas de términos c·xᵏ con k "
            "entero no negativo (no funciones como sin(x), sqrt(x) o exp(x), ni divisiones entre x, "
            "ni exponentes negativos o no enteros)."
        )

    expanded = sp.expand(expr)
    if not expanded.has(x):
        raise PolynomialValidationError(degree_errors(0))
    coefficients = []
    for value in sp.Poly(expanded, x).all_coeffs():
        number = complex(sp.N(value))
        if number.imag != 0:
            raise PolynomialValidationError("Los coeficientes del polinomio deben ser reales.")
        coefficients.append(number.real)

    errors = coefficient_errors(coefficients) + degree_errors(len(coefficients) - 1)
    if errors:
        raise PolynomialValidationError(errors)
    return coefficients
