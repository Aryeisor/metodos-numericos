"""Determinantes y regla de Cramer, en Python puro con floats.

Es la forma en que se resuelve a mano el sistema lineal de cada iteración de
Newton en el curso: D = det(A) y, para cada incógnita i, D_i = det(A_i),
donde A_i es A con la columna i reemplazada por el vector de términos
independientes; entonces x_i = D_i / D.

El determinante se calcula por expansión de cofactores (la generalización
de la regla de Sarrus que se usa a mano). Su costo crece como n!, lo que no
importa para los sistemas pequeños del curso (2 a 4 incógnitas; la
categoría admite hasta 6), pero sí para matrices grandes: por eso hay un
tamaño máximo.
"""

import math
from typing import NamedTuple

MAX_SIZE = 8
# Tolerancia relativa para considerar singular una matriz. Se compara |D| con
# la cota de Hadamard (producto de las normas de las filas), que es el mayor
# valor que podría tener el determinante con esas filas: así el criterio no
# depende de la escala de los números.
SINGULAR_TOLERANCE = 1e-12


class CramerSolution(NamedTuple):
    determinant: float
    # D_i y la matriz A_i con la que se calculó cada uno.
    column_determinants: list
    column_matrices: list
    solution: list


class SingularMatrixError(ArithmeticError):
    """La matriz es singular: el sistema no tiene solución única."""

    def __init__(self, determinant):
        self.determinant = determinant
        super().__init__(f"La matriz es singular (det = {determinant}).")


def _check_square(matrix):
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        raise ValueError("La matriz debe ser cuadrada y no vacía.")
    if n > MAX_SIZE:
        raise ValueError(f"La expansión por cofactores admite matrices de hasta {MAX_SIZE}x{MAX_SIZE}.")
    return n


def determinant(matrix):
    """Determinante por expansión de cofactores a lo largo de la primera fila."""
    n = _check_square(matrix)
    # + 0.0 convierte −0.0 en 0.0 (un determinante nulo no tiene signo).
    return _cofactor_expansion([list(map(float, row)) for row in matrix], n) + 0.0


def _cofactor_expansion(matrix, n):
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    total = 0.0
    for j, value in enumerate(matrix[0]):
        if value == 0:
            continue  # el término se anula: no hace falta calcular el menor
        minor = [row[:j] + row[j + 1:] for row in matrix[1:]]
        sign = -1.0 if j % 2 else 1.0
        total += sign * value * _cofactor_expansion(minor, n - 1)
    return total


def replace_column(matrix, column, vector):
    """Copia de `matrix` con la columna `column` reemplazada por `vector`."""
    return [
        [vector[i] if j == column else value for j, value in enumerate(row)]
        for i, row in enumerate(matrix)
    ]


def is_singular(matrix, det=None):
    """True si |det| es despreciable frente a la cota de Hadamard de la matriz."""
    det = determinant(matrix) if det is None else det
    bound = math.prod(math.sqrt(sum(v * v for v in row)) for row in matrix)
    return abs(det) <= SINGULAR_TOLERANCE * bound


def cramer(matrix, vector):
    """Resuelve matrix · x = vector por la regla de Cramer.

    Lanza SingularMatrixError si la matriz es (numéricamente) singular.
    """
    n = _check_square(matrix)
    if len(vector) != n:
        raise ValueError("El vector debe tener tantos elementos como filas la matriz.")
    det = determinant(matrix)
    if is_singular(matrix, det):
        raise SingularMatrixError(det)
    column_matrices = [replace_column(matrix, i, vector) for i in range(n)]
    column_determinants = [determinant(m) for m in column_matrices]
    return CramerSolution(
        determinant=det,
        column_determinants=column_determinants,
        column_matrices=column_matrices,
        solution=[d / det for d in column_determinants],
    )
