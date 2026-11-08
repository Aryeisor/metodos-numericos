import math

from rest_framework import serializers

from ..expressions.parser import MAX_MAGNITUDE
from ..solvers.differentiation.finite_differences import (
    DEFAULT_H0,
    DEFAULT_MAX_REFINEMENTS,
    DEFAULT_TOLERANCE,
    MAX_POINTS,
    MAX_REFINEMENTS,
    MIN_POINTS,
    MIN_REFINEMENTS,
    DifferentiationValidationError,
    parse_function_of_x,
)
from ..solvers.differentiation import display
from ..solvers.differentiation.five_point import DEFAULT_TOLERANCE as FIVE_POINT_TOLERANCE
from ..solvers.differentiation.five_point import MIN_POINTS as FIVE_POINT_MIN_POINTS
from ..solvers.differentiation.formulas import CHOICES, FIVE_POINT_CHOICES, THREE_POINT_CHOICES
from ..solvers.differentiation.three_point import DEFAULT_TOLERANCE as THREE_POINT_TOLERANCE
from ..solvers.differentiation.three_point import MIN_POINTS as THREE_POINT_MIN_POINTS


def _finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) \
        and abs(value) <= MAX_MAGNITUDE


def validate_points(points, min_points, max_points):
    """Tabla [[x₁, y₁], ..., [xₙ, yₙ]]: entre min_points y max_points pares de
    números finitos, con x estrictamente crecientes. Errores por fila."""
    if not isinstance(points, list):
        raise serializers.ValidationError({"points": ["Faltan los puntos (xᵢ, yᵢ) de la tabla."]})
    if not min_points <= len(points) <= max_points:
        raise serializers.ValidationError({
            "points": [f"La tabla debe tener entre {min_points} y {max_points} puntos (tiene {len(points)})."]
        })

    errors = []
    for i, point in enumerate(points, start=1):
        if not (isinstance(point, list) and len(point) == 2):
            errors.append(f"Fila {i}: cada punto debe ser un par [x, y].")
            continue
        for name, value in zip(("x", "y"), point):
            if value is None:
                errors.append(f"Fila {i}: falta el valor de {name}.")
            elif not _finite(value):
                errors.append(f"Fila {i}: {name} debe ser un número real finito de magnitud razonable.")
    if not errors:
        for i in range(1, len(points)):
            if not points[i][0] > points[i - 1][0]:
                errors.append(
                    f"Fila {i + 1}: los valores de x deben ser estrictamente crecientes "
                    f"(x{i + 1} = {points[i][0]:g} no es mayor que x{i} = {points[i - 1][0]:g})."
                )
    if errors:
        raise serializers.ValidationError({"points": errors})


class DifferentiationSerializer(serializers.Serializer):
    """Entrada de las fórmulas de diferencias, en uno de dos modos:

    - "function": `function` (f(x) como texto), `x0`, `h0`, `tolerance` y
      `max_iterations` (máximo de refinamientos de h, de 6 a 30).
    - "table": `points` = [[x₁, y₁], ..., [xₙ, yₙ]] (2 a 20, x estrictamente
      crecientes) y, opcional, `compare_function`.

    En ambos, `formula` es "forward", "backward" o "both". Los errores se
    devuelven como listas planas de mensajes por campo.
    """

    mode = serializers.ChoiceField(
        choices=["function", "table"], default="function",
        error_messages={"invalid_choice": "El modo debe ser «function» o «table»."},
    )
    formula = serializers.ChoiceField(
        choices=list(CHOICES), default="both",
        error_messages={"invalid_choice": "La fórmula debe ser «forward», «backward» o «both»."},
    )
    function = serializers.CharField(required=False, allow_blank=True, default="", trim_whitespace=True)
    x0 = serializers.FloatField(required=False, allow_null=True, default=None)
    h0 = serializers.FloatField(default=DEFAULT_H0)
    tolerance = serializers.FloatField(default=DEFAULT_TOLERANCE)
    max_iterations = serializers.IntegerField(default=DEFAULT_MAX_REFINEMENTS)
    points = serializers.JSONField(required=False, allow_null=True, default=None)
    compare_function = serializers.CharField(required=False, allow_blank=True, default="", trim_whitespace=True)

    min_points = MIN_POINTS

    def validate(self, data):
        if data["mode"] == "table":
            return self._validate_table(data)
        return self._validate_function(data)

    def _validate_function(self, data):
        errors = {}
        if not data["function"]:
            errors["function"] = ["Escribe la función f(x)."]
        else:
            try:
                parse_function_of_x(data["function"])
            except DifferentiationValidationError as exc:
                errors["function"] = [f"f(x): {message}" for message in exc.errors]
        if data["x0"] is None:
            errors["x0"] = ["Falta el valor de x₀."]
        elif not _finite(data["x0"]):
            errors["x0"] = ["x₀ debe ser un número real finito de magnitud razonable."]
        if not (_finite(data["h0"]) and data["h0"] > 0):
            errors["h0"] = ["El paso inicial h₀ debe ser un número mayor que 0."]
        if not (_finite(data["tolerance"]) and data["tolerance"] > 0):
            errors["tolerance"] = ["La tolerancia del error estimado debe ser mayor que 0."]
        if not MIN_REFINEMENTS <= data["max_iterations"] <= MAX_REFINEMENTS:
            errors["max_iterations"] = [
                f"El máximo de refinamientos de h debe estar entre {MIN_REFINEMENTS} y {MAX_REFINEMENTS}."
            ]
        if errors:
            raise serializers.ValidationError(errors)
        return data

    def _validate_table(self, data):
        validate_points(data["points"], self.min_points, MAX_POINTS)

        if data["compare_function"]:
            try:
                parse_function_of_x(data["compare_function"])
            except DifferentiationValidationError as exc:
                raise serializers.ValidationError(
                    {"compare_function": [f"Función para comparar: {m}" for m in exc.errors]}
                ) from exc
        return data


# Espaciado uniforme: |hᵢ − h₁| ≤ UNIFORM_RELATIVE · máx(1, |h₁|).
UNIFORM_RELATIVE = 1e-9


class ThreePointSerializer(DifferentiationSerializer):
    """Entrada de la fórmula de 3 puntos: la misma que la de diferencias, con
    `formula` = "punto_medio", "extremo_adelante", "extremo_atras" o "all",
    tolerancia por defecto 10⁻⁶ y, en modo tabla, de 3 a 20 puntos igualmente
    espaciados."""

    formula = serializers.ChoiceField(
        choices=list(THREE_POINT_CHOICES), default="all",
        error_messages={
            "invalid_choice": "La fórmula debe ser «punto_medio», «extremo_adelante», «extremo_atras» o «all»."
        },
    )
    tolerance = serializers.FloatField(default=THREE_POINT_TOLERANCE)

    min_points = THREE_POINT_MIN_POINTS
    method_label = "La fórmula de 3 puntos"

    def _validate_table(self, data):
        data = super()._validate_table(data)
        xs = [x for x, _ in data["points"]]
        first = xs[1] - xs[0]
        for i in range(1, len(xs) - 1):
            step = xs[i + 1] - xs[i]
            if abs(step - first) > UNIFORM_RELATIVE * max(1.0, abs(first)):
                shown = [display.decimal(display.exact(b) - display.exact(a))["text"]
                         for a, b in ((xs[i], xs[i + 1]), (xs[0], xs[1]))]
                raise serializers.ValidationError({"points": [
                    f"{self.method_label} necesita datos igualmente espaciados: entre la fila "
                    f"{i + 1} y la {i + 2} el espaciado es {shown[0]} y el de la primera pareja es {shown[1]}."
                ]})
        return data


class FivePointSerializer(ThreePointSerializer):
    """Entrada de la fórmula de 5 puntos: la de 3 puntos con `formula` =
    "punto_medio_5", "extremo_adelante_5", "extremo_atras_5" o "all" y, en modo
    tabla, de 5 a 20 puntos igualmente espaciados."""

    formula = serializers.ChoiceField(
        choices=list(FIVE_POINT_CHOICES), default="all",
        error_messages={
            "invalid_choice": "La fórmula debe ser «punto_medio_5», «extremo_adelante_5», «extremo_atras_5» o «all»."
        },
    )
    tolerance = serializers.FloatField(default=FIVE_POINT_TOLERANCE)

    min_points = FIVE_POINT_MIN_POINTS
    method_label = "La fórmula de 5 puntos"
