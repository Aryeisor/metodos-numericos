from rest_framework import serializers

from .solvers.validation import DEFAULT_MAX_ITERATIONS, MIN_VARIABLES


class LinearSystemSerializer(serializers.Serializer):
    """Valida la entrada de un sistema de ecuaciones lineales A x = b."""

    A = serializers.ListField(
        child=serializers.ListField(child=serializers.FloatField()),
        help_text="Matriz de coeficientes A (n x n).",
    )
    b = serializers.ListField(
        child=serializers.FloatField(),
        help_text="Vector de términos independientes b (n elementos).",
    )
    x0 = serializers.ListField(
        child=serializers.FloatField(),
        required=False,
        allow_null=True,
        help_text="Vector inicial x0 (opcional, por defecto ceros).",
    )
    tolerance = serializers.FloatField(
        default=1e-6,
        min_value=0,
        help_text="Tolerancia de error entre iteraciones sucesivas (ej. 0.000001).",
    )
    max_iterations = serializers.IntegerField(
        default=DEFAULT_MAX_ITERATIONS,
        min_value=1,
        help_text="Número máximo de iteraciones permitidas.",
    )

    def validate(self, data):
        A = data.get("A")
        b = data.get("b")
        x0 = data.get("x0")
        errors = {}

        if not A:
            errors["A"] = ["La matriz A es requerida y no puede estar vacía."]
            raise serializers.ValidationError(errors)

        n = len(A)

        if n < MIN_VARIABLES:
            errors.setdefault("A", []).append(
                f"El sistema debe tener al menos {MIN_VARIABLES} variables (n >= {MIN_VARIABLES})."
            )

        for row in A:
            if len(row) != n:
                errors.setdefault("A", []).append("La matriz A debe ser cuadrada (n x n).")
                break

        if b is None or len(b) != n:
            errors.setdefault("b", []).append(
                f"El vector b debe tener exactamente {n} elementos."
            )

        if x0 is not None and len(x0) != n:
            errors.setdefault("x0", []).append(
                f"El vector inicial x0 debe tener exactamente {n} elementos."
            )

        if errors:
            raise serializers.ValidationError(errors)

        diag_errors = []
        for i in range(n):
            if A[i][i] == 0:
                diag_errors.append(i + 1)
        if diag_errors:
            raise serializers.ValidationError(
                {
                    "A": [
                        "La diagonal principal no puede tener ceros "
                        f"(filas problemáticas: {diag_errors}); no es posible despejar esa variable."
                    ]
                }
            )

        return data
