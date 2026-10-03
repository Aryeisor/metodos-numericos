# Métodos Numéricos Iterativos

Aplicación web full-stack para resolver, paso a paso, sistemas de ecuaciones
**lineales** y **no lineales** con métodos iterativos, y para estudiar la
teoría de cada método.

| Categoría | Método | Qué resuelve |
| --- | --- | --- |
| Sistemas lineales | **Jacobi** | `A·x = b`, n × n con n ≥ 3 |
| Sistemas lineales | **Gauss-Seidel** | `A·x = b`, n × n con n ≥ 3 |
| Ecuaciones no lineales | **Punto Fijo (Iterativo Secuencial)** | `F(x) = 0`, de 2 a 6 ecuaciones, despejando cada una automáticamente |
| Ecuaciones no lineales | **Newton** | `F(x) = 0`, de 2 a 6 ecuaciones, con la matriz Jacobiana y la regla de Cramer |

- **Backend:** Django + Django REST Framework (API REST) y sympy para el
  manejo simbólico de las ecuaciones.
- **Frontend:** Vue 3 (Composition API) + Vite, con Axios, KaTeX, Chart.js y
  jsPDF.

---

## Contenido

1. [Funcionalidades](#funcionalidades)
2. [Requisitos e instalación](#requisitos-e-instalación)
3. [Cómo escribir las ecuaciones](#cómo-escribir-las-ecuaciones)
4. [Detalle de cada método](#detalle-de-cada-método)
5. [API](#api)
6. [Estructura del proyecto](#estructura-del-proyecto)
7. [Arquitectura: cómo agregar un método](#arquitectura-cómo-agregar-un-método)
8. [Seguridad del parser de expresiones](#seguridad-del-parser-de-expresiones)
9. [Tests](#tests)
10. [Notas y alcance](#notas-y-alcance)

---

## Funcionalidades

### Vista «Resolver» (`/resolver/<método>`)

- **Ejemplos precargados** por método (13 en total), que se cargan en el
  formulario con un clic.
- **Formulario propio de cada categoría:**
  - Sistemas lineales: matriz `A`, vector `b` y vector inicial `x0`; acepta
    decimales, negativos y **fracciones** (`6/7`), y el cálculo usa el valor
    exacto, no el redondeado que se ve.
  - Sistemas no lineales: una fila por ecuación, con controles para agregar o
    quitar ecuaciones, y el punto inicial `x0` (también con fracciones).
- **Barra de símbolos matemáticos** (√, xⁿ, log, ln, exp, sin, cos, tan, π, e,
  |x|, paréntesis y un desplegable «Más funciones» con trigonométricas
  inversas e hiperbólicas). Inserta en la posición del cursor del campo activo
  y deja el cursor entre los paréntesis.
- **Vista previa en vivo** de cada ecuación en LaTeX mientras se escribe, con
  el error específico de la fila si no es válida.
- **Resultado:** solución, estado (convergió o no), advertencias, **gráfico de
  convergencia** del error en escala logarítmica (con la línea de tolerancia y
  notación científica) y **tabla de iteraciones** paginada.
- **Paso a paso expandible** en cada iteración, con todas las fórmulas
  renderizadas con KaTeX (ver [Detalle de cada método](#detalle-de-cada-método)).
- **Exportación a PDF** del resultado: datos del sistema, solución, gráfico y
  tabla completa de iteraciones.

### Vista «Teoría» (`/teoria/<método>`)

Una página por método, con el mismo formato en los cuatro: fundamento común
de la categoría, definición formal en LaTeX, condición de convergencia,
restricciones, algoritmo en tarjetas, ejemplo resuelto paso a paso con datos
reales del solver, tabla comparativa y referencias bibliográficas (APA).

- **Lineales:** dominancia diagonal y radio espectral; Jacobi frente a
  Gauss-Seidel.
- **No lineales:** concepto de punto fijo y contracción; esquema simultáneo
  frente a secuencial; derivación de Newton, regla de Cramer y convergencia
  cuadrática; Punto Fijo frente a Newton.

Los menús «Resolver ▾» y «Teoría ▾» se generan automáticamente a partir del
catálogo de métodos del backend, agrupados por categoría.

---

## Requisitos e instalación

- Python 3.11+
- Node.js 18+ (recomendado 20+)

### 1. Backend (Django)

```bash
cd backend

# Crear el entorno virtual (solo la primera vez)
python -m venv .venv

# Activarlo
.venv\Scripts\activate.bat        # Windows (CMD)
.venv\Scripts\Activate.ps1        # Windows (PowerShell)
source .venv/Scripts/activate     # Windows (Git Bash)
source .venv/bin/activate         # Linux / macOS

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones (solo tablas internas de Django: admin, auth, sesiones)
python manage.py migrate

# Ejecutar el servidor de desarrollo
python manage.py runserver 8000
```

La API queda disponible en `http://127.0.0.1:8000/api/`.

Dependencias (`backend/requirements.txt`): Django 5.2, Django REST Framework
3.18, django-cors-headers 4.9 y sympy 1.14.

### 2. Frontend (Vue 3 + Vite)

En otra terminal:

```bash
cd frontend
npm install
npm run dev        # desarrollo, en http://localhost:5173
npm run build      # compilación de producción en frontend/dist
```

El frontend consume la API en `http://127.0.0.1:8000/api`, configurable en
`frontend/.env.development` con la variable `VITE_API_BASE_URL`.

Dependencias principales: Vue 3.5, Vue Router 4, Axios, KaTeX (fórmulas),
Chart.js (gráfico de convergencia) y jsPDF + jspdf-autotable (PDF).

---

## Cómo escribir las ecuaciones

Las ecuaciones de los métodos no lineales se escriben como texto. Se pueden
escribir igualadas a cero (`3*x - cos(y) - 1 = 0`) o con dos lados
(`y = (sin(x) + 2)/4`). Una expresión sin `=` se interpreta como
`expresión = 0`.

| Operación | Sintaxis |
| --- | --- |
| Producto | `3*x` o `3x` |
| Potencia | `x^2` o `x**2` |
| Raíz cuadrada | `sqrt(x)` |
| Logaritmo en base 10 | `log(x)` (y `log(x, b)` para otra base) |
| Logaritmo natural | `ln(x)` |
| Exponencial | `exp(x)` o `e^x` |
| Valor absoluto | `abs(x)` |
| Trigonométricas | `sin(x)`, `cos(x)`, `tan(x)` |
| Trigonométricas inversas | `asin(x)`, `acos(x)`, `atan(x)` |
| Hiperbólicas | `sinh(x)`, `cosh(x)`, `tanh(x)` |
| Constantes | `pi`, `e` |

Dos números seguidos (`007`, `1.5.2`, `2 3`) se rechazan como error de
escritura, en lugar de interpretarse como una multiplicación.

---

## Detalle de cada método

Reglas comunes a los cuatro métodos: tolerancia por defecto `0.000001`,
máximo de iteraciones por defecto `100`, **mínimo de 6 iteraciones** aunque
la tolerancia se alcance antes, y el error de cada iteración se mide en
norma infinito. Si un valor deja de ser un número real finito, el método se
detiene y se reporta como no convergente, con una advertencia.

### Jacobi y Gauss-Seidel (sistemas lineales)

- La matriz debe ser cuadrada, con al menos 3 variables, y sin ceros en la
  diagonal principal.
- Se verifica la **dominancia diagonal**. Si no se cumple, el método se
  ejecuta igual, con una advertencia.
- **Reordenamiento automático de filas** (opcional, activado por defecto): si
  la matriz no es diagonalmente dominante, se busca un orden de las ecuaciones
  que sí lo sea. El resultado muestra el sistema reordenado y de qué fila
  original viene cada una.
- Paso a paso de cada iteración: fórmula general, sustitución numérica de cada
  variable (valores de la iteración anterior en azul y, en Gauss-Seidel, los ya
  recalculados en verde) y cálculo del error.

### Punto Fijo (Iterativo Secuencial)

- La ecuación `i` se **despeja automáticamente** para la variable `i` (con
  `sympy.solve`). Se rechaza con un mensaje claro si no tiene despeje, si sólo
  tiene despejes complejos, o si tiene varios despejes reales (despeje
  ambiguo). Por rendimiento, no se intenta despejar una variable que aparezca
  con grado mayor que 4.
- La actualización es **secuencial** (análoga a Gauss-Seidel): cada `x_i` usa
  los valores ya recalculados en la misma iteración.
- Se muestra el **despeje paso a paso** de cada ecuación (agrupar términos,
  dividir entre el coeficiente, aplicar raíces). Cada desglose se verifica
  numéricamente contra la función que realmente se itera.
- Paso a paso de cada iteración: sustitución en cada `g_i`, indicando qué
  valores son nuevos y cuáles de la iteración anterior, y cálculo del error.

### Newton

- Las ecuaciones se usan tal como se escriben, **sin despejar**. Las
  variables se declaran aparte y en orden; ese orden fija las columnas de la
  Jacobiana y el de `x0`.
- La **matriz Jacobiana** se calcula simbólicamente una sola vez, y se muestra
  la derivación de cada `∂f_i/∂x_j` término a término, con la regla aplicada
  (potencia, producto, cadena, constante).
- En cada iteración se resuelve `J(x^(k))·Δx = −F(x^(k))` por la **regla de
  Cramer** (`D = det J`, `D_i` con la columna `i` reemplazada por `−F`,
  `Δx_i = D_i / D`) y se actualiza `x^(k+1) = x^(k) + Δx`.
- Si la Jacobiana es singular (`D ≈ 0`), el método se detiene y lo reporta
  como no convergente. Se rechazan de entrada las variables que no aparecen en
  ninguna ecuación (su columna de la Jacobiana sería de ceros).
- Paso a paso de cada iteración, en el orden en que se resuelve a mano:
  evaluación de `F` (sustitución término a término) y de `J` en el punto
  actual, sistema lineal planteado, determinantes (`ad − bc` en 2×2,
  expansión por cofactores en 3×3 o más), incrementos, actualización y error.

---

## API

Todas las rutas cuelgan de `/api/`.

| Método | Endpoint | Descripción |
| --- | --- | --- |
| GET | `/api/methods/` | Catálogo de métodos: `slug`, `name`, `category`, `category_label` |
| GET | `/api/examples/?method=<slug>` | Ejemplos precargados de un método (sin `method`, todos sin repetir) |
| POST | `/api/solve/jacobi/` | Resuelve un sistema lineal con Jacobi |
| POST | `/api/solve/gauss-seidel/` | Resuelve un sistema lineal con Gauss-Seidel |
| POST | `/api/solve/punto-fijo/` | Resuelve un sistema no lineal con Punto Fijo |
| POST | `/api/solve/newton/` | Resuelve un sistema no lineal con Newton |
| POST | `/api/expressions/preview` | Valida una ecuación y devuelve su LaTeX (no resuelve nada) |

### Cuerpo de la petición

Sistemas lineales (Jacobi, Gauss-Seidel):

```json
{
  "A": [[10, -1, 2], [-1, 11, -1], [2, -1, 10]],
  "b": [6, 22, -10],
  "x0": [0, 0, 0],
  "tolerance": 0.000001,
  "max_iterations": 100,
  "auto_reorder": true
}
```

Sistemas no lineales (Punto Fijo, Newton):

```json
{
  "equations": ["x^2 + x*y - 10 = 0", "y + 3*x*y^2 - 57 = 0"],
  "variables": ["x", "y"],
  "x0": [1.5, 3.5],
  "tolerance": 0.000001,
  "max_iterations": 100
}
```

En Punto Fijo, la ecuación `i` se despeja para la variable `i`; en Newton,
`variables` sólo fija el orden. `x0` es opcional en todos los métodos (por
defecto, ceros), igual que `tolerance` y `max_iterations`.

Vista previa de una ecuación:

```json
{ "equation": "3*x - y**2 - 1 = 0", "variables": ["x", "y"] }
```

Responde `{"latex": "3 x - y^{2} - 1 = 0"}`, o un **400** con el mensaje de
error del parser (por ejemplo, `{"equation": ["La expresión no está bien formada."]}`).

### Respuesta de `/api/solve/<slug>/`

Campos comunes a todos los métodos:

| Campo | Contenido |
| --- | --- |
| `method`, `category` | Método y categoría con que se resolvió |
| `converged` | Si alcanzó la tolerancia |
| `iterations` | Lista `[{iteration, x, error, extra?}]`; `extra` lleva los datos del paso a paso del método |
| `iterations_used` | Número de iteraciones ejecutadas |
| `solution`, `variables` | Último punto calculado y nombre de cada variable |
| `warnings` | Advertencias (dominancia, no convergencia, Jacobiana singular, valores no finitos…) |

Campos propios de cada categoría:

- **Lineales:** `A` y `b` tal como se usaron (ya reordenados, si hubo
  reordenamiento), `is_diagonally_dominant`, `reordered`, `row_order`.
- **Punto Fijo:** por ecuación, el despeje `g_i` (en LaTeX y en texto) y su
  paso a paso (`isolation`); `x0`; `failure`.
- **Newton:** la función `f_i` de cada ecuación y sus términos, la Jacobiana
  simbólica con el desglose de cada derivada (`jacobian`), `x0`, `failure`. En
  cada iteración, `extra` incluye `F`, `J`, `D`, `D_i` con sus matrices y
  `Δx`.

Los errores de validación de la entrada responden **400** con listas planas de
mensajes por campo. Un despeje imposible en Punto Fijo responde **400** con el
motivo en `detail`.

---

## Estructura del proyecto

```
metodos/
├── backend/
│   ├── core/                        # Configuración de Django (settings, urls)
│   └── numeric_methods/             # App principal
│       ├── registry.py              # Registro de métodos: slug, nombre, categoría, serializer y solver
│       ├── views.py, urls.py        # Una ruta /api/solve/<slug>/ por método registrado + methods, examples, preview
│       ├── examples_data.py         # Ejemplos precargados por método
│       ├── serializers/             # Validación de entrada: linear.py, nonlinear.py, expressions.py
│       ├── expressions/             # Manejo simbólico de ecuaciones (sympy)
│       │   ├── parser.py            #   Parseo seguro de texto del usuario
│       │   ├── differentiate.py     #   Derivadas parciales, gradiente y Jacobiano
│       │   ├── normalize.py         #   Forma evaluada de una expresión parseada
│       │   ├── to_latex.py          #   Conversión a LaTeX
│       │   └── to_text.py           #   Conversión a texto plano (mensajes y PDF)
│       ├── linalg/cramer.py         # Determinante por cofactores y regla de Cramer (Python puro)
│       ├── solvers/
│       │   ├── base.py              #   SolverResult / IterationStep: formato común de la respuesta
│       │   ├── validation.py        #   Constantes comunes (tolerancia, máx. y mín. de iteraciones)
│       │   ├── linear/              #   Jacobi, Gauss-Seidel, dominancia y reordenamiento
│       │   ├── nonlinear/           #   Punto Fijo (+ despeje paso a paso) y Newton (+ derivadas paso a paso)
│       │   └── polynomial/          #   Reservado para métodos de polinomios
│       └── tests/                   # Tests unitarios y de API
└── frontend/
    └── src/
        ├── main.js                  # Carga el catálogo de métodos antes de montar la app
        ├── api/client.js            # Cliente Axios
        ├── router/index.js          # Rutas /resolver/<slug> y /teoria/<slug>, generadas desde el registro
        ├── views/                   # SolverView (genérica para todos los métodos) y TheoryView
        ├── methods/
        │   ├── registry.js          # Asocia cada categoría (y método) con su interfaz
        │   ├── linear/              # Formulario, detalle de iteración, PDF y teoría de Jacobi / Gauss-Seidel
        │   └── nonlinear/           # Formularios, detalles, PDF y teoría de Punto Fijo y Newton
        ├── components/              # ResultsTable, ConvergenceChart, MathFormula, MatrixInput,
        │   │                        # MathSymbolToolbar, MathSyntaxHelp, NavMenu
        │   └── theory/              # Piezas comunes de las páginas de teoría
        ├── composables/             # useExpressionPreviews (vista previa en vivo)
        └── utils/                   # PDF, formato numérico, fórmulas LaTeX, entrada con fracciones
```

---

## Arquitectura: cómo agregar un método

La aplicación está pensada para crecer por **categorías** de métodos.

**Backend:**

1. Escribir el solver en `solvers/<categoría>/`. Recibe los datos validados y
   devuelve un `SolverResult` (`solvers/base.py`).
2. Escribir o reutilizar el serializer en `serializers/`.
3. Registrar el método en `registry.py` (`slug`, nombre, categoría,
   serializer, solver).
4. Agregar sus ejemplos en `examples_data.py`.

La ruta `/api/solve/<slug>/` y su entrada en `/api/methods/` aparecen solas,
sin tocar `views.py` ni `urls.py`.

**Frontend:**

- Un método de una categoría existente cuyo formulario y paso a paso sean los
  mismos (como Gauss-Seidel respecto a Jacobi) no requiere cambios: aparece
  solo en el menú «Resolver ▾» y en el selector de método.
- Si necesita una interfaz distinta dentro de la misma categoría (como Newton
  respecto a Punto Fijo), se declara en `methods[slug]` dentro de la interfaz
  de la categoría (`methods/<categoría>/index.js`).
- Una categoría nueva sólo requiere registrar su interfaz en
  `methods/registry.js`. El contrato que debe cumplir está documentado en
  `methods/linear/index.js`.
- Para que el método aparezca en «Teoría ▾», basta con agregar su sección a
  `THEORY_SECTIONS` en la página de teoría de su categoría.

No hace falta tocar `App.vue`, el router ni `NavMenu.vue`.

---

## Seguridad del parser de expresiones

El texto que escribe el usuario **nunca se evalúa con `eval()` directamente**.
`expressions/parser.py` aplica tres capas de defensa:

1. **Validación léxica previa:** sólo se aceptan números, operadores
   aritméticos, paréntesis, comas y nombres de una lista blanca (variables
   declaradas, funciones y constantes conocidas).
2. **Entorno restringido** para `sympy.parse_expr`: sin `__builtins__` y sólo
   con los nombres imprescindibles.
3. **Validación del árbol** ya parseado: sólo pueden aparecer variables
   declaradas, números finitos y operaciones o funciones permitidas.

Además se aplican límites contra la denegación de servicio: longitud máxima
(300 caracteres), anidamiento (30 paréntesis), profundidad del árbol (40),
magnitud de los números (10¹⁰⁰), exponentes (1000) y división literal entre
cero. Toda evaluación numérica se hace con floats (`lambdify`), nunca con
sustitución simbólica repetida.

---

## Tests

```bash
cd backend
python manage.py test numeric_methods
```

**232 tests**, todos en verde:

| Archivo | Tests | Qué cubre |
| --- | --- | --- |
| `test_solvers.py` | 15 | Jacobi y Gauss-Seidel |
| `test_dominance.py` | 8 | Dominancia diagonal y reordenamiento de filas |
| `test_api.py` | 13 | Endpoints de los métodos lineales y de ejemplos |
| `test_registry.py` | 13 | Registro de métodos, catálogo y ejemplos por método |
| `test_expressions.py` | 49 | Parser seguro, derivación y LaTeX |
| `test_preview.py` | 31 | Endpoint de vista previa, logaritmos y límites de seguridad |
| `test_fixed_point.py` | 36 | Punto Fijo: despeje automático, rechazos, actualización secuencial, endpoint |
| `test_isolation_steps.py` | 20 | Despeje paso a paso de Punto Fijo |
| `test_newton.py` | 31 | Newton y regla de Cramer: iteraciones calculadas a mano, Jacobiana singular, endpoint |
| `test_newton_steps.py` | 16 | Derivadas parciales paso a paso y sustitución en F |

---

## Notas y alcance

- No hay autenticación ni persistencia: los resultados no se guardan y los
  ejemplos viven en `backend/numeric_methods/examples_data.py`.
- La categoría «Polinomios» está reservada en el registro (prevista para
  Bairstow) y todavía no tiene métodos implementados.
- Los métodos para sistemas no lineales admiten de 2 a 6 ecuaciones; los
  lineales, de 3 a 12 variables en el formulario.
