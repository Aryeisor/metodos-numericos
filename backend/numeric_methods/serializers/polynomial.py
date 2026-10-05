import math

from rest_framework import serializers

from ..expressions.parser import MAX_MAGNITUDE
from ..solvers.polynomial.validation import (
    DEFAULT_R0,
    DEFAULT_S0,
    DEFAULT_TOLERANCE_PERCENT,
    PolynomialValidationError,
    coefficients_from_text,
    validate_coefficients,
)
from ..solvers.validation import DEFAULT_MAX_ITERATIONS


class PolynomialSerializer(serializers.Serializer):
    """Entrada de Bairstow: el polinomio como texto (`polynomial`) o como
    lista de coeficientes en orden descendente (`coefficients`), exactamente
    uno de los dos.

    Tras validar, `coefficients` siempre queda con los coeficientes (los del
    texto, si se envió texto), así que el solver no distingue el modo. Los
    errores se devuelven como listas planas de mensajes por campo.
    """

    polynomial = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        trim_whitespace=True,
        help_text='Polinomio en x, ej. "x^3 - 6x^2 + 11x - 6" (o "… = 0").',
    )
    coefficients = serializers.ListField(
        child=serializers.FloatField(),
        required=False,
        allow_null=True,
        help_text="Coeficientes en orden descendente, de aₙ a a₀.",
    )
    r0 = serializers.FloatField(default=DEFAULT_R0, help_text="Valor inicial de r (por defecto −1).")
    s0 = serializers.FloatField(default=DEFAULT_S0, help_text="Valor inicial de s (por defecto −1).")
    tolerance = serializers.FloatField(
        default=DEFAULT_TOLERANCE_PERCENT,
        help_text="Tolerancia εs del error relativo, en porcentaje (ej. 0.0001).",
    )
    max_iterations = serializers.IntegerField(
        default=DEFAULT_MAX_ITERATIONS,
        min_value=1,
        help_text="Número máximo de iteraciones por factor.",
    )

    def validate(self, data):
        text = (data.get("polynomial") or "").strip()
        coefficients = data.get("coefficients")
        has_text, has_coefficients = bool(text), coefficients is not None

        if has_text == has_coefficients:
            raise serializers.ValidationError({
                "polynomial": [
                    "Envía exactamente uno: el polinomio como texto (polynomial) o sus "
                    "coeficientes en orden descendente (coefficients)."
                ]
            })

        errors = {}
        if not data["tolerance"] > 0:
            errors["tolerance"] = ["La tolerancia εs debe ser mayor que 0 (está en porcentaje)."]
        for name in ("r0", "s0"):
            if not math.isfinite(data[name]) or abs(data[name]) > MAX_MAGNITUDE:
                errors[name] = [f"{name} debe ser un número real finito de magnitud razonable."]
        if errors:
            raise serializers.ValidationError(errors)

        try:
            if has_text:
                data["coefficients"] = coefficients_from_text(text)
                data["polynomial"] = text
            else:
                data["coefficients"] = validate_coefficients(coefficients)
                data["polynomial"] = None
        except PolynomialValidationError as exc:
            field = "polynomial" if has_text else "coefficients"
            raise serializers.ValidationError({field: exc.errors}) from exc

        return data
