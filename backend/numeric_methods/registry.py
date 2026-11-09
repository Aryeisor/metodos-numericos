"""Registro central de métodos numéricos.

Única fuente de verdad sobre qué métodos existen. De aquí salen:
  - las rutas `/api/solve/<slug>/` (ver urls.py),
  - el catálogo `GET /api/methods/` con el que el frontend arma su menú.

Agregar un método nuevo es añadir una entrada a METHODS (y sus ejemplos en
examples_data.py); el resto del sistema no se toca.
"""

from dataclasses import dataclass
from typing import Callable

from .serializers.differentiation import DifferentiationSerializer, FivePointSerializer, ThreePointSerializer
from .serializers.integration import GaussSerializer, IntegrationSerializer, RombergSerializer, SimpsonSerializer
from .serializers.linear import LinearSystemSerializer
from .serializers.nonlinear import NewtonSystemSerializer, NonlinearSystemSerializer
from .serializers.polynomial import PolynomialSerializer
from .solvers.differentiation.finite_differences import solve_finite_differences
from .solvers.differentiation.five_point import solve_five_point
from .solvers.differentiation.three_point import solve_three_point
from .solvers.integration.gauss import solve_gauss
from .solvers.integration.romberg import solve_romberg
from .solvers.integration.simpson import solve_simpson
from .solvers.integration.trapezoid import solve_trapezoid
from .solvers.linear.runner import solve_gauss_seidel, solve_jacobi
from .solvers.nonlinear.fixed_point import solve_fixed_point
from .solvers.nonlinear.newton import solve_newton
from .solvers.polynomial.bairstow import solve_bairstow

@dataclass(frozen=True)
class CategorySpec:
    """Metadatos de una categoría para el menú.

    latex: expresión característica que encabeza la columna; si se deja vacía,
        el menú muestra sólo el nombre. order: posición en el menú.
    """

    label: str
    description: str
    order: int
    latex: str = ""


# Categorías conocidas; el menú las ordena por `order`.
CATEGORIES = {
    "linear_system": CategorySpec(
        label="Sistemas lineales",
        description="Sistemas de ecuaciones lineales con métodos iterativos",
        latex=r"A\mathbf{x}=\mathbf{b}",
        order=1,
    ),
    "nonlinear_system": CategorySpec(
        label="Ecuaciones no lineales",
        description="Sistemas de ecuaciones no lineales",
        latex=r"F(\mathbf{x})=\mathbf{0}",
        order=2,
    ),
    "polynomial": CategorySpec(
        label="Polinomios",
        description="Raíces reales y complejas de polinomios",
        latex="P(x)=0",
        order=3,
    ),
    "differentiation": CategorySpec(
        label="Diferenciación numérica",
        description="Derivadas aproximadas a partir de valores de la función",
        latex="f'(x_0)",
        order=4,
    ),
    "integration": CategorySpec(
        label="Integración numérica",
        description="Integrales definidas aproximadas",
        latex=r"\int_a^b f(x)\,dx",
        order=5,
    ),
}


@dataclass(frozen=True)
class MethodSpec:
    """serializer: valida la entrada del método.
    solver: recibe los datos validados y devuelve un `SolverResult`; lanza
        `InputValidationError` si la entrada no cumple las restricciones.
    summary: una línea, en lenguaje sencillo, de lo que hace (menú).
    keywords: sinónimos para el buscador del menú («derivada», «área»…).
    """

    slug: str
    name: str
    category: str
    serializer: type
    solver: Callable
    summary: str = ""
    keywords: tuple = ()


METHODS = {
    spec.slug: spec
    for spec in (
        MethodSpec(
            slug="jacobi",
            name="Jacobi",
            category="linear_system",
            serializer=LinearSystemSerializer,
            solver=solve_jacobi,
            summary="Actualiza todas las variables a la vez con los valores anteriores",
            keywords=('sistema', 'ecuaciones lineales', 'matriz', 'iterativo'),
        ),
        MethodSpec(
            slug="gauss-seidel",
            name="Gauss-Seidel",
            category="linear_system",
            serializer=LinearSystemSerializer,
            solver=solve_gauss_seidel,
            summary="Usa cada valor nuevo apenas se calcula",
            keywords=('sistema', 'ecuaciones lineales', 'matriz', 'iterativo'),
        ),
        MethodSpec(
            slug="punto-fijo",
            name="Punto Fijo (Iterativo Secuencial)",
            category="nonlinear_system",
            serializer=NonlinearSystemSerializer,
            solver=solve_fixed_point,
            summary="Despeja cada ecuación y sustituye en secuencia",
            keywords=('sistema', 'no lineal', 'despeje', 'iterativo'),
        ),
        MethodSpec(
            slug="newton",
            name="Newton",
            category="nonlinear_system",
            serializer=NewtonSystemSerializer,
            solver=solve_newton,
            summary="Usa la matriz Jacobiana y la regla de Cramer",
            keywords=('sistema', 'no lineal', 'jacobiano', 'raphson'),
        ),
        MethodSpec(
            slug="bairstow",
            name="Bairstow",
            category="polynomial",
            serializer=PolynomialSerializer,
            solver=solve_bairstow,
            summary="Extrae factores cuadráticos x² − r·x − s",
            keywords=('raices', 'raíz', 'ecuación polinómica', 'factor cuadrático'),
        ),
        MethodSpec(
            slug="diferencias-finitas",
            name="Diferencias progresiva y regresiva",
            category="differentiation",
            serializer=DifferentiationSerializer,
            solver=solve_finite_differences,
            summary="Pendiente de una recta secante, error O(h)",
            keywords=('derivada', 'diferencia progresiva', 'diferencia regresiva', 'secante'),
        ),
        MethodSpec(
            slug="tres-puntos",
            name="Fórmula de 3 puntos",
            category="differentiation",
            serializer=ThreePointSerializer,
            solver=solve_three_point,
            summary="Pendiente de una parábola, error O(h²)",
            keywords=('derivada', 'diferencia centrada', 'tres puntos'),
        ),
        MethodSpec(
            slug="cinco-puntos",
            name="Fórmula de 5 puntos",
            category="differentiation",
            serializer=FivePointSerializer,
            solver=solve_five_point,
            summary="Polinomio de grado 4, error O(h⁴)",
            keywords=('derivada', 'diferencia centrada', 'cinco puntos'),
        ),
        MethodSpec(
            slug="trapecio",
            name="Método del trapecio",
            category="integration",
            serializer=IntegrationSerializer,
            solver=solve_trapezoid,
            summary="Une los puntos con rectas",
            keywords=('integral', 'área', 'trapecio compuesto'),
        ),
        MethodSpec(
            slug="simpson",
            name="Método de Simpson",
            category="integration",
            serializer=SimpsonSerializer,
            solver=solve_simpson,
            summary="Une los puntos con parábolas (1/3) o cúbicas (3/8)",
            keywords=('integral', 'área', '1/3', '3/8'),
        ),
        MethodSpec(
            slug="romberg",
            name="Integración de Romberg",
            category="integration",
            serializer=RombergSerializer,
            solver=solve_romberg,
            summary="Mejora el trapecio en escalera con Richardson",
            keywords=('integral', 'área', 'extrapolación', 'richardson'),
        ),
        MethodSpec(
            slug="gauss",
            name="Cuadratura gaussiana",
            category="integration",
            serializer=GaussSerializer,
            solver=solve_gauss,
            summary="Evalúa en los puntos óptimos (nodos de Legendre)",
            keywords=('integral', 'área', 'legendre', 'gauss-legendre'),
        ),
    )
}


def get_method(slug):
    return METHODS.get(slug)


def public_catalog():
    """Metadatos que se exponen al frontend (sin serializer ni solver).

    Cada método lleva los datos de su categoría, así la respuesta sigue siendo
    una lista plana; va ordenada por categoría (`order`) y, dentro de cada una,
    en el orden de METHODS.
    """
    specs = sorted(METHODS.values(), key=lambda spec: CATEGORIES[spec.category].order)
    return [
        {
            "slug": spec.slug,
            "name": spec.name,
            "category": spec.category,
            "category_label": CATEGORIES[spec.category].label,
            "summary": spec.summary,
            "keywords": list(spec.keywords),
            "category_description": CATEGORIES[spec.category].description,
            "category_latex": CATEGORIES[spec.category].latex,
            "category_order": CATEGORIES[spec.category].order,
        }
        for spec in specs
    ]
