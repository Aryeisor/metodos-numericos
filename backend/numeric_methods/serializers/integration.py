from rest_framework import serializers

from ..solvers.differentiation.finite_differences import parse_function_of_x
from ..solvers.integration.trapezoid import (
    DEFAULT_MAX_REFINEMENTS,
    DEFAULT_N0,
    DEFAULT_TOLERANCE,
    MAX_N0,
    MAX_POINTS,
    MAX_REFINEMENTS,
    MIN_N0,
    MIN_POINTS,
    MIN_REFINEMENTS,
)
from ..solvers.validation import InputValidationError
from .differentiation import _finite, validate_points


def _function_errors(text, label):
    try:
        parse_function_of_x(text)
    except InputValidationError as exc:
        return [f"{label}: {message}" for message in exc.errors]
    return []


class IntegrationSerializer(serializers.Serializer):
    """Entrada de las reglas de integración, en uno de dos modos:

    - "function": `function` (f(x) como texto), `a`, `b` (a < b), `n0`
      (segmentos iniciales, 1 a 1000), `tolerance` y `max_iterations`
      (máximo de refinamientos, de 6 a 22).
    - "table": `points` = [[x₀, y₀], ..., [xₙ, yₙ]] (2 a 30, x estrictamente
      crecientes, espaciado libre) y, opcional, `compare_function`.
    """

    mode = serializers.ChoiceField(
        choices=["function", "table"], default="function",
        error_messages={"invalid_choice": "El modo debe ser «function» o «table»."},
    )
    function = serializers.CharField(required=False, allow_blank=True, default="", trim_whitespace=True)
    a = serializers.FloatField(required=False, allow_null=True, default=None)
    b = serializers.FloatField(required=False, allow_null=True, default=None)
    n0 = serializers.IntegerField(default=DEFAULT_N0)
    tolerance = serializers.FloatField(default=DEFAULT_TOLERANCE)
    max_iterations = serializers.IntegerField(default=DEFAULT_MAX_REFINEMENTS)
    points = serializers.JSONField(required=False, allow_null=True, default=None)
    compare_function = serializers.CharField(required=False, allow_blank=True, default="", trim_whitespace=True)

    def validate(self, data):
        if data["mode"] == "table":
            validate_points(data["points"], MIN_POINTS, MAX_POINTS)
            if data["compare_function"]:
                errors = _function_errors(data["compare_function"], "Función para comparar")
                if errors:
                    raise serializers.ValidationError({"compare_function": errors})
            return data

        errors = {}
        if not data["function"]:
            errors["function"] = ["Escribe la función f(x)."]
        else:
            function_errors = _function_errors(data["function"], "f(x)")
            if function_errors:
                errors["function"] = function_errors
        for name in ("a", "b"):
            if data[name] is None:
                errors[name] = [f"Falta el límite {'inferior a' if name == 'a' else 'superior b'}."]
            elif not _finite(data[name]):
                errors[name] = [f"El límite {name} debe ser un número real finito de magnitud razonable."]
        if "a" not in errors and "b" not in errors and not data["a"] < data["b"]:
            errors["b"] = ["El límite inferior a debe ser menor que el límite superior b."]
        if not MIN_N0 <= data["n0"] <= MAX_N0:
            errors["n0"] = [f"Los segmentos iniciales n₀ deben ser un entero entre {MIN_N0} y {MAX_N0}."]
        if not (_finite(data["tolerance"]) and data["tolerance"] > 0):
            errors["tolerance"] = ["La tolerancia del error estimado debe ser mayor que 0."]
        if not MIN_REFINEMENTS <= data["max_iterations"] <= MAX_REFINEMENTS:
            errors["max_iterations"] = [
                f"El máximo de refinamientos debe estar entre {MIN_REFINEMENTS} y {MAX_REFINEMENTS}."
            ]
        if errors:
            raise serializers.ValidationError(errors)
        return data
