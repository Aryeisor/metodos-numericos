"""Registro central de métodos numéricos.

Única fuente de verdad sobre qué métodos existen. De aquí salen:
  - las rutas `/api/solve/<slug>/` (ver urls.py),
  - el catálogo `GET /api/methods/` con el que el frontend arma su menú.

Agregar un método nuevo es añadir una entrada a METHODS (y sus ejemplos en
examples_data.py); el resto del sistema no se toca.
"""

from dataclasses import dataclass
from typing import Callable

from .serializers.linear import LinearSystemSerializer
from .solvers.linear.runner import solve_gauss_seidel, solve_jacobi

# Categorías conocidas, en el orden en que se muestran en el menú.
CATEGORIES = {
    "linear_system": "Sistemas lineales",
    "nonlinear_system": "Ecuaciones no lineales",
    "polynomial": "Polinomios",
}


@dataclass(frozen=True)
class MethodSpec:
    """serializer: valida la entrada del método.
    solver: recibe los datos validados y devuelve un `SolverResult`; lanza
        `InputValidationError` si la entrada no cumple las restricciones.
    """

    slug: str
    name: str
    category: str
    serializer: type
    solver: Callable


METHODS = {
    spec.slug: spec
    for spec in (
        MethodSpec(
            slug="jacobi",
            name="Jacobi",
            category="linear_system",
            serializer=LinearSystemSerializer,
            solver=solve_jacobi,
        ),
        MethodSpec(
            slug="gauss-seidel",
            name="Gauss-Seidel",
            category="linear_system",
            serializer=LinearSystemSerializer,
            solver=solve_gauss_seidel,
        ),
    )
}


def get_method(slug):
    return METHODS.get(slug)


def public_catalog():
    """Metadatos que se exponen al frontend (sin serializer ni solver)."""
    return [
        {
            "slug": spec.slug,
            "name": spec.name,
            "category": spec.category,
            "category_label": CATEGORIES[spec.category],
        }
        for spec in METHODS.values()
    ]
