from rest_framework import serializers

from ..expressions.parser import ExpressionError, make_symbols, parse_equation
from ..expressions.to_latex import equation_to_latex

# Más que suficiente para cualquier método (Punto Fijo admite 6); acota el
# trabajo de una petición que el frontend hace mientras el usuario escribe.
MAX_PREVIEW_VARIABLES = 20


class ExpressionPreviewSerializer(serializers.Serializer):
    """Valida una ecuación escrita por el usuario y la convierte a LaTeX.

    Sólo parsea, con el mismo parser endurecido que usan los métodos (mismos
    límites de longitud, anidamiento, magnitud...): no despeja ni resuelve.
    Los errores se devuelven como listas planas de mensajes por campo.
    """

    equation = serializers.CharField(
        allow_blank=True,
        trim_whitespace=False,
        error_messages={
            "required": "Falta la ecuación.",
            "invalid": "La ecuación debe ser texto.",
            "null": "Falta la ecuación.",
        },
    )
    variables = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        max_length=MAX_PREVIEW_VARIABLES,
        error_messages={
            "required": "Faltan las variables del sistema.",
            "not_a_list": "Las variables deben enviarse como una lista.",
            "max_length": f"Se admiten como máximo {MAX_PREVIEW_VARIABLES} variables.",
        },
    )

    def validate(self, data):
        variables = data["variables"]
        try:
            make_symbols(variables)
        except ExpressionError as exc:
            raise serializers.ValidationError({"variables": [str(exc)]}) from exc

        try:
            name, lhs, rhs = parse_equation(data["equation"], variables)
        except ExpressionError as exc:
            raise serializers.ValidationError({"equation": [str(exc)]}) from exc

        data["latex"] = equation_to_latex(name, lhs, rhs, variables)
        return data
