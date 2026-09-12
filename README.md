# Métodos Iterativos — Jacobi y Gauss-Seidel

Aplicación web full-stack para resolver sistemas de ecuaciones lineales
(n×n, n ≥ 3) usando los métodos iterativos de **Jacobi** y **Gauss-Seidel**.

- **Backend:** Django + Django REST Framework (API REST).
- **Frontend:** Vue 3 (Composition API) + Vite, con Axios.

## Estructura del proyecto

```
metodos/
├── backend/                   # Django + DRF
│   ├── core/                  # Configuración del proyecto (settings, urls)
│   ├── numeric_methods/       # App principal
│   │   ├── solvers/           # Lógica pura (sin Django): jacobi.py, gauss_seidel.py, validation.py
│   │   ├── examples_data.py   # 6 sistemas de ejemplo precargados
│   │   ├── serializers.py     # Validación de entrada (A, b, x0, tolerancia, max_iter)
│   │   ├── views.py           # Endpoints de la API
│   │   ├── urls.py
│   │   └── tests/             # Tests unitarios (solvers + API)
│   ├── manage.py
│   └── requirements.txt
└── frontend/                   # Vue 3 + Vite
    └── src/
        ├── api/client.js       # Cliente Axios
        ├── router/index.js
        ├── views/
        │   ├── SolverView.vue  # Formulario + resolución
        │   └── TheoryView.vue  # Explicación matemática de los métodos
        └── components/
            ├── MatrixInput.vue
            └── ResultsTable.vue
```

## Requisitos

- Python 3.11+
- Node.js 18+ (recomendado 20+)

## 1. Backend (Django)

```bash
cd backend

# Crear y activar el entorno virtual
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (Git Bash):
source .venv/Scripts/activate
# Linux / macOS:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones (solo tablas internas de Django: admin, auth, sesiones)
python manage.py migrate

# Ejecutar el servidor de desarrollo
python manage.py runserver 8000
```

La API quedará disponible en `http://127.0.0.1:8000/api/`.

### Endpoints disponibles

| Método | Endpoint                        | Descripción                                   |
|--------|----------------------------------|------------------------------------------------|
| POST   | `/api/solve/jacobi/`             | Resuelve el sistema con el método de Jacobi     |
| POST   | `/api/solve/gauss-seidel/`       | Resuelve el sistema con el método de Gauss-Seidel |
| GET    | `/api/examples/`                 | Devuelve los sistemas de ejemplo precargados    |

**Cuerpo esperado por los endpoints de resolución:**

```json
{
  "A": [[10, -1, 2], [-1, 11, -1], [2, -1, 10]],
  "b": [6, 22, -10],
  "x0": [0, 0, 0],
  "tolerance": 0.000001,
  "max_iterations": 100
}
```

`x0` es opcional (por defecto, vector de ceros). La respuesta incluye la
lista completa de iteraciones (con el valor de cada variable y el error
respecto a la iteración anterior), la solución final, si convergió, cuántas
iteraciones se usaron y advertencias (por ejemplo, si la matriz no es
diagonalmente dominante).

### Correr los tests del backend

```bash
cd backend
python manage.py test numeric_methods
```

## 2. Frontend (Vue 3 + Vite)

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

La aplicación quedará disponible en `http://localhost:5173`.

Por defecto, el frontend consume la API en `http://127.0.0.1:8000/api`
(configurable en `frontend/.env.development`, variable `VITE_API_BASE_URL`).

## Validaciones implementadas

- La matriz `A` debe ser cuadrada (n × n) y el sistema debe tener al menos
  3 variables.
- Ningún elemento de la diagonal principal puede ser cero.
- Se verifica si `A` es diagonalmente dominante (condición suficiente de
  convergencia); si no lo es, la API responde igualmente pero incluye una
  advertencia, y el frontend la muestra al usuario.
- El algoritmo siempre ejecuta un mínimo de 6 iteraciones, incluso si la
  tolerancia se alcanza antes, y se detiene al llegar al máximo de
  iteraciones configurado (por defecto 100) si no converge antes.

## Notas de esta primera etapa

- No hay autenticación ni persistencia de resultados en base de datos; los
  6 ejemplos precargados viven en `backend/numeric_methods/examples_data.py`.
- El objetivo de esta etapa es que los cálculos sean correctos (cubierto por
  tests unitarios) y que la interfaz permita cargar un ejemplo o ingresar un
  sistema manualmente, elegir método, resolver y ver la tabla de iteraciones.


## .venv\Scripts\activate.bat
