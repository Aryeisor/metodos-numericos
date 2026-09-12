"""Ejemplos precargados de sistemas de ecuaciones lineales.

Cada ejemplo tiene al menos 3 variables. Se sirven a través del endpoint
GET /api/examples/ para que el frontend los pueda cargar con un clic.
"""

EXAMPLES = [
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
