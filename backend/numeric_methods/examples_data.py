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
    # El de la exposición: el factor cumple la tolerancia en la iteración 2
    # (se muestran las 6 del mínimo general).
    _polynomial_example(
        "bairstow-cubica-enteras", "x³ − 2x² − 5x + 6",
        "Cúbica con raíces enteras: converge en 2 iteraciones", 3,
        text="x^3 - 2x^2 - 5x + 6", tolerance=1,
    ),
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


def _difference_example(example_id, name, description, formula, tolerance=0.0001, **data):
    """Ejemplo de diferencias finitas: modo función (function, x0, h0) o modo
    tabla (points y, opcional, compare_function)."""
    mode = "table" if "points" in data else "function"
    return {
        "id": example_id,
        "name": name,
        "description": description,
        "mode": mode,
        "formula": formula,
        "function": data.get("function", ""),
        "x0": data.get("x0"),
        "h0": data.get("h0", 0.1),
        "points": data.get("points"),
        "compare_function": data.get("compare_function", ""),
        "tolerance": tolerance,
        "max_iterations": 25,
    }


# Diferencias progresiva y regresiva. Los valores esperados (README y
# tests/test_differentiation.py) se verificaron con un script independiente.
DIFFERENCE_EXAMPLES = [
    _difference_example(
        "dif-burden-ln", "ln(x) en x₀ = 1.8 (Burden y Faires)",
        "Ambas fórmulas con h₀ = 0.1; exacta f'(1.8) = 1/1.8 ≈ 0.555556.", "both",
        function="ln(x)", x0=1.8, h0=0.1,
    ),
    _difference_example(
        "dif-exp", "eˣ en x₀ = 0, progresiva",
        "La derivada exacta es 1; el error se reduce a la mitad con cada h.", "forward",
        function="exp(x)", x0=0, h0=0.1,
    ),
    _difference_example(
        "dif-seno", "sin(x) en x₀ = 1, regresiva",
        "Exacta cos(1) ≈ 0.540302 (en radianes).", "backward",
        function="sin(x)", x0=1, h0=0.1,
    ),
    _difference_example(
        "dif-cubica", "Cúbica x³ − 2x² + x en x₀ = 2",
        "Exacta f'(2) = 5; con h = 0.1, D⁺ = 5.41 y D⁻ = 4.61.", "both",
        function="x^3 - 2x^2 + x", x0=2, h0=0.1,
    ),
    _difference_example(
        "dif-lineal", "Función lineal 3x + 2",
        "f'' = 0: las dos fórmulas son exactas (error y cota 0). Para en la fila 6, el mínimo.", "both",
        function="3x + 2", x0=1, h0=0.5,
    ),
    _difference_example(
        "dif-xexp", "x·eˣ en x₀ = 2",
        "Crece rápido: exacta 3e² ≈ 22.167168; hacen falta 15 filas.", "both",
        function="x*exp(x)", x0=2, h0=0.1,
    ),
    _difference_example(
        "dif-carro", "Posición de un carro (tabla + función)",
        "x es el tiempo en segundos y f(x) la posición en metros; se compara con f(x) = 2x².", "both",
        points=[[0, 0], [1, 2], [2, 8], [3, 18], [4, 32], [5, 50]], compare_function="2x^2",
    ),
    _difference_example(
        "dif-tabla", "Tabla de datos sin función",
        "Seis datos medidos con h = 0.1: progresiva y regresiva comparten cada secante.", "both",
        points=[[1.1, 9.025013], [1.2, 11.023176], [1.3, 13.463738], [1.4, 16.444647],
                [1.5, 20.085537], [1.6, 24.53253]],
    ),
]


def _three_point_example(example_id, name, description, formula, **data):
    """Ejemplo de la fórmula de 3 puntos (tolerancia 10⁻⁶, máximo 25)."""
    return _difference_example(example_id, name, description, formula, tolerance=0.000001, **data)


# Fórmula de 3 puntos. Los valores esperados (README y tests/test_three_point.py)
# se verificaron con un script independiente.
THREE_POINT_EXAMPLES = [
    _three_point_example(
        "tp-burden-xexp", "x·eˣ en x₀ = 2 (Burden y Faires)",
        "Las tres fórmulas con h₀ = 0.1; exacta 3e² ≈ 22.167168. Para en la fila 11.", "all",
        function="x*exp(x)", x0=2, h0=0.1,
    ),
    _three_point_example(
        "tp-ln", "ln(x) en x₀ = 1.8",
        "El mismo ejemplo de diferencias, para comparar: exacta 1/1.8 ≈ 0.555556.", "all",
        function="ln(x)", x0=1.8, h0=0.1,
    ),
    _three_point_example(
        "tp-seno", "sin(x) en x₀ = 1, punto medio",
        "Exacta cos(1) ≈ 0.540302 (en radianes).", "punto_medio",
        function="sin(x)", x0=1, h0=0.1,
    ),
    _three_point_example(
        "tp-cubica", "Cúbica x³ − 2x² + x en x₀ = 2",
        "f‴ = 6 es constante: el error real es igual a la cota en cada fila.", "all",
        function="x^3 - 2x^2 + x", x0=2, h0=0.1,
    ),
    _three_point_example(
        "tp-cuadratica", "Cuadrática x² − 3x + 1 en x₀ = 2",
        "f‴ = 0: las tres fórmulas son exactas para polinomios de grado ≤ 2. Para en la fila 6.", "all",
        function="x^2 - 3x + 1", x0=2, h0=0.5,
    ),
    _three_point_example(
        "tp-gauss", "e^(−x²) en x₀ = 0.5, extremo hacia atrás",
        "Exacta −e^(−0.25) ≈ −0.778801.", "extremo_atras",
        function="exp(-x^2)", x0=0.5, h0=0.1,
    ),
    _three_point_example(
        "tp-tabla-burden", "Tabla de x·eˣ (Burden y Faires, tabla + función)",
        "Cinco datos con h = 0.1; se compara con f(x) = x·eˣ.", "all",
        points=[[1.8, 10.889365], [1.9, 12.703199], [2.0, 14.778112], [2.1, 17.148957], [2.2, 19.85503]],
        compare_function="x*exp(x)",
    ),
    _three_point_example(
        "tp-tabla-cubos", "Tabla de datos sin función",
        "Datos de x³ en x = 0, 1, …, 5: punto medio en el interior y extremos en los bordes.", "all",
        points=[[0, 0], [1, 1], [2, 8], [3, 27], [4, 64], [5, 125]],
    ),
]


# Fórmula de 5 puntos (misma tolerancia y máximo que la de 3 puntos). Los
# valores esperados (README y tests/test_five_point.py) se verificaron con un
# script independiente.
FIVE_POINT_EXAMPLES = [
    _three_point_example(
        "cp-burden-xexp", "x·eˣ en x₀ = 2 (Burden y Faires)",
        "Las tres fórmulas con h₀ = 0.1; exacta 3e² ≈ 22.167168. Punto medio 22.166996 en la fila 1.", "all",
        function="x*exp(x)", x0=2, h0=0.1,
    ),
    _three_point_example(
        "cp-ln", "ln(x) en x₀ = 1.8",
        "El mismo ejemplo de diferencias y de 3 puntos: exacta 1/1.8 ≈ 0.555556.", "all",
        function="ln(x)", x0=1.8, h0=0.1,
    ),
    _three_point_example(
        "cp-seno", "sin(x) en x₀ = 1, punto medio",
        "Exacta cos(1) ≈ 0.540302 (en radianes).", "punto_medio_5",
        function="sin(x)", x0=1, h0=0.1,
    ),
    _three_point_example(
        "cp-cuartica", "Cuártica x⁴ − 2x³ + x en x₀ = 1",
        "f⁽⁵⁾ = 0: las tres fórmulas son exactas para polinomios de grado ≤ 4 (la de 3 puntos no).", "all",
        function="x^4 - 2x^3 + x", x0=1, h0=0.5,
    ),
    _three_point_example(
        "cp-quintica", "x⁵ en x₀ = 1",
        "f⁽⁵⁾ = 120 es constante: el error real es igual a la cota en cada fila.", "all",
        function="x^5", x0=1, h0=0.5,
    ),
    _three_point_example(
        "cp-gauss", "e^(−x²) en x₀ = 0.5, extremo hacia atrás",
        "Exacta −e^(−0.25) ≈ −0.778801.", "extremo_atras_5",
        function="exp(-x^2)", x0=0.5, h0=0.1,
    ),
    _three_point_example(
        "cp-tabla-burden", "Tabla de x·eˣ (Burden y Faires, tabla + función)",
        "Nueve datos con h = 0.1; se compara con f(x) = x·eˣ.", "all",
        points=[[1.6, 7.924852], [1.7, 9.305711], [1.8, 10.889365], [1.9, 12.703199], [2.0, 14.778112],
                [2.1, 17.148957], [2.2, 19.85503], [2.3, 22.94062], [2.4, 26.455623]],
        compare_function="x*exp(x)",
    ),
    _three_point_example(
        "cp-tabla-cuartas", "Tabla de datos sin función",
        "Datos de x⁴ en x = 0, 1, …, 6: las fórmulas de 5 puntos dan exactamente 4x³.", "all",
        points=[[0, 0], [1, 1], [2, 16], [3, 81], [4, 256], [5, 625], [6, 1296]],
    ),
]


def _integration_example(example_id, name, description, **data):
    """Ejemplo de integración: modo función (function, a, b, n0) o modo tabla
    (points y, opcional, compare_function)."""
    return {
        "id": example_id,
        "name": name,
        "description": description,
        "mode": "table" if "points" in data else "function",
        "function": data.get("function", ""),
        "a": data.get("a"),
        "b": data.get("b"),
        "n0": data.get("n0", 1),
        "points": data.get("points"),
        "compare_function": data.get("compare_function", ""),
        "tolerance": 0.000001,
        "max_iterations": 20,
    }


CHAPRA_POLYNOMIAL = "0.2 + 25x - 200x^2 + 675x^3 - 900x^4 + 400x^5"

# Método del trapecio. Los valores esperados (README y tests/test_trapezoid.py)
# se verificaron con un script independiente.
TRAPEZOID_EXAMPLES = [
    _integration_example(
        "trap-chapra", "Polinomio de Chapra en [0, 0.8]",
        "Exacta 1.640533 (3076/1875). La regla simple da 0.1728 (εₜ = 89.5 %).",
        function=CHAPRA_POLYNOMIAL, a=0, b=0.8,
    ),
    _integration_example(
        "trap-gauss", "e^(−x²) en [0, 1]",
        "Antiderivada con erf: se compara con un valor de referencia, 0.746824.",
        function="exp(-x^2)", a=0, b=1,
    ),
    _integration_example(
        "trap-seno", "sin(x) en [0, π]",
        "Exacta 2. f'' < 0: el trapecio subestima la integral.",
        function="sin(x)", a=0, b=3.141592653589793,
    ),
    _integration_example(
        "trap-cuadrado", "x² en [0, 2]",
        "Exacta 8/3. f'' = 2 es constante: Eₐ = Eₜ y el error es igual a la cota.",
        function="x^2", a=0, b=2,
    ),
    _integration_example(
        "trap-recta", "Recta 2x + 1 en [1, 3]",
        "Exacta 10: el trapecio es exacto para rectas (error y cota 0).",
        function="2x + 1", a=1, b=3,
    ),
    _integration_example(
        "trap-exponencial", "eˣ en [0, 1] con n₀ = 2",
        "Exacta e − 1 ≈ 1.718282, empezando con 2 segmentos.",
        function="exp(x)", a=0, b=1, n0=2,
    ),
    _integration_example(
        "trap-tabla-chapra", "Tabla de Chapra con h = 0.1 (tabla + función)",
        "Nueve datos igualmente espaciados; se compara con el polinomio de Chapra.",
        points=[[0, 0.2], [0.1, 1.289], [0.2, 1.288], [0.3, 1.607], [0.4, 2.456], [0.5, 3.325],
                [0.6, 3.464], [0.7, 2.363], [0.8, 0.232]],
        compare_function=CHAPRA_POLYNOMIAL,
    ),
    _integration_example(
        "trap-tabla-desigual", "Tabla de Chapra con segmentos desiguales",
        "Once datos con espaciado no uniforme: cada trapecio usa su propio ancho.",
        points=[[0, 0.2], [0.12, 1.309729], [0.22, 1.305241], [0.32, 1.743393], [0.36, 2.074903],
                [0.40, 2.456], [0.44, 2.842985], [0.54, 3.507297], [0.64, 3.181929], [0.70, 2.363],
                [0.80, 0.232]],
        compare_function=CHAPRA_POLYNOMIAL,
    ),
]


def _simpson_example(example_id, name, description, rule="both", **data):
    """Ejemplo de Simpson: el de integración con la regla y un n₀ por regla."""
    example = _integration_example(example_id, name, description, **data)
    example.update({"rule": rule, "n0_13": data.get("n0_13", 2), "n0_38": data.get("n0_38", 3)})
    return example


# Método de Simpson. Los valores esperados (README y tests/test_simpson.py) se
# verificaron con un script independiente (fracciones exactas).
SIMPSON_EXAMPLES = [
    _simpson_example(
        "simp-chapra", "Polinomio de Chapra en [0, 0.8]",
        "Exacta 1.640533. 1/3 con n = 2: 1.367467; 3/8 con n = 3: 1.51917. Eₐ = Eₜ en todas las filas.",
        function=CHAPRA_POLYNOMIAL, a=0, b=0.8,
    ),
    _simpson_example(
        "simp-gauss", "e^(−x²) en [0, 1]",
        "Antiderivada con erf: se compara con un valor de referencia, 0.746824.",
        function="exp(-x^2)", a=0, b=1,
    ),
    _simpson_example(
        "simp-seno", "sin(x) en [0, π] con Simpson 1/3",
        "Exacta 2. f⁽⁴⁾ = sin x > 0: Simpson sobreestima la integral.",
        rule="simpson13", function="sin(x)", a=0, b=3.141592653589793,
    ),
    _simpson_example(
        "simp-cubica", "x³ en [0, 2]",
        "Exacta 4: Simpson es exacto para polinomios de grado ≤ 3 (error y cota 0).",
        function="x^3", a=0, b=2,
    ),
    _simpson_example(
        "simp-cuarta", "x⁴ en [0, 2]",
        "Exacta 6.4. f⁽⁴⁾ = 24 es constante: Eₐ = Eₜ y el error es igual a la cota.",
        function="x^4", a=0, b=2,
    ),
    _simpson_example(
        "simp-reciproco", "1/x en [1, 2] con Simpson 3/8",
        "Exacta ln 2 ≈ 0.693147.",
        rule="simpson38", function="1/x", a=1, b=2,
    ),
    _simpson_example(
        "simp-tabla-chapra", "Tabla de Chapra con h = 0.1 (tabla + función)",
        "Nueve datos (n = 8, par): Simpson 1/3 da 1.639467; identidad con el trapecio.",
        points=[[0, 0.2], [0.1, 1.289], [0.2, 1.288], [0.3, 1.607], [0.4, 2.456], [0.5, 3.325],
                [0.6, 3.464], [0.7, 2.363], [0.8, 0.232]],
        compare_function=CHAPRA_POLYNOMIAL,
    ),
    _simpson_example(
        "simp-tabla-impar", "Tabla de Chapra con n = 5 (combinación 1/3 + 3/8)",
        "Seis datos (n impar): 1/3 en [0, 0.32] y 3/8 en [0.32, 0.8]; total 1.645077.",
        points=[[0, 0.2], [0.16, 1.296919], [0.32, 1.743393], [0.48, 3.186015], [0.64, 3.181929],
                [0.8, 0.232]],
        compare_function=CHAPRA_POLYNOMIAL,
    ),
]


EXAMPLES = {
    "jacobi": LINEAR_SYSTEM_EXAMPLES,
    "gauss-seidel": LINEAR_SYSTEM_EXAMPLES,
    "punto-fijo": NONLINEAR_SYSTEM_EXAMPLES,
    "newton": NEWTON_EXAMPLES,
    "bairstow": POLYNOMIAL_EXAMPLES,
    "diferencias-finitas": DIFFERENCE_EXAMPLES,
    "tres-puntos": THREE_POINT_EXAMPLES,
    "cinco-puntos": FIVE_POINT_EXAMPLES,
    "trapecio": TRAPEZOID_EXAMPLES,
    "simpson": SIMPSON_EXAMPLES,
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
