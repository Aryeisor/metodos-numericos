from django.urls import path

from .registry import METHODS
from .views import BaseSolveView, ExamplesListView, MethodsListView

# Una ruta de resolución por método registrado: /api/solve/<slug>/
solve_patterns = [
    path(f"solve/{slug}/", BaseSolveView.as_view(method_slug=slug), name=f"solve-{slug}")
    for slug in METHODS
]

urlpatterns = [
    *solve_patterns,
    path("methods/", MethodsListView.as_view(), name="methods-list"),
    path("examples/", ExamplesListView.as_view(), name="examples-list"),
]
