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


# Sistemas no lineales para Newton. Las variables se declaran en orden por
# separado (no se despeja ninguna ecuación). Todos convergen desde el x0
# indicado; el primero es el mismo sistema del ejemplo «Algebraico 2x2» de
# Punto Fijo, para comparar ambos métodos.
NEWTON_EXAMPLES = [
    {
        "id": "newton-algebraico-2x2",
        "name": "Algebraico 2x2",
        "description": "El mismo sistema del ejemplo de Punto Fijo: compara cuántas iteraciones necesita cada método.",
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
    {
        "id": "newton-chapra-2x2",
        "name": "Clásico 2x2 (Chapra)",
        "description": "x² + xy = 10 y y + 3xy² = 57 desde (1.5, 3.5); solución exacta (2, 3).",
        "n": 2,
        "variables": ["x", "y"],
        "equations": [
            "x^2 + x*y - 10 = 0",
            "y + 3*x*y^2 - 57 = 0",
        ],
        "x0": [1.5, 3.5],
        "tolerance": 0.000001,
        "max_iterations": 100,
    },
    {
        "id": "newton-burden-faires-3x3",
        "name": "Burden y Faires 3x3",
        "description": "Coseno, seno y exponencial con tres variables; solución (0.5, 0, -π/6).",
        "n": 3,
        "variables": ["x1", "x2", "x3"],
        "equations": [
            "3*x1 - cos(x2*x3) - 1/2 = 0",
            "x1^2 - 81*(x2 + 0.1)^2 + sin(x3) + 1.06 = 0",
            "exp(-x1*x2) + 20*x3 + (10*pi - 3)/3 = 0",
        ],
        "x0": [0.1, 0.1, -0.1],
        "tolerance": 0.000001,
        "max_iterations": 100,
    },
]


def _polynomial_example(id, name, description, degree, *, text=None, coefficients=None,
                        r0=-1, s0=-1, tolerance=0.0001):
    """Ejemplo de Bairstow en modo texto o en modo coeficientes (uno de los dos)."""
    return {
        "id": id,
        "name": name,
        "description": description,
        "n": degree,
        "mode": "text" if text is not None else "coefficients",
        "polynomial": text,
        "coefficients": coefficients,
        "r0": r0,
        "s0": s0,
        "tolerance": tolerance,  # en porcentaje
        "max_iterations": 100,
    }


# Polinomios para Bairstow. Cada expansión se verificó con sympy contra sus
# raíces, y cada ejemplo converge con el r₀ y s₀ indicados (−1 y −1 salvo
# donde se aclara). Unos se cargan como texto y otros como coeficientes.
POLYNOMIAL_EXAMPLES = [
    _polynomial_example(
        "bairstow-chapra", "Clásico de Chapra y Canale",
        "Grado 5; raíces −1, 0.5, 2 y 1 ± 0.5i. Tolerancia 1 %, como en el libro.", 5,
        text="x^5 - 3.5x^4 + 2.75x^3 + 2.125x^2 - 3.875x + 1.25", tolerance=1,
    ),
    _polynomial_example(
        "bairstow-cubica-reales", "Cúbica con raíces reales",
        "x³ − 6x² + 11x − 6, raíces 1, 2 y 3.", 3,
        coefficients=[1, -6, 11, -6],
    ),
    _polynomial_example(
        "bairstow-cubica-compleja", "Cúbica con par complejo",
        "x³ − x² + x − 1, raíces 1 y ± i. Desde r₀ = s₀ = −1 el sistema se vuelve singular: usa r₀ = 0.5, s₀ = −0.5.", 3,
        text="x^3 - x^2 + x - 1", r0=0.5, s0=-0.5,
    ),
    _polynomial_example(
        "bairstow-terminos-faltantes", "Términos faltantes",
        "x⁴ − 5x² + 4: coeficientes 0 en x³ y x; raíces ±1 y ±2.", 4,
        coefficients=[1, 0, -5, 0, 4],
    ),
    _polynomial_example(
        "bairstow-dos-pares", "Dos pares complejos",
        "x⁴ − 2x³ + 6x² − 2x + 5, raíces ± i y 1 ± 2i.", 4,
        text="x^4 - 2x^3 + 6x^2 - 2x + 5",
    ),
    _polynomial_example(
        "bairstow-principal-2", "Coeficiente principal ≠ 1",
        "2x³ + x² + x − 1, raíces 0.5 y (−1 ± i√3)/2.", 3,
        coefficients=[2, 1, 1, -1],
    ),
    _polynomial_example(
        "bairstow-grado-6", "Grado 6, tres factores",
        "x⁶ − x⁵ + 2x⁴ − 6x³ − 4x² − 8x + 16, raíces −1 ± i, 1, 2 y ± 2i.", 6,
        text="x^6 - x^5 + 2x^4 - 6x^3 - 4x^2 - 8x + 16",
    ),
    _polynomial_example(
        "bairstow-raiz-nula", "Con raíz nula (paso previo)",
        "x⁵ − x⁴ − 7x³ + x² + 6x: primero se extrae x = 0; raíces 0, 1, −1, 3 y −2.", 5,
        text="x^5 - x^4 - 7x^3 + x^2 + 6x",
    ),
]


EXAMPLES = {
    "jacobi": LINEAR_SYSTEM_EXAMPLES,
    "gauss-seidel": LINEAR_SYSTEM_EXAMPLES,
    "punto-fijo": NONLINEAR_SYSTEM_EXAMPLES,
    "newton": NEWTON_EXAMPLES,
    "bairstow": POLYNOMIAL_EXAMPLES,
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
