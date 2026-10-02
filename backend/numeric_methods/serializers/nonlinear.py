from rest_framework import serializers

from ..expressions.parser import ExpressionError, make_symbols, parse_function
from ..solvers.nonlinear.common import MAX_EQUATIONS, MIN_EQUATIONS
from ..solvers.nonlinear.newton import structure_errors
from ..solvers.validation import DEFAULT_MAX_ITERATIONS, DEFAULT_TOLERANCE


class NonlinearSystemSerializer(serializers.Serializer):
    """Valida la entrada de un sistema no lineal f_i(x_1, ..., x_n) = 0.

    Los errores se devuelven como listas planas de mensajes por campo (no por
    posición de la lista), que es lo que el frontend sabe mostrar.
    """

    equations = serializers.ListField(
        child=serializers.CharField(allow_blank=True, trim_whitespace=True),
        help_text='Ecuaciones como texto, una por variable (ej. "3*x - cos(y) - 1 = 0").',
    )
    variables = serializers.ListField(
        child=serializers.CharField(allow_blank=True, trim_whitespace=True),
        help_text="Nombres de las variables; la ecuación i se despeja para la variable i.",
    )
    x0 = serializers.ListField(
        child=serializers.FloatField(),
        required=False,
        allow_null=True,
        help_text="Punto inicial x0 (opcional, por defecto ceros).",
    )
    tolerance = serializers.FloatField(
        default=DEFAULT_TOLERANCE,
        min_value=0,
        help_text="Tolerancia de error entre iteraciones sucesivas (ej. 0.000001).",
    )
    max_iterations = serializers.IntegerField(
        default=DEFAULT_MAX_ITERATIONS,
        min_value=1,
        help_text="Número máximo de iteraciones permitidas.",
    )

    def validate(self, data):
        equations = data["equations"]
        variables = data["variables"]
        x0 = data.get("x0")
        n = len(equations)

        if not MIN_EQUATIONS <= n <= MAX_EQUATIONS:
            raise serializers.ValidationError(
                {
                    "equations": [
                        f"El sistema debe tener entre {MIN_EQUATIONS} y {MAX_EQUATIONS} "
                        f"ecuaciones (tiene {n})."
                    ]
                }
            )

        errors = {}
        if len(variables) != n:
            errors["variables"] = [
                f"Debe haber una variable por ecuación ({n} ecuaciones, "
                f"{len(variables)} variables)."
            ]
        elif any(not name for name in variables):
            errors["variables"] = ["Los nombres de las variables no pueden estar vacíos."]
        else:
            try:
                make_symbols(variables)
            except ExpressionError as exc:
                errors["variables"] = [str(exc)]

        if x0 is not None and len(x0) != n:
            errors["x0"] = [f"El punto inicial x0 debe tener exactamente {n} valores."]

        if errors:
            raise serializers.ValidationError(errors)

        equation_errors = []
        for i, text in enumerate(equations):
            if not text:
                equation_errors.append(f"Ecuación {i + 1}: está vacía.")
                continue
            try:
                parse_function(text, variables)
            except ExpressionError as exc:
                equation_errors.append(f"Ecuación {i + 1}: {exc}")
        if equation_errors:
            raise serializers.ValidationError({"equations": equation_errors})

        return data


class NewtonSystemSerializer(NonlinearSystemSerializer):
    """Entrada de Newton: la misma forma que Punto Fijo (ecuaciones, variables
    en orden, x0, tolerancia, máximo de iteraciones). Aquí las variables no se
    asocian a una ecuación: su orden fija el orden de las columnas del
    Jacobiano y de x0.

    Además rechaza los sistemas cuyo Jacobiano sería singular en cualquier
    punto: una variable que no aparece en ninguna ecuación, o una ecuación
    sin variables.
    """

    def validate(self, data):
        data = super().validate(data)
        variables = data["variables"]
        symbols = list(make_symbols(variables).values())
        functions = [parse_function(text, variables)[1] for text in data["equations"]]
        errors = structure_errors(functions, symbols)
        if errors:
            raise serializers.ValidationError({"equations": errors})
        return data
