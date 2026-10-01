"""Constantes y errores de validación comunes a todos los métodos iterativos.

Lo específico de cada familia de métodos (por ejemplo, las dimensiones de una
matriz o la dominancia diagonal) vive junto a sus solvers: ver
`solvers/linear/validation.py`.

No depende de Django: puede usarse y testearse de forma aislada.
"""

DEFAULT_TOLERANCE = 1e-6
DEFAULT_MAX_ITERATIONS = 100
MIN_ITERATIONS = 6


class InputValidationError(Exception):
    """Entrada que no cumple las restricciones de un método.

    Las vistas la traducen a una respuesta 400 con `errors` como detalle; cada
    familia de métodos define su propia subclase.
    """

    def __init__(self, errors):
        self.errors = errors if isinstance(errors, list) else [errors]
        super().__init__("; ".join(self.errors))
