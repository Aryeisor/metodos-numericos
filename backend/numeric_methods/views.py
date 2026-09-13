from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .examples_data import EXAMPLES
from .serializers import LinearSystemSerializer
from .solvers import gauss_seidel, jacobi
from .solvers.dominance import OrderingResult, find_dominant_ordering
from .solvers.validation import MatrixValidationError, check_diagonal_dominance


class BaseSolveView(APIView):
    """Vista base compartida por los endpoints de Jacobi y Gauss-Seidel."""

    solver_module = None
    method_name = ""

    def post(self, request):
        serializer = LinearSystemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        A = data["A"]
        b = data["b"]
        x0 = data.get("x0")
        tolerance = data["tolerance"]
        max_iterations = data["max_iterations"]
        auto_reorder = data["auto_reorder"]

        is_dominant, offending_rows = check_diagonal_dominance(A)

        # Preprocesamiento: si no es dominante, se intenta reordenar las filas.
        # Sólo se reordenan ecuaciones (filas de A junto con b); las columnas no
        # se tocan, así que x0 y el vector solución siguen indexados igual.
        ordering = OrderingResult(False, None, A, b)
        if not is_dominant and auto_reorder:
            ordering = find_dominant_ordering(A, b)
            if ordering.reordered:
                A, b = ordering.A, ordering.b
                is_dominant, offending_rows = check_diagonal_dominance(A)

        warnings = []
        if not is_dominant:
            warnings.append(
                "La matriz no es diagonalmente dominante en la(s) fila(s) "
                f"{offending_rows}. Esta es una condición suficiente (no necesaria) "
                "de convergencia: el método puede converger o no."
            )

        try:
            result = self.solver_module.solve(
                A, b, x0=x0, tolerance=tolerance, max_iterations=max_iterations
            )
        except MatrixValidationError as exc:
            return Response({"detail": exc.errors}, status=status.HTTP_400_BAD_REQUEST)

        if not result["converged"]:
            warnings.append(
                f"El método no alcanzó la tolerancia solicitada ({tolerance}) "
                f"dentro de {result['iterations_used']} iteraciones."
            )

        return Response(
            {
                "method": self.method_name,
                "n": len(A),
                "solution": result["solution"],
                "iterations": result["iterations"],
                "iterations_used": result["iterations_used"],
                "converged": result["converged"],
                "is_diagonally_dominant": is_dominant,
                "warnings": warnings,
                # A y b tal como se usaron realmente en el cálculo (ya
                # reordenadas si hubo reordenamiento), para que el paso a paso
                # del frontend coincida con las iteraciones devueltas.
                "A": A,
                "b": b,
                "reordered": ordering.reordered,
                "row_order": ordering.row_order,
            }
        )


class JacobiSolveView(BaseSolveView):
    solver_module = jacobi
    method_name = "jacobi"


class GaussSeidelSolveView(BaseSolveView):
    solver_module = gauss_seidel
    method_name = "gauss-seidel"


class ExamplesListView(APIView):
    """GET /api/examples/ -> lista de sistemas de ecuaciones precargados."""

    def get(self, request):
        return Response(EXAMPLES)
