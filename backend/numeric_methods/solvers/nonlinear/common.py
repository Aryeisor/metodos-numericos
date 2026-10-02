"""Constantes y utilidades comunes a los métodos para sistemas no lineales
(Punto Fijo, Newton).

No depende de Django: puede usarse y testearse de forma aislada.
"""

import math

import mpmath

from ..validation import InputValidationError

CATEGORY = "nonlinear_system"

MIN_EQUATIONS = 2
# Cota práctica para todos los métodos de la categoría. En Punto Fijo, cada
# despeje automático sin solución cerrada puede tardar segundos en fallar; en
# Newton, cada iteración calcula n + 1 determinantes por cofactores.
MAX_EQUATIONS = 6


class NonlinearValidationError(InputValidationError):
    """Sistema no lineal que no puede resolverse con el método pedido."""


def to_real(value):
    """Convierte un valor evaluado a float, o None si no es real y finito.

    `lambdify` con los módulos math y mpmath puede devolver float, complex o
    mpc (por ejemplo, la raíz de un negativo con mpmath).
    """
    if isinstance(value, (complex, mpmath.mpc)):
        if value.imag != 0:
            return None
        value = value.real
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    # + 0.0 convierte −0.0 en 0.0, que si no se mostraría como "−0".
    return value + 0.0 if math.isfinite(value) else None
