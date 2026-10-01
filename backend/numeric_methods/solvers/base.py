"""Estructura común de resultado para todos los métodos iterativos.

Cada método (lineal, no lineal, polinomial) devuelve un `SolverResult`. Los
nombres de los campos siguen el contrato que la API ya expone (`iteration`,
`x`, `error`, `solution`), así que serializar un resultado de Jacobi o
Gauss-Seidel produce exactamente la misma respuesta que antes del registro de
métodos.

No depende de Django: puede usarse y testearse de forma aislada.
"""

from dataclasses import dataclass, field


@dataclass
class IterationStep:
    """Una fila de la tabla de iteraciones.

    x: valores de la iteración, en el orden de `SolverResult.variables`.
    error: diferencia con la iteración anterior (None si no es calculable).
    extra: datos propios del método para el detalle expandible (por ejemplo,
        el jacobiano evaluado en Newton). Sólo se serializa si no está vacío.
    """

    iteration: int
    x: list
    error: float | None
    extra: dict = field(default_factory=dict)

    def to_dict(self):
        data = {"iteration": self.iteration, "x": self.x, "error": self.error}
        if self.extra:
            data["extra"] = self.extra
        return data


@dataclass
class SolverResult:
    """Resultado de un método, independiente de cómo se describa su entrada.

    variables: nombres de las incógnitas, en el orden de `solution` y de cada
        `IterationStep.x` (ej. ["x1", "x2", "x3"], o ["r", "s"] en Bairstow).
    meta: datos propios de la familia del método. Se serializan al primer
        nivel de la respuesta (ej. `A`, `b`, `reordered` y `row_order` en los
        sistemas lineales) y no pueden pisar los campos comunes.
    """

    method: str
    category: str
    converged: bool
    iterations: list
    solution: list
    variables: list
    warnings: list = field(default_factory=list)
    meta: dict = field(default_factory=dict)

    @property
    def iterations_used(self):
        return len(self.iterations)

    def to_dict(self):
        data = {
            "method": self.method,
            "category": self.category,
            "converged": self.converged,
            "iterations": [step.to_dict() for step in self.iterations],
            "iterations_used": self.iterations_used,
            "solution": self.solution,
            "variables": self.variables,
            "warnings": self.warnings,
        }
        clashes = data.keys() & self.meta.keys()
        if clashes:
            raise ValueError(f"meta no puede redefinir campos comunes: {sorted(clashes)}")
        data.update(self.meta)
        return data
