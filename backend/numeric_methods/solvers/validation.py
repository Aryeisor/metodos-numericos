"""Validaciones puras para sistemas de ecuaciones lineales.

No depende de Django: puede usarse y testearse de forma aislada.
"""

MIN_VARIABLES = 3
DEFAULT_MAX_ITERATIONS = 100
MIN_ITERATIONS = 6


class MatrixValidationError(Exception):
    """Se lanza cuando el sistema (A, b, x0) no cumple las restricciones mínimas."""

    def __init__(self, errors):
        self.errors = errors if isinstance(errors, list) else [errors]
        super().__init__("; ".join(self.errors))


def validate_dimensions(A, b, x0=None, min_variables=MIN_VARIABLES):
    """Valida que A sea cuadrada, de tamaño >= min_variables, y que b (y x0) calcen.

    Devuelve n (tamaño del sistema) si todo es correcto, o lanza MatrixValidationError.
    """
    errors = []

    if not A or not isinstance(A, (list, tuple)):
        raise MatrixValidationError("La matriz A es requerida y no puede estar vacía.")

    n = len(A)

    if n < min_variables:
        errors.append(
            f"El sistema debe tener al menos {min_variables} variables (n >= {min_variables})."
        )

    for row in A:
        if len(row) != n:
            errors.append("La matriz A debe ser cuadrada (n x n).")
            break

    if b is None or len(b) != n:
        errors.append(f"El vector b debe tener exactamente {n} elementos.")

    if x0 is not None and len(x0) != n:
        errors.append(f"El vector inicial x0 debe tener exactamente {n} elementos.")

    if errors:
        raise MatrixValidationError(errors)

    return n


def validate_diagonal_nonzero(A):
    """Valida que ningún elemento de la diagonal principal sea cero."""
    errors = []
    n = len(A)
    for i in range(n):
        if A[i][i] == 0:
            errors.append(
                f"El elemento de la diagonal a[{i + 1}][{i + 1}] es cero; "
                f"no es posible despejar la variable x{i + 1}."
            )
    if errors:
        raise MatrixValidationError(errors)


def check_diagonal_dominance(A):
    """Verifica si A es (estrictamente) diagonalmente dominante por filas.

    Devuelve (is_dominant: bool, offending_rows: list[int]) con las filas
    (1-indexadas) que no cumplen |a_ii| > sum_{j!=i} |a_ij|.
    """
    n = len(A)
    offending_rows = []
    for i in range(n):
        diag = abs(A[i][i])
        off_sum = sum(abs(A[i][j]) for j in range(n) if j != i)
        if diag <= off_sum:
            offending_rows.append(i + 1)
    return (len(offending_rows) == 0, offending_rows)
