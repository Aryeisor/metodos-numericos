from django.urls import path, re_path

from .registry import METHODS
from .views import BaseSolveView, ExamplesListView, ExpressionPreviewView, MethodsListView

# Una ruta de resolución por método registrado: /api/solve/<slug>/
solve_patterns = [
    path(f"solve/{slug}/", BaseSolveView.as_view(method_slug=slug), name=f"solve-{slug}")
    for slug in METHODS
]

urlpatterns = [
    *solve_patterns,
    path("methods/", MethodsListView.as_view(), name="methods-list"),
    path("examples/", ExamplesListView.as_view(), name="examples-list"),
    # Con o sin barra final: un POST no puede redirigirse a la versión con barra.
    re_path(r"^expressions/preview/?$", ExpressionPreviewView.as_view(), name="expression-preview"),
]
