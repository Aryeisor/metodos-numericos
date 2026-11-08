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
from ..solvers.differentiation import display
from ..solvers.integration import romberg, simpson
from ..solvers.validation import InputValidationError
from .differentiation import UNIFORM_RELATIVE, _finite, validate_points


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

    min_points = MIN_POINTS
    max_points = MAX_POINTS
    max_rows = MAX_REFINEMENTS
    rows_error = "El máximo de refinamientos debe estar entre {low} y {high}."

    def validate(self, data):
        if data["mode"] == "table":
            validate_points(data["points"], self.min_points, self.max_points)
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
        if not MIN_REFINEMENTS <= data["max_iterations"] <= self.max_rows:
            errors["max_iterations"] = [self.rows_error.format(low=MIN_REFINEMENTS, high=self.max_rows)]
        if errors:
            raise serializers.ValidationError(errors)
        return data


class SimpsonSerializer(IntegrationSerializer):
    """Entrada del método de Simpson: la misma del trapecio, más

    - `rule`: "simpson13", "simpson38" o "both" (por defecto);
    - `n0_13` (par, de 2 a 1000, por defecto 2) y `n0_38` (múltiplo de 3, de
      3 a 999, por defecto 3): los segmentos iniciales de cada regla pedida;
    - en modo tabla, de 3 a 30 puntos igualmente espaciados.
    """

    rule = serializers.ChoiceField(
        choices=list(simpson.RULE_CHOICES), default="both",
        error_messages={"invalid_choice": "La regla debe ser «simpson13», «simpson38» o «both»."},
    )
    n0_13 = serializers.IntegerField(default=simpson.DEFAULT_N0["simpson13"])
    n0_38 = serializers.IntegerField(default=simpson.DEFAULT_N0["simpson38"])

    min_points = simpson.MIN_POINTS

    def validate(self, data):
        points = data.get("points")
        if data["mode"] == "table" and isinstance(points, list) and len(points) < simpson.MIN_POINTS:
            raise serializers.ValidationError({"points": [
                f"Simpson necesita al menos {simpson.MIN_POINTS} puntos: se necesitan al menos 2 segmentos "
                f"(la tabla tiene {len(points)} {'punto' if len(points) == 1 else 'puntos'})."
            ]})
        data = super().validate(data)
        if data["mode"] == "table":
            self._validate_spacing([x for x, _ in data["points"]])
            return data
        errors = {}
        for rule in simpson.RULE_CHOICES[data["rule"]]:
            field = simpson.N0_FIELDS[rule.key]
            n0, low, high = data[field], simpson.MIN_N0[rule.key], simpson.MAX_N0[rule.key]
            if n0 % rule.segments_multiple:
                errors[field] = [
                    "Simpson 1/3 necesita un número par de segmentos, porque cada parábola ocupa 2 segmentos "
                    f"(n₀ = {n0})." if rule.segments_multiple == 2 else
                    "Simpson 3/8 necesita un número de segmentos múltiplo de 3, porque cada cúbica ocupa 3 "
                    f"segmentos (n₀ = {n0})."
                ]
            elif not low <= n0 <= high:
                errors[field] = [f"Los segmentos iniciales n₀ de {rule.name} deben estar entre {low} y {high}."]
        if errors:
            raise serializers.ValidationError(errors)
        return data

    @staticmethod
    def _validate_spacing(xs, method="Simpson"):
        first = xs[1] - xs[0]
        for i in range(1, len(xs) - 1):
            if abs(xs[i + 1] - xs[i] - first) > UNIFORM_RELATIVE * max(1.0, abs(first)):
                shown = [display.decimal(display.exact(b) - display.exact(a))["text"]
                         for a, b in ((xs[i], xs[i + 1]), (xs[0], xs[1]))]
                raise serializers.ValidationError({"points": [
                    f"{method} necesita datos igualmente espaciados: entre la fila {i + 1} y la {i + 2} el "
                    f"espaciado es {shown[0]} y el de la primera pareja es {shown[1]}. Con datos de espaciado "
                    "desigual puedes usar el método del trapecio."
                ]})


class RombergSerializer(IntegrationSerializer):
    """Entrada de la integración de Romberg: la misma del trapecio, pero

    - sin `n0` (Romberg siempre empieza con n = 1; si llega, se ignora);
    - `max_iterations` es el máximo de filas, de 6 a 20 (por defecto 15);
    - en modo tabla, 2ᵐ + 1 puntos (3, 5, 9, 17 o 33) igualmente espaciados.
    """

    max_iterations = serializers.IntegerField(default=romberg.DEFAULT_MAX_ROWS)

    min_points = romberg.MIN_POINTS
    max_points = romberg.MAX_POINTS
    max_rows = romberg.MAX_ROWS
    rows_error = "El máximo de filas debe estar entre {low} y {high}."

    def validate(self, data):
        points = data.get("points")
        if data["mode"] == "table" and isinstance(points, list) and len(points) not in romberg.TABLE_POINTS:
            raise serializers.ValidationError({"points": [
                "Romberg necesita 2ᵐ + 1 puntos igualmente espaciados (3, 5, 9, 17 o 33), porque cada fila duplica "
                f"el número de segmentos. Tienes {len(points)} {'punto' if len(points) == 1 else 'puntos'}: puedes "
                "usar el trapecio o Simpson."
            ]})
        data = super().validate(data)
        if data["mode"] == "table":
            SimpsonSerializer._validate_spacing([x for x, _ in data["points"]], "Romberg")
        return data
