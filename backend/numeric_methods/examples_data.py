"""Ejemplos precargados, organizados por método.

Se sirven a través de GET /api/examples/?method=<slug> para que el frontend
los pueda cargar con un clic. Los métodos de una misma familia pueden
compartir la misma lista (Jacobi y Gauss-Seidel resuelven los mismos
sistemas).
"""

# Sistemas lineales: cada ejemplo tiene al menos 3 variables.
LINEAR_SYSTEM_EXAMPLES = [
    {
        "id": "basico-3x3",
        "name": "Sistema básico 3x3",
        "description": (
            "Sistema diagonalmente dominante sencillo, ideal para el primer "
            "contacto con los métodos iterativos."
        ),
        "n": 3,
        "A": [
            [4, 1, 1],
            [2, 5, 2],
            [1, 2, 4],
        ],
        "b": [6, 9, 7],
        "x0": [0, 0, 0],
        "tolerance": 0.000001,
        "max_iterations": 100,
    },
    {
        "id": "clasico-3x3",
        "name": "Sistema clásico 3x3 (libro de texto)",
        "description": (
            "Ejemplo clásico de convergencia rápida, fuertemente diagonalmente "
            "dominante. Solución exacta conocida: x = (1, 2, -1)."
        ),
        "n": 3,
        "A": [
            [10, -1, 2],
            [-1, 11, -1],
            [2, -1, 10],
        ],
        "b": [6, 22, -10],
        "x0": [0, 0, 0],
        "tolerance": 0.000001,
        "max_iterations": 100,
    },
    {
        "id": "dominante-4x4",
        "name": "Sistema diagonalmente dominante 4x4",
        "description": "Sistema de 4 variables, diagonalmente dominante, converge en pocas iteraciones.",
        "n": 4,
        "A": [
            [10, 2, 3, 1],
            [1, 12, 1, 2],
            [2, 1, 15, 1],
            [1, 2, 1, 14],
        ],
        "b": [23, 17, 22, 20],
        "x0": [0, 0, 0, 0],
        "tolerance": 0.000001,
        "max_iterations": 100,
    },
    {
        "id": "no-dominante-3x3",
        "name": "Sistema 3x3 sin dominancia diagonal (advertencia)",
        "description": (
            "Este sistema NO es diagonalmente dominante. Sirve para comprobar "
            "que la aplicación advierte al usuario y que la convergencia no "
            "está garantizada (puede no converger)."
        ),
        "n": 3,
        "A": [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 10],
        ],
        "b": [6, 15, 25],
        "x0": [0, 0, 0],
        "tolerance": 0.000001,
        "max_iterations": 100,
    },
    {
        "id": "dominante-5x5",
        "name": "Sistema diagonalmente dominante 5x5",
        "description": "Sistema de 5 variables, diagonalmente dominante, para probar el caso general n x n.",
        "n": 5,
        "A": [
            [12, 1, 1, 1, 0],
            [1, 14, 2, 0, 1],
            [1, 1, 15, 1, 1],
            [0, 1, 1, 13, 2],
            [1, 0, 1, 1, 11],
        ],
        "b": [20, 25, 30, 22, 18],
        "x0": [0, 0, 0, 0, 0],
        "tolerance": 0.000001,
        "max_iterations": 100,
    },
    {
        "id": "decimales-3x3",
        "name": "Sistema con coeficientes decimales",
        "description": "Sistema 3x3 diagonalmente dominante con coeficientes no enteros.",
        "n": 3,
        "A": [
            [5, 0.5, 1],
            [0.4, 6, 0.3],
            [1, 0.2, 4],
        ],
        "b": [7.5, 12.3, 9.8],
        "x0": [0, 0, 0],
        "tolerance": 0.000001,
        "max_iterations": 100,
    },
]

# Sistemas no lineales f_i(x) = 0. La ecuación i se despeja automáticamente
# para la variable i, así que cada una debe tener un único despeje real de su
# variable. Todos convergen con punto fijo secuencial desde el x0 indicado.
NONLINEAR_SYSTEM_EXAMPLES = [
    {
        "id": "trigonometrico-2x2",
        "name": "Trigonométrico 2x2",
        "description": "Dos ecuaciones con seno y coseno; variables x, y.",
        "n": 2,
        "variables": ["x", "y"],
        "equations": [
            "3*x - cos(y) - 1 = 0",
            "4*y - sin(x) - 2 = 0",
        ],
        "x0": [0, 0],
        "tolerance": 0.000001,
        "max_iterations": 100,
    },
    {
        "id": "burden-faires-3x3",
        "name": "Burden y Faires 3x3",
        "description": "Ejemplo clásico con coseno, raíz y exponencial; solución (0.5, 0, -π/6).",
        "n": 3,
        "variables": ["x1", "x2", "x3"],
        "equations": [
            "3*x1 - cos(x2*x3) - 1/2 = 0",
            "x2 = sqrt(x1^2 + sin(x3) + 1.06)/9 - 0.1",
            "exp(-x1*x2) + 20*x3 + (10*pi - 3)/3 = 0",
        ],
        "x0": [0.1, 0.1, -0.1],
        "tolerance": 0.000001,
        "max_iterations": 100,
    },
    {
        "id": "polinomico-3x3",
        "name": "Polinómico 3x3",
        "description": "Términos cuadráticos y productos cruzados, desde el origen.",
        "n": 3,
        "variables": ["x1", "x2", "x3"],
        "equations": [
            "6*x1 - x2^2 - x3 - 1 = 0",
            "8*x2 - x1*x3 - 2 = 0",
            "5*x3 - x1 - x2^2 - 3 = 0",
        ],
        "x0": [0, 0, 0],
        "tolerance": 0.000001,
        "max_iterations": 100,
    },
    {
        "id": "algebraico-2x2",
        "name": "Algebraico 2x2",
        "description": "Dos ecuaciones polinómicas simples, sin trigonometría; buen primer contacto con el despeje automático.",
        "n": 2,
        "variables": ["x", "y"],
        "equations": [
            "3*x - y**2 - 1 = 0",
            "x**2 + 4*y - 2 = 0",
        ],
        "x0": [0, 0],
        "tolerance": 0.000001,
        "max_iterations": 100,
    },
]


EXAMPLES = {
    "jacobi": LINEAR_SYSTEM_EXAMPLES,
    "gauss-seidel": LINEAR_SYSTEM_EXAMPLES,
    "punto-fijo": NONLINEAR_SYSTEM_EXAMPLES,
}


def all_examples():
    """Todos los ejemplos sin repetir, en orden de aparición."""
    seen, unique = set(), []
    for examples in EXAMPLES.values():
        for example in examples:
            if example["id"] not in seen:
                seen.add(example["id"])
                unique.append(example)
    return unique
