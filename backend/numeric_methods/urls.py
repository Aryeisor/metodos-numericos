from django.urls import path

from .views import ExamplesListView, GaussSeidelSolveView, JacobiSolveView

urlpatterns = [
    path("solve/jacobi/", JacobiSolveView.as_view(), name="solve-jacobi"),
    path("solve/gauss-seidel/", GaussSeidelSolveView.as_view(), name="solve-gauss-seidel"),
    path("examples/", ExamplesListView.as_view(), name="examples-list"),
]
