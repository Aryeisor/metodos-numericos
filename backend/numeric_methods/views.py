from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .examples_data import EXAMPLES, all_examples
from .registry import get_method, public_catalog
from .solvers.validation import InputValidationError


class BaseSolveView(APIView):
    """POST /api/solve/<slug>/ para cualquier método del registro.

    Se instancia una vez por método desde urls.py con
    `BaseSolveView.as_view(method_slug=...)`: el serializer y el solver salen
    del registro, así que un método nuevo no necesita una vista propia.
    """

    method_slug = None

    def post(self, request):
        spec = get_method(self.method_slug)

        serializer = spec.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = spec.solver(serializer.validated_data)
        except InputValidationError as exc:
            return Response({"detail": exc.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result.to_dict())


class MethodsListView(APIView):
    """GET /api/methods/ -> catálogo de métodos para el menú del frontend."""

    def get(self, request):
        return Response(public_catalog())


class ExamplesListView(APIView):
    """GET /api/examples/?method=<slug> -> ejemplos precargados de ese método.

    Sin `method` devuelve todos los ejemplos sin repetir.
    """

    def get(self, request):
        method = request.query_params.get("method")
        if method is None:
            return Response(all_examples())
        if method not in EXAMPLES:
            return Response(
                {"detail": f"No hay ejemplos para el método '{method}'."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(EXAMPLES[method])
