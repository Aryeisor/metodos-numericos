# Métodos Numéricos Iterativos

Aplicación web full-stack para resolver, paso a paso, sistemas de ecuaciones
**lineales** y **no lineales**, las **raíces de polinomios** con métodos
iterativos, la **derivada numérica** con fórmulas de diferencias finitas y la
**integral numérica** con reglas de integración (método del trapecio), y para
estudiar la teoría de cada método.

| Categoría | Método | Qué resuelve |
| --- | --- | --- |
| Sistemas lineales | **Jacobi** | `A·x = b`, n × n con n ≥ 3 |
| Sistemas lineales | **Gauss-Seidel** | `A·x = b`, n × n con n ≥ 3 |
| Ecuaciones no lineales | **Punto Fijo (Iterativo Secuencial)** | `F(x) = 0`, de 2 a 6 ecuaciones, despejando cada una automáticamente |
| Ecuaciones no lineales | **Newton** | `F(x) = 0`, de 2 a 6 ecuaciones, con la matriz Jacobiana y la regla de Cramer |
| Polinomios | **Bairstow** | Todas las raíces (reales y complejas) de un polinomio de grado 3 a 10, extrayendo factores cuadráticos `x² − r·x − s` |
| Diferenciación numérica | **Diferencias progresiva y regresiva** | `f'(x₀)` a partir de `f(x)` (con refinamiento de h) o de una tabla de datos `(xᵢ, yᵢ)` |
| Diferenciación numérica | **Fórmula de 3 puntos** | `f'(x₀)` con el punto medio y los extremos hacia adelante y hacia atrás, de orden `O(h²)`; desde `f(x)` o desde una tabla igualmente espaciada |
| Diferenciación numérica | **Fórmula de 5 puntos** | `f'(x₀)` con el punto medio y los extremos de 5 puntos, de orden `O(h⁴)`; desde `f(x)` o desde una tabla igualmente espaciada (de 5 a 20 puntos) |
| Integración numérica | **Método del trapecio** | `∫ₐᵇ f(x) dx` con la regla simple y la compuesta, refinando `n` (con la recurrencia que aprovecha los puntos ya evaluados), o desde una tabla de datos con espaciado no uniforme (de 2 a 30 puntos) |

- **Backend:** Django + Django REST Framework (API REST) y sympy para el
  manejo simbólico de las ecuaciones.
- **Frontend:** Vue 3 (Composition API) + Vite, con Axios, KaTeX, Chart.js y
  jsPDF.

---

## Contenido

1. [Funcionalidades](#funcionalidades)
2. [Requisitos e instalación](#requisitos-e-instalación)
3. [Ejecutar con Docker](#ejecutar-con-docker)
4. [Cómo escribir las ecuaciones](#cómo-escribir-las-ecuaciones)
5. [Detalle de cada método](#detalle-de-cada-método)
6. [API](#api)
7. [Estructura del proyecto](#estructura-del-proyecto)
8. [Arquitectura: cómo agregar un método](#arquitectura-cómo-agregar-un-método)
9. [Seguridad del parser de expresiones](#seguridad-del-parser-de-expresiones)
10. [Tests](#tests)
11. [Notas y alcance](#notas-y-alcance)

---

## Funcionalidades

### Vista «Resolver» (`/resolver/<método>`)

- **Ejemplos precargados** por método (54 en total: 6 lineales compartidos por
  Jacobi y Gauss-Seidel, 4 de Punto Fijo, 3 de Newton, 9 de Bairstow, 8 de
  diferencias finitas, 8 de la fórmula de 3 puntos, 8 de la de 5 puntos y 8
  del método del trapecio),
  que se cargan en el
  formulario con un clic.
- **Botón «Limpiar»** al lado de «Resolver», en los nueve métodos: deja la
  vista como al abrir el método (formulario con su tamaño y valores
  iniciales, tolerancia, máximo de iteraciones y opciones por defecto del
  método) y borra el resultado, los errores, las advertencias, las vistas
  previas y la marca de ejemplo cargado, sin cambiar de método. Si hay datos
  escritos o un resultado en pantalla, pide confirmación; si el formulario ya
  está en su estado inicial, está deshabilitado. Una petición de resolver en
  curso se descarta.
- **Formulario propio de cada categoría:**
  - Sistemas lineales: matriz `A`, vector `b` y vector inicial `x0`; acepta
    decimales, negativos y **fracciones** (`6/7`), y el cálculo usa el valor
    exacto, no el redondeado que se ve.
  - Sistemas no lineales: una fila por ecuación, con controles para agregar o
    quitar ecuaciones, y el punto inicial `x0` (también con fracciones).
  - Polinomios: dos modos de entrada, **escribir el polinomio** en x (con
    barra de símbolos reducida y vista previa) o **coeficientes** (selector
    de grado y una casilla por potencia), y los valores iniciales `r₀`, `s₀`.
  - Diferenciación numérica: dos modos, **Función** (`f(x)` con la barra de
    símbolos y la vista previa de los no lineales, `x₀` y el paso inicial
    `h₀`) y **Tabla de datos** (de 2 a 20 puntos `(xᵢ, yᵢ)` con filas para
    agregar y quitar, y una función opcional para comparar). En ambos, el
    selector **Fórmula** (progresiva, regresiva o ambas). En modo tabla se
    ocultan la tolerancia y el máximo de refinamientos.
  - Fórmula de 3 puntos: el mismo formulario, con el selector **Fórmula**
    (punto medio, extremo hacia adelante, extremo hacia atrás o **todas**, por
    defecto), tolerancia del error estimado `0.000001` por defecto y de 3 a
    20 puntos igualmente espaciados en modo tabla.
  - Fórmula de 5 puntos: el mismo formulario, con el selector **Fórmula**
    (punto medio, extremo hacia adelante, extremo hacia atrás o **todas**),
    tolerancia `0.000001` por defecto y de 5 a 20 puntos igualmente
    espaciados en modo tabla (9 filas vacías al empezar o al limpiar).
  - Integración numérica: el mismo formulario de dos modos (compartido en
    `components/FunctionTableInput.vue`). **Función**: `f(x)` con la barra de
    símbolos y la vista previa, los límites `a` y `b` (números o fracciones,
    con `a < b`) y, en la configuración, los **segmentos iniciales `n₀`** (de
    1 a 1000, por defecto 1), la tolerancia del error estimado (`0.000001`) y
    el máximo de refinamientos (20, de 6 a 22). **Tabla de datos**: de 2 a 30
    puntos `(xᵢ, yᵢ)` con `x` estrictamente creciente y **espaciado libre**
    (9 filas vacías al empezar o al limpiar) y una función opcional para
    comparar; se ocultan `n₀`, la tolerancia y el máximo.
- **Barra de símbolos matemáticos** (√, xⁿ, log, ln, exp, sin, cos, tan, π, e,
  |x|, paréntesis y un desplegable «Más funciones» con trigonométricas
  inversas e hiperbólicas). Inserta en la posición del cursor del campo activo
  y deja el cursor entre los paréntesis.
- **Vista previa en vivo** de cada ecuación en LaTeX mientras se escribe, con
  el error específico de la fila si no es válida.
- **Resultado:** solución, estado (convergió o no), advertencias, **gráfico de
  convergencia** del error en escala logarítmica (con la línea de tolerancia y
  notación científica) y **tabla de iteraciones** paginada.
- En **Jacobi, Gauss-Seidel, Punto Fijo y Newton**, al final del resultado, el
  apartado **«Comprobación»**: la solución sustituida en cada ecuación del
  sistema original, con su residuo.
- **Errores y residuos** (tablas, paso a paso, comprobaciones y PDF) se
  muestran con **6 decimales como máximo**, igual que los valores de las
  variables: los menores que 0.0000005 se muestran como `0`, coherentes con
  los valores que se ven. Sólo los números muy grandes (desde 10⁷, por ejemplo
  al diverger) se escriben en notación científica.
- **Paso a paso expandible** en cada iteración, con todas las fórmulas
  renderizadas con KaTeX (ver [Detalle de cada método](#detalle-de-cada-método)).
- **Exportación a PDF** del resultado: datos del sistema, solución, gráfico y
  tabla completa de iteraciones.
- En **Bairstow**, el resultado se organiza por **factor**: un bloque
  plegable por cada factor cuadrático, con su tabla de iteraciones, su gráfico
  de ε_r y ε_s y su cierre (discriminante, raíces y deflación); después, el
  resumen de raíces con la comprobación `|f(x)|`, la factorización completa y
  el apartado **«Comprobación»** (cada raíz sustituida en el polinomio).
- En **diferencias finitas**, el resultado tiene su propia vista: resumen,
  derivada exacta con su desglose, una tabla de refinamiento por fórmula (o
  la tabla de puntos), gráfico y «Comprobación» (ver el
  [detalle](#diferencias-progresiva-y-regresiva)). La **fórmula de 3 puntos**
  usa la misma vista, con tres tablas apiladas, un gráfico de hasta 6 series,
  la comparación con las diferencias y las identidades de la comprobación
  (ver su [detalle](#fórmula-de-3-puntos)). La **fórmula de 5 puntos** usa
  la misma vista, con la comparación con la de 3 puntos y las diferencias, la
  identidad de Richardson y, en modo tabla, el punto medio de 3 puntos como
  referencia (ver su [detalle](#fórmula-de-5-puntos)).
- En el **método del trapecio**, el resultado tiene su propia vista: resumen
  (`T`, la integral exacta o de referencia con su rótulo, `Eₜ` y `εₜ`),
  datos del problema (`∫ₐᵇ f(x) dx`, `f'` y `f''`), el **gráfico de los
  trapecios** (la curva y los trapecios sombreados de la fila elegida, con un
  color distinto bajo el eje; selector de fila para `n ≤ 64`), la tabla de
  refinamiento (o la de segmentos) con paso a paso, el gráfico de
  convergencia y la «Comprobación» (ver su [detalle](#método-del-trapecio)).
  El gráfico de trapecios (`components/TrapezoidChart.vue`) es genérico: lo
  reutilizarán Simpson y las demás reglas.

### Vista «Teoría» (`/teoria/<método>`)

Una página por método, con el mismo formato en las ocho (Jacobi,
Gauss-Seidel, Punto Fijo, Newton, Bairstow, diferencias progresiva y
regresiva y fórmulas de 3 y 5 puntos): fundamento común
de la categoría, definición formal en LaTeX, condición de convergencia,
restricciones, algoritmo en tarjetas, ejemplo resuelto paso a paso con datos
reales del solver, tabla comparativa y referencias bibliográficas (APA).

- **Lineales:** dominancia diagonal y radio espectral; Jacobi frente a
  Gauss-Seidel.
- **No lineales:** concepto de punto fijo y contracción; esquema simultáneo
  frente a secuencial; derivación de Newton, regla de Cramer y convergencia
  cuadrática; Punto Fijo frente a Newton.
- **Polinomios:** teorema fundamental del álgebra, pares conjugados como
  factores cuadráticos reales y deflación; división entre `x² − r·x − s`,
  derivación de la recurrencia de los `b` y su equivalencia con la división
  sintética de cuatro filas; demostración de que las derivadas parciales son
  los coeficientes `c` (por eso no se calcula `c₀`) y de que la matriz del
  sistema es la Jacobiana de Newton; el ejemplo de Chapra y Canale resuelto
  con datos reales del solver; Bairstow frente a Newton-Raphson y frente a
  Newton para sistemas.
- **Diferenciación numérica:** la derivada como límite con `h` finito, serie
  de Taylor con residuo, truncamiento frente a redondeo y orden `O(hⁿ)`
  (fundamento común, pensado también para las fórmulas de 3 y 5 puntos);
  figura de la tangente y las secantes de `ln x` con un deslizador de `h`;
  derivación desde Taylor, signos opuestos del error y el promedio que lleva
  a la fórmula de 3 puntos; tabla de razones ≈ 0.5 y la «V» del error total
  (tabla y gráfico log-log); el ejemplo de Burden y Faires y el del carro con
  datos reales del solver, dibujados con los mismos componentes del paso a
  paso de Resolver; progresiva frente a regresiva y a la derivada analítica.
  La **fórmula de 3 puntos** comparte ese fundamento y agrega: definición
  formal con el término exacto del error; figura de la parábola por los 3
  puntos con selector de fórmula y deslizador de `h`; derivación con el
  polinomio de **Lagrange** y con **Taylor** (desarrollo del error de cada
  fórmula, exactitud para polinomios de grado ≤ 2); conexión con las
  diferencias por **extrapolación de Richardson** (punto medio = promedio,
  extremo = `2·D(h) − D(2h)`); tabla de razones ≈ 0.25, **comparación con
  las diferencias** (error, eficiencia y la «V» del redondeo de las dos
  fórmulas); el ejemplo de `x·eˣ` de Burden y Faires y su tabla de datos con
  datos reales del solver; tabla comparativa de diferencias y 3 puntos.
  La **fórmula de 5 puntos** cierra la categoría: definición formal con el
  error exacto; figura del polinomio de grado 4 con selector de fórmula y, de
  referencia, la parábola de 3 puntos y la secante; derivación del punto medio
  por **extrapolación de Richardson** (`(4D₃(h) − D₃(2h))/3`) y del extremo
  por **coeficientes indeterminados**; desarrollo del error y exactitud para
  grado ≤ 4; la **escalera de Richardson** hasta `O(h⁶)` como puente hacia
  Romberg; tabla de razones ≈ 0.0625, eficiencia y la «V» del redondeo de las
  tres fórmulas; el ejemplo de `x·eˣ` y su tabla de 9 datos con datos reales
  del solver; y la **comparación de toda la categoría** con el puente hacia la
  integración numérica.

Los menús «Resolver ▾» y «Teoría ▾» se generan automáticamente a partir del
catálogo de métodos del backend, agrupados por categoría.

### Modo claro y modo oscuro

- **Botón de tema** en la barra superior, a la derecha de «Teoría ▾» (luna
  para pasar a oscuro, sol para pasar a claro).
- La primera vez sigue la **preferencia del sistema operativo**; al pulsar el
  botón, la elección se **recuerda** en el navegador para las visitas
  siguientes. Sin elección guardada, la app sigue los cambios del sistema.
- El tema se aplica antes de pintar la página (sin destello blanco) y los
  gráficos de convergencia se actualizan al cambiarlo, sin volver a resolver.
- El **PDF siempre sale en tema claro**, gráfico incluido.

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

## Ejecutar con Docker

Alternativa al modo desarrollo pensada para exposiciones: toda la aplicación
arranca con **un solo comando** y queda en **http://localhost:8080**, sin
abrir terminales para el backend y el frontend. Es una configuración tipo
producción: el frontend compilado servido por **nginx**, el backend con
**gunicorn** y un solo puerto (sin recarga en caliente).

```
Navegador → http://localhost:8080 → nginx (contenedor frontend)
                                      ├── /        → Vue compilado (dist)
                                      └── /api/... → gunicorn + Django (contenedor backend)
```

El navegador solo habla con nginx (mismo origen, sin CORS) y el backend no
publica su puerto al equipo.

> **El modo desarrollo sigue exactamente igual que antes**
> (`python manage.py runserver` + `npm run dev`). Docker es opcional y no
> cambia nada de ese flujo.

### Requisito

[Docker Desktop](https://www.docker.com/products/docker-desktop/) (en Windows,
con WSL 2). Debe estar abierto antes de usar los comandos.

### Primera vez

```bash
docker compose up -d --build
```

Descarga las imágenes base, instala dependencias y compila el frontend:
**tarda varios minutos**. Las siguientes veces es casi inmediato.

### Uso diario

```bash
docker compose up -d      # iniciar  → http://localhost:8080
docker compose down       # detener
```

O con **doble clic** en los scripts de la raíz:

| Script | Qué hace |
|---|---|
| `iniciar.bat` | Inicia, espera a que el backend esté listo y abre el navegador |
| `detener.bat` | Detiene la aplicación |
| `reconstruir.bat` | Reconstruye con el código actual e inicia |

Los contenedores tienen `restart: unless-stopped`: si no se detuvieron con
`down`, **vuelven a levantarse solos** al abrir Docker Desktop.

### Después de cambiar código

```bash
docker compose up -d --build     # o doble clic en reconstruir.bat
```

### Ver logs

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

### Sin internet

Una vez construidas las imágenes, la aplicación funciona **sin internet**
(solo la construcción descarga paquetes).

### Desde otro dispositivo de la misma red Wi-Fi

Abrir `http://<IP-del-equipo>:8080` (la IP se ve con `ipconfig`, en
«Dirección IPv4»). La primera vez, el firewall de Windows puede pedir permiso
para Docker: hay que permitirlo en redes privadas.

### Configuración

`docker-compose.yml` ya trae valores por defecto (`DJANGO_DEBUG=0`,
`DJANGO_ALLOWED_HOSTS=*`). Para cambiarlos, copiar `.env.example` como `.env`
en la raíz y editarlo; `.env` no se sube al repositorio.

### Problemas comunes

- **El puerto 8080 está ocupado:** en `docker-compose.yml`, cambiar
  `"8080:80"` por otro puerto libre, por ejemplo `"8090:80"`, y abrir
  `http://localhost:8090`.
- **Docker Desktop no está iniciado:** aparece un error como
  `error during connect` o `cannot find the file specified`
  (`iniciar.bat` lo avisa con un mensaje). Abrir Docker Desktop, esperar a que
  diga «Engine running» y repetir.
- **Un script falla por saltos de línea CRLF:** los `.sh` deben tener saltos
  de línea LF para ejecutarse dentro de Linux (`.gitattributes` lo fuerza con
  `*.sh text eol=lf`; este proyecto no usa ninguno, el arranque está en el
  `CMD` del `Dockerfile`). Si un `.bat` se ve mal o no ejecuta, debe tener
  CRLF (`*.bat text eol=crlf`). Si se editó a mano, volver a guardarlo con el
  salto de línea correcto (en VS Code, abajo a la derecha: «LF» / «CRLF»).

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

En Bairstow, el polinomio se escribe con la misma sintaxis, sólo en la
variable `x` y sin funciones (`x^3 - 6x^2 + 11x - 6`, `(x - 1)(x + 2)(x - 3)`,
`x^3 = 2x - 1`); se expande y se pasa a coeficientes antes de resolver.

---

## Detalle de cada método

Reglas comunes a los métodos de sistemas: tolerancia por defecto `0.000001`,
máximo de iteraciones por defecto `100`, **mínimo de 6 iteraciones** aunque
la tolerancia se alcance antes, y el error de cada iteración se mide en
norma infinito. Si un valor deja de ser un número real finito, el método se
detiene y se reporta como no convergente, con una advertencia. Bairstow y las
diferencias finitas tienen reglas propias de tolerancia y error (ver sus
secciones).

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
- **Comprobación** (al final del resultado y en el PDF): la solución se
  reemplaza en cada ecuación del sistema **tal como se escribió** (orden
  original de las filas, aunque el método haya trabajado con las filas
  reordenadas), término a término —por ejemplo
  `4(−3) + 2(−2) = −12 − 4 = −16 (b₁ = −16) ✔`—. Se omiten los términos con
  coeficiente 0. Por cada ecuación se calcula el residuo
  `rᵢ = Σ aᵢⱼ·xⱼ − bᵢ` con los valores sin redondear; se marca ✔ («≈ bᵢ», con
  el residuo en letra pequeña si con 6 decimales no se ve 0) si `|rᵢ| ≤ 10⁻⁶ · max(1, |bᵢ|, Σ|aᵢⱼ·xⱼ|)`
  (el mismo criterio relativo que la comprobación de Bairstow) y ⚠ si no.
  Si la solución se ve entera con 6 decimales (por ejemplo, 0.9999997 → 1), se
  comprueba con esos enteros, sin aproximaciones: `4(1) + (1) + (1) = 4 + 1 + 1 = 6`.
  Cuando la solución tiene decimales, las igualdades se escriben «≈». Al final
  se muestra el residuo máximo (norma infinito). Si el método no convergió, la
  comprobación usa la última aproximación, con un aviso.

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
- **Comprobación** (al final del resultado y en el PDF): la solución se
  reemplaza en cada **ecuación original** —no en `g_i`—, escrita como
  `f_i = 0` (una ecuación «lado = lado» pasa todo a la izquierda, como en
  Newton y con los mismos términos), término a término:
  `20(1) + (2)² − 24 = 20 + 4 − 24 = 0 ✔`. Las funciones se muestran con su
  argumento sustituido y luego su valor (`sin(0.552354)` → `0.524693`).
  Cada variable que se ve entera con 6 decimales (|xᵢ − redondeo(xᵢ)| < 5·10⁻⁷,
  el mismo criterio que Jacobi y Gauss-Seidel) se escribe y se sustituye como
  entero, así la línea da `= 0` sin aproximaciones; el residuo con los valores
  sin redondear se indica en letra pequeña sólo si con 6 decimales no se ve 0. Con valores decimales las
  igualdades se escriben «≈» y se marca ✔ («≈ 0», con el residuo si se ve con 6 decimales) si
  `|rᵢ| ≤ 10⁻⁶ · max(1, Σ|términos|)` y ⚠ si no. Si hay funciones
  trigonométricas se recuerda que se evalúan en radianes. Al final, el residuo
  máximo; si el método no convergió, la comprobación usa la última
  aproximación, con un aviso.

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
- **Comprobación** (al final del resultado y en el PDF): la misma de Punto
  Fijo (mismo código, `solvers/nonlinear/verification.py`). La solución se
  reemplaza en cada `f_i = 0`, término a término, con las variables que se ven
  enteras sustituidas como enteros:
  `(1)² − (1)(2) − 3(2) + 7 = 1 − 2 − 6 + 7 = 0 ✔`. Con decimales, «≈ 0 ✔» o
  ⚠ con el mismo criterio; nota de radianes, residuo máximo y, si no convergió
  (iteraciones agotadas o Jacobiana singular), la última aproximación con un aviso.

### Bairstow (raíces de polinomios)

- Polinomio de **grado 3 a 10** con coeficientes reales, escrito como texto o
  dado por coeficientes (de mayor a menor potencia, sin ceros a la izquierda).
  Grados 1 y 2 se rechazan con un mensaje que indica cómo resolverlos.
- Busca factores cuadráticos **`x² − r·x − s`**. Valores iniciales `r₀ = s₀ =
  −1` por defecto; cada factor arranca con los mismos `r₀`, `s₀`.
- En cada iteración: división sintética para los `b`
  (`b_i = a_i + r·b_{i+1} + s·b_{i+2}`), segunda división para los `c` (sobre
  los `b`; `c₀` no se calcula), sistema 2×2 `c₂Δr + c₃Δs = −b₁`,
  `c₁Δr + c₂Δs = −b₀` resuelto por la **regla de Cramer** (`linalg/cramer.py`), actualización y errores
  relativos `ε_r = |Δr / r_nuevo|·100` y `ε_s = |Δs / s_nuevo|·100`.
- La **tolerancia `εs` está en porcentaje** (por defecto `0.0001 %`). Un
  factor converge cuando `ε_r ≤ εs` y `ε_s ≤ εs`, con un **mínimo de 6
  iteraciones**; el máximo de iteraciones es **por factor**. Si `r` o `s`
  tienden a 0 (`|valor| < 10⁻¹²`), se usa el error absoluto, con una
  advertencia.
- **Cierre de cada factor:** discriminante `Δ = r² + 4s` (raíces reales,
  doble o complejas conjugadas) y **deflación**: se recalculan los `b` con
  los `r` y `s` finales y el cociente pasa al siguiente factor. Cuando queda
  grado 2 o 1, se cierra directamente (fórmula cuadrática o despeje).
- **Paso previo:** si el término independiente es 0, se extraen primero las
  raíces `x = 0` (factor `x^k`).
- Si un factor falla (sistema singular `D ≈ 0`, valores no finitos o máximo de
  iteraciones), el método se detiene, lo reporta como no convergente y
  muestra las raíces encontradas hasta ese momento.
- Cada raíz se comprueba evaluando `|f(raíz)|` (Horner con aritmética
  compleja).
- **Apartado «Comprobación»** (al final del resultado y en el PDF): cada raíz
  se reemplaza en el polinomio original.
  - Raíces reales, término a término:
    `f(−2) = (−2)³ − 2(−2)² − 5(−2) + 6 = −8 − 8 + 10 + 6 = 0 ✔`. Los
    términos de coeficiente 0 se omiten y la raíz nula queda `f(0) = a₀ = 0`.
  - Pares complejos: una tabla con `xᵏ = (a + bi)ᵏ` y `aₖ·xᵏ` de la raíz con
    parte imaginaria positiva, y la suma; la conjugada da el valor conjugado
    porque los coeficientes son reales.
  - Criterio de «≈ 0»: `|f(x)| ≤ 10⁻⁶ · max(1, Σ|aₖ·xᵏ|)` (la suma de las
    magnitudes de los términos es la escala del redondeo). Se muestra
    «≈ 0 ✔», con el valor en letra pequeña sólo si con 6 decimales no se ve 0; si es mayor, el residuo con
    ⚠ y una nota (pasa con tolerancias grandes, por ejemplo `εs = 10 %` en el
    ejemplo de Chapra).
  - Los valores (`xᵏ`, `aₖ·xᵏ`, `f(x)` y el criterio) los calcula el backend
    en `roots[i].verification`; el frontend sólo les da formato.
- Paso a paso de cada iteración (8 pasos): valores actuales, tabla de los
  `b`, tabla de los `c`, sistema 2×2, regla de Cramer con los determinantes
  desglosados, incrementos, actualización y errores relativos.

### Diferencias progresiva y regresiva

- Fórmulas, para un paso `h > 0`:
  - progresiva `D⁺(h) = [f(x₀ + h) − f(x₀)] / h`;
  - regresiva `D⁻(h) = [f(x₀) − f(x₀ − h)] / h`.

  Las dos son de orden `O(h)`: `|error| ≤ (h/2)·máx |f''(ξ)|`, con ξ en
  `[x₀, x₀ + h]` (progresiva) o `[x₀ − h, x₀]` (regresiva).
- Cada fórmula es un **dato** de `solvers/differentiation/formulas.py`
  (nodos, pesos, orden y cota). El solver, la vista, el paso a paso y el PDF
  no conocen ninguna fórmula en particular: la de 3 y la de 5 puntos se
  agregan como entradas nuevas de ese archivo.
- **Modo función:** tabla de refinamiento con `h_k = h₀ / 2^(k−1)`. En cada
  fila y para cada fórmula: `D_k`, el **error estimado** `|D_k − D_(k−1)|`
  (desde la fila 2), el **error real** `|D_k − f'(x₀)|`, la **cota**
  `(h_k/2)·M_k` y la **razón** entre errores reales consecutivos, que tiende a
  0.5 (orden `O(h)`). `M_k = máx |f''(x)|` en el intervalo de la fila se
  **estima por muestreo** (401 puntos equiespaciados, extremos incluidos); el
  paso a paso dice en qué x se alcanzó.
  - Parada: error estimado `≤ tolerancia` (por defecto `0.0001`) con **al
    menos 6 filas**; con «Ambas», las dos fórmulas en la misma fila. Máximo de
    refinamientos: 25 por defecto, de 6 a 30.
  - Columna «≤ cota»: `error real ≤ cota + R_k`, con
    `R_k = 4ε·máx(|f(a)|, |f(b)|)/h_k` (ε = 2.220446049250313e−16). Si una fila
    sólo cumple gracias a `R_k`, lleva ✔ con la marca `R`.
  - Advertencias: `f` no definida en x₀ o en los puntos de la fila 1 (400 que
    nombra el punto: «f(x) no está definida en x = −0.05 (punto x₀ − h)»),
    `f''` no definida en todo un intervalo (la cota queda «no disponible»),
    `h` demasiado pequeño para la precisión de la máquina, error de redondeo
    comparable con el de truncamiento en la última fila (`R_k` mayor que la
    cota; no se avisa si la cota es 0, porque entonces la fórmula es exacta),
    `f` no derivable en x₀ (`f'(x₀)` no finita o `abs(u)` con `u(x₀) = 0`) y
    no convergencia.
- **Modo tabla:** en cada `xᵢ`, la progresiva con `h = x_(i+1) − xᵢ` y la
  regresiva con `h = xᵢ − x_(i−1)` (cada una con su propio h si el espaciado
  no es uniforme, con una advertencia). Con función para comparar: derivada
  exacta, error real y cota en cada punto. No hay tolerancia ni
  refinamiento (`converged = true`).
- **Derivada exacta:** `f'(x)` y `f''(x)` se calculan simbólicamente una sola
  vez y las dos se muestran con el desglose término a término de las
  parciales de Newton (con notación `d/dx`): `f'` derivando `f`, y `f''`
  derivando `f'` (en la fórmula de 3 puntos, también `f'''` derivando `f''`).
- **Comprobación** (calculada en el backend): en modo función, `x₀`
  sustituido en `f'(x)` término a término (`f'(2) = 3(2)² − 4(2) + 1 = 12 − 8
  + 1 = 5`), la comparación de la última fila (aproximación, exacta, error y
  cota con ✔/⚠) y la línea «En todas las filas el error real quedó por debajo
  de la cota teórica ✔» (o las filas con ⚠). En modo tabla, siempre la
  **secante común** (`D⁺(xᵢ) = D⁻(x_(i+1))`) y, con función, los datos contra
  la función (`|yᵢ − f(xᵢ)| ≤ 10⁻⁶·máx(1, |f(xᵢ)|)`), la sustitución en `f'` y
  error ≤ cota en cada punto.
- **Dos excepciones a la regla de 6 decimales**, propias de este método:
  1. **El paso `h` y los puntos `x₀ ± h`** definen el cálculo y se muestran
     **exactos**: su decimal exacto es `Decimal(str(h₀)) / 2^(k−1)`. Con 12
     decimales o menos se escribe tal cual (`0.0015625`); con más, como
     `h₀/2^(k−1)` (`0.1/2^{14}` en LaTeX, `0.1/2^14` en el PDF) y, en el paso a
     paso, «≈» con 6 decimales.
  2. **En el paso a paso**, las evaluaciones `f(·)` y la resta del numerador
     llevan `d = mín(15, 6 + ⌈−log₁₀ h⌉)` decimales si `h < 1` (6 si `h ≥ 1`),
     para que el cociente visible sea coherente con los valores que se ven
     (con `h = 0.001`, una resta a 6 decimales perdería casi todas las cifras).
     Si aun así el cociente de los valores mostrados no coincide con `D` a 6
     decimales, se agregan decimales (hasta 15) hasta que coincida. Las
     tablas, el resumen y el cociente `D` siguen con 6 decimales.

### Fórmula de 3 puntos

- Fórmulas, para un paso `h > 0` (todas de orden `O(h²)`):
  - punto medio `[f(x₀ + h) − f(x₀ − h)] / (2h)`, con
    `|error| ≤ (h²/6)·máx |f'''(ξ)|`, ξ en `[x₀ − h, x₀ + h]`;
  - extremo hacia adelante `[−3f(x₀) + 4f(x₀ + h) − f(x₀ + 2h)] / (2h)`, con
    `|error| ≤ (h²/3)·máx |f'''(ξ)|`, ξ en `[x₀, x₀ + 2h]`;
  - extremo hacia atrás `[3f(x₀) − 4f(x₀ − h) + f(x₀ − 2h)] / (2h)`, con la
    misma cota en `[x₀ − 2h, x₀]`.
- Usa el **mismo motor** que las diferencias (refinamiento de `h`, mínimo de
  6 filas, parada con todas las fórmulas pedidas en la misma fila, h exacto,
  decimales del paso a paso, muestreo de 401 puntos, advertencias). Cambia:
  la cota usa `f'''` (se calculan `f'`, `f''` y `f'''` una sola vez), la
  **razón** entre errores reales se acerca a **0.25** (dividir `h` entre 2
  divide el error entre 4), la tolerancia por defecto es `0.000001` y el
  paso a paso muestra cada producto `cᵢ·f(xᵢ)` antes de la suma:
  `(−3(14.778112) + 4(17.148957) − 19.85503) / 0.2 = (−44.334336 + 68.595828
  − 19.85503) / 0.2 = 4.406462 / 0.2 = 22.03231`.
- **Redondeo** `R_k`: en modo tabla, `2ε·Σ|cᵢ·f(xᵢ)| / (factor·h_k)`; en modo
  función se suma el error de representar cada punto `xᵢ = x₀ + dᵢh` en
  binario: `2ε·Σ|cᵢ|·(|f(xᵢ)| + |xᵢ·f'(xᵢ)|) / (factor·h_k)`. Sin ese término,
  en la cúbica (error real = cota, porque `f''' = 6` es constante) el error
  real superaba `cota + R_k` en ~10⁻¹³ en algunas filas.
- **Comparación con diferencias** (calculada en el backend, debajo del
  resumen): qué darían la progresiva y la regresiva con el `h₀` de la fila 1
  y con el `h` de la última fila, con su error real, y cuántas veces menor es
  el error de cada fórmula de 3 puntos. Con `x·eˣ`, `x₀ = 2`, `h₀ = 0.1`: la
  progresiva daría 23.708446 (error 1.541278), la regresiva 20.749128 (error
  1.418041) y el punto medio 22.228787 (error 0.061619, 25 veces menor).
- **Modo tabla:** de 3 a 20 puntos con **espaciado uniforme** obligatorio
  (`|hᵢ − h₁| ≤ 10⁻⁹·máx(1, |h₁|)`; si no, 400: «La fórmula de 3 puntos
  necesita datos igualmente espaciados: entre la fila 3 y la 4 el espaciado
  es 0.5 y el de la primera pareja es 0.25»). Cada fórmula se calcula donde
  tiene datos (extremo hacia adelante donde existe `x_(i+2)`, punto medio en
  los interiores, extremo hacia atrás donde existe `x_(i−2)`; «—» donde no).
  La columna **«Recomendada»** toma el punto medio donde existe y, en el
  primer y el último punto, el extremo hacia adelante y hacia atrás.
- **Comprobación:** además de la sustitución de `f'` y error ≤ cota, las
  **identidades** (con los valores sin redondear, ✔ si la diferencia es
  `≤ 10⁻⁹·máx(1, |valor|)`): punto medio `= (D⁺ + D⁻)/2` (el promedio de la
  progresiva y la regresiva) y extremo `= 2·D(h) − D(2h)`, con
  `D⁺(2h) = [f(x₀ + 2h) − f(x₀)]/(2h)` (extrapolación de Richardson, que
  cancela el término de orden `h`). En modo función, en la fila 1; en modo
  tabla, en cada punto, con los datos.

### Fórmula de 5 puntos

- Fórmulas, para un paso `h > 0` (todas de orden `O(h⁴)`):
  - punto medio `[f(x₀ − 2h) − 8f(x₀ − h) + 8f(x₀ + h) − f(x₀ + 2h)] / (12h)`,
    con `|error| ≤ (h⁴/30)·máx |f⁽⁵⁾(ξ)|`, ξ en `[x₀ − 2h, x₀ + 2h]`;
  - extremo hacia adelante `[−25f(x₀) + 48f(x₀ + h) − 36f(x₀ + 2h) +
    16f(x₀ + 3h) − 3f(x₀ + 4h)] / (12h)`, con `|error| ≤ (h⁴/5)·máx |f⁽⁵⁾(ξ)|`,
    ξ en `[x₀, x₀ + 4h]`;
  - extremo hacia atrás, el simétrico (coeficientes 25, −48, 36, −16, 3 con
    `x₀, x₀ − h, …, x₀ − 4h`), con la misma cota en `[x₀ − 4h, x₀]`.
- Son datos de `formulas.py` y usan el **mismo motor** que la de 3 puntos
  (`five_point.py`): refinamiento, mínimo de 6 filas, parada con todas las
  fórmulas pedidas en la misma fila, `R_k` con la regla de la de 3 puntos,
  paso a paso con productos, decimales `d` y advertencias. `f'` a `f⁽⁵⁾` se
  calculan simbólicamente una vez (cada una con su desglose desde la
  anterior) y `máx |f⁽⁵⁾|` se estima con los mismos 401 puntos. La **razón**
  se acerca a **0.0625** (dividir `h` entre 2 divide el error entre 16). Al
  ser tan precisa, el mejor `h` ronda 0.001: con tolerancias muy bajas, el
  aviso de redondeo puede salir en las últimas filas.
- En el paso a paso, la regla de `d` puede pedir un decimal más: en `x·eˣ`
  con `h = 0.1`, con 6 decimales `26.600399/1.2 = 22.166999 ≠ D`, así que se
  muestran 7 (`26.6003949/1.2 = 22.166996`).
- **Comparación** (debajo del resumen): qué darían el punto medio de 3
  puntos, la progresiva y la regresiva con el `h₀` de la fila 1 y con el `h`
  de la última fila, con su error real, y cuántas veces menor es el error de
  cada fórmula de 5 puntos frente a cada una. Con `x·eˣ`, `x₀ = 2`, `h = 0.1`:
  3 puntos 22.228787 (error 0.061619), progresiva 23.708446 (1.541278),
  regresiva 20.749128 (1.418041); el punto medio de 5 puntos tiene error
  0.000173, 357 veces menor que el de 3 puntos (el cociente usa los errores
  sin redondear).
- **Modo tabla:** de 5 a 20 puntos igualmente espaciados (si no, 400: «La
  fórmula de 5 puntos necesita datos igualmente espaciados…»). Columnas: las
  fórmulas pedidas, el **punto medio de 3 puntos** como referencia y
  **«Recomendada»**, que toma, en este orden: el punto medio de 5 puntos; el
  extremo de 5 puntos (hacia adelante si existe, si no hacia atrás); el punto
  medio de 3 puntos sólo donde no aplica ninguna de 5 puntos (el segundo y el
  penúltimo punto de una tabla de 5 datos). Con 6 o más datos, los dos
  primeros puntos quedan con el extremo hacia adelante y los dos últimos con
  el extremo hacia atrás.
- **Comprobación:** sustitución de `f'`, comparación final, error ≤ cota y la
  **identidad de Richardson** del punto medio, `D₅(h) = (4·D₃(h) − D₃(2h))/3`
  (combina dos fórmulas de 3 puntos para eliminar su error de orden `h²`; la
  idea de Romberg): en modo función en la fila 1, y en modo tabla en cada
  punto donde aplica, con `D₃(2h) = (y_(i+2) − y_(i−2))/(4h)`. El ✔ se decide
  sin redondear (`≤ 10⁻⁹·máx(1, |valor|)`); el resultado mostrado se calcula
  con los valores mostrados y, si difiere de `D₅` mostrado en una unidad del
  sexto decimal, se marca «(diferencia por redondeo)». Los extremos no tienen
  identidad: sólo se comprueba error ≤ cota.
- **Redondeo en la tabla de `x·eˣ`:** en `x = 2.0` (adelante), `2.2` (medio) y
  `2.3` (atrás) el cociente exacto de los datos termina en 5 en el séptimo
  decimal (22.1659225, 28.8798275, 32.9135975); en binario se muestran como
  22.165922, 28.879828 y 32.913598. En `x = 2.2` la identidad da
  `(4(28.958315) − 29.193778)/3 = 28.879827`, que se muestra con la nota de
  diferencia por redondeo.

### Método del trapecio

- **Fórmulas** (notación de Chapra y Canale), con `h = (b − a)/n` y
  `xᵢ = a + i·h`:
  - simple (`n = 1`): `I ≈ (b − a)·[f(a) + f(b)]/2`;
  - compuesta: `I ≈ (h/2)·[f(x₀) + 2·Σᵢ₌₁ⁿ⁻¹ f(xᵢ) + f(xₙ)]`.

  En el motor es una **regla compuesta con pesos** (`solvers/integration/rules.py`):
  pesos `1, 2, …, 2, 1` multiplicados por `h/2`. Simpson se declarará con
  `1, 4, 2, …, 4, 1` y `h/3`.
- **Tabla de refinamiento:** la fila `k` usa `n_k = n₀·2^(k−1)` y
  `h_k = (b − a)/n_k`. Columnas: `k`, `n`, `h` (exacto con hasta 12 decimales;
  si no, `(b − a)/n` con su aproximación), `T`, error estimado
  `|T_k − T_(k−1)|`, `Eₜ`, `εₜ`, `Eₐ`, cota, razón `Eₜ,k/Eₜ,(k−1)` (→ 0.25) y
  «`|Eₜ| ≤ cota + R_k`», con `R_k = 2ε·Σ|wᵢ·f(xᵢ)|·(h/2)`. Se detiene cuando
  el error estimado es `≤` tolerancia con al menos 6 filas; si se agota el
  máximo, `converged = false` con una advertencia.
- **Errores:**
  - verdadero `Eₜ = I − T`, con signo;
  - relativo `εₜ = |Eₜ|/|I|·100` («—» si `|I| < 10⁻¹²`);
  - aproximado de Chapra `Eₐ = −(b − a)h²/12·f̄''`, con
    `f̄'' = [f'(b) − f'(a)]/(b − a)` (el promedio exacto de `f''`, con `f'`
    simbólica; si `f'(a)` o `f'(b)` no es finita, no se muestra);
  - cota `(b − a)h²/12·M₂`, con `M₂ = máx |f''|` estimado con 2001 puntos
    equiespaciados (se indica en qué `x` se alcanzó).
- **Recurrencia:** desde la fila 2,
  `T_k = T_(k−1)/2 + h_k·Σ f(nuevos)`, con los nuevos en `a + (2j − 1)·h_k`:
  sólo se evalúan los puntos nuevos (la base de Romberg). Ejemplo 1:
  `T₂ = 0.1728/2 + 0.4·f(0.4) = 1.0688` y
  `T₃ = 1.0688/2 + 0.2·[f(0.2) + f(0.6)] = 1.4848`.
- **Paso a paso:** fila 1 con `h`, la tabla de `xᵢ`, `f(xᵢ)` y su peso (con
  más de 17 puntos, los 8 primeros y los 8 últimos) y la sustitución en la
  fórmula; filas siguientes con `h_k`, los puntos nuevos en verde (plegados
  si son más de 16), `T_(k−1)` en azul y la recurrencia; después, error
  estimado, `Eₜ`, `εₜ`, `Eₐ` con `f̄''` sustituido, la cota con `M₂` y la
  razón. Los valores usan 6 decimales y se agregan decimales (hasta 15) si
  hiciera falta para que el resultado visible sea coherente con ellos.
- **Integral exacta o de referencia** (`solvers/integration/exact.py`, común a
  todas las reglas): `sympy.integrate` da la antiderivada `F` (los decimales
  de `f` se pasan antes a racionales, así `F` sale con fracciones exactas
  como `200/3`); si `F` no contiene `Integral`, sólo usa funciones de la
  lista blanca y `F(a)`, `F(b)` son reales y finitos, `I = F(b) − F(a)`
  («exacta»). Si no (función especial como `erf`, tiempo agotado, integral
  impropia…), `I` se calcula con `mpmath.quad` a 30 dígitos («valor de
  referencia (cálculo numérico de alta precisión)») y `Eₜ` y `εₜ` se rotulan
  «respecto al valor de referencia». Sin ninguno de los dos, no se muestran
  `Eₜ`, `εₜ` ni la razón.
- **Límite de tiempo de la integración simbólica (3 s):** `sympy.integrate`
  corre en un **proceso hijo** que se mata al agotarse el plazo (`fork` en
  Linux/gunicorn, `spawn` en Windows con `runserver`). Un hilo no puede
  detenerse y `signal.alarm` no existe en Windows ni funciona fuera del hilo
  principal. El plazo empieza cuando el hijo avisa que está listo (en
  Windows, `spawn` tarda unos 2 s en importar sympy) y cada antiderivada se
  guarda en una caché.
- **Validaciones (400):** `a < b`; `f` real y finita en `a` y en `b`
  («f(x) no está definida en x = 0 (límite a)»); `f` sólo en `x`; `n₀` de 1 a
  1000; máximo de 6 a 22. Si un punto interior da un valor no finito (por
  ejemplo `1/(x − 1)` en `[0, 2]`), el método se detiene con
  `converged = false` y la advertencia «f(x) no está definida en x = 1,
  dentro de [0, 2]: la integral puede no existir»; si ocurre ya en la fila
  1, es un 400 con ese mensaje.
- **Notas:** si `f''` tiene un solo signo en `[a, b]` (según el muestreo):
  «f'' < 0 … el trapecio subestima la integral» o «f'' > 0 … sobreestima».
- **Modo tabla (espaciado no uniforme):**
  `I ≈ Σ (xᵢ₊₁ − xᵢ)·(yᵢ + yᵢ₊₁)/2`, cada trapecio con su propio ancho.
  Tabla de segmentos: `i`, `[xᵢ, xᵢ₊₁]`, `hᵢ`, `yᵢ`, `yᵢ₊₁`, área y área
  acumulada, con el paso a paso `hᵢ·(yᵢ + yᵢ₊₁)/2` de cada uno. Si el
  espaciado es uniforme, se indica y se muestra también la fórmula compuesta
  con `h`. Con función para comparar: integral exacta o de referencia en
  `[x₀, xₙ]`, `Eₜ`, `εₜ`, la cota por segmentos `Σ hᵢ³/12·máx|f''|` (401
  puntos por segmento) y la comprobación de los datos.
- **Comprobación:** con valor exacto, `F(x)` en LaTeX (coeficientes racionales
  como fracciones, `\frac{200}{3}x^3`), `F(b)` y `F(a)` término a término
  (`F(0.8) = 0.2(0.8) + 12.5(0.8)² − (200/3)(0.8)³ + … ≈ 0.16 + 8 −
  34.133333 + 69.12 − 58.9824 + 17.476267 ≈ 1.640533`; `F(0) = 0`, «todos sus
  términos se anulan»), la comparación `T`, `I`, `Eₜ`, `εₜ`, cota con ✔/⚠ y
  una línea sobre todas las filas. Con valor de referencia, se indica que no
  hay antiderivada elemental y se compara con la referencia. En modo tabla:
  la suma de las áreas es el total (con `≈` si las áreas a 6 decimales no
  suman exacto), la fórmula compuesta es igual a esa suma (si es uniforme),
  los datos contra `f` (`|yᵢ − f(xᵢ)| ≤ 10⁻⁶·máx(1, |f(xᵢ)|)`) y la
  comparación con la integral.
- **Ejemplos** (tolerancia `0.000001`, máximo 20):

  | # | Datos | Resultado |
  | --- | --- | --- |
  | 1 | Chapra `0.2 + 25x − 200x² + 675x³ − 900x⁴ + 400x⁵` en `[0, 0.8]` | exacta 1.640533; fila 1: T = 0.1728, Eₜ = 1.467733 (89.4668 %), Eₐ = 2.56, cota 17.066667; para en la fila 13 (n = 4096) |
  | 2 | `exp(-x^2)` en `[0, 1]` | referencia 0.746824 (erf); 0.68394, 0.73137, 0.742984; fila 10 |
  | 3 | `sin(x)` en `[0, π]` | exacta 2; 0, 1.570796, 1.896119; subestima; fila 13 |
  | 4 | `x^2` en `[0, 2]` | exacta 8/3; 4, 3, 2.75; `Eₐ = Eₜ` y `\|Eₜ\|` = cota; fila 12 |
  | 5 | `2x + 1` en `[1, 3]` | exacta 10 en todas las filas, error y cota 0; fila 6 |
  | 6 | `exp(x)` en `[0, 1]`, `n₀ = 2` | exacta e − 1; 1.753931, 1.727222, 1.720519; fila 10 (n = 1024) |
  | 7 | Tabla de Chapra con h = 0.1 + función | total 1.6008 = fórmula compuesta; Eₜ = 0.039733 (2.422 %) |
  | 8 | Tabla de Chapra con segmentos desiguales + función | total 1.594801; Eₜ = 0.045732 (2.7877 %); datos ✔ |

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
| POST | `/api/solve/bairstow/` | Halla todas las raíces de un polinomio con Bairstow |
| POST | `/api/solve/diferencias-finitas/` | Aproxima `f'(x)` con las diferencias progresiva y regresiva |
| POST | `/api/solve/tres-puntos/` | Aproxima `f'(x)` con la fórmula de 3 puntos (punto medio y extremos) |
| POST | `/api/solve/cinco-puntos/` | Aproxima `f'(x)` con la fórmula de 5 puntos (punto medio y extremos) |
| POST | `/api/solve/trapecio/` | Aproxima `∫ₐᵇ f(x) dx` con el método del trapecio |
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

Polinomios (Bairstow), con **exactamente uno** de `polynomial` (texto) o
`coefficients` (de mayor a menor potencia):

```json
{
  "polynomial": "x^5 - 3.5x^4 + 2.75x^3 + 2.125x^2 - 3.875x + 1.25",
  "r0": -1,
  "s0": -1,
  "tolerance": 0.0001,
  "max_iterations": 100
}
```

```json
{ "coefficients": [1, -6, 11, -6], "r0": -1, "s0": -1 }
```

En Bairstow, `tolerance` está en **porcentaje** (por defecto `0.0001`, debe
ser mayor que 0) y `max_iterations` es por factor. `r0` y `s0` son opcionales
(por defecto `−1`).

Diferencias finitas, modo función (`formula`: `forward`, `backward` o
`both`; `max_iterations` es el máximo de refinamientos de h, de 6 a 30):

```json
{
  "mode": "function",
  "function": "ln(x)",
  "x0": 1.8,
  "h0": 0.1,
  "formula": "both",
  "tolerance": 0.0001,
  "max_iterations": 25
}
```

Modo tabla (`points` con x estrictamente creciente, de 2 a 20 puntos;
`compare_function` es opcional):

```json
{
  "mode": "table",
  "points": [[0, 0], [1, 2], [2, 8], [3, 18], [4, 32], [5, 50]],
  "formula": "both",
  "compare_function": "2x^2"
}
```

Fórmula de 3 puntos: el mismo cuerpo, con `formula` = `punto_medio`,
`extremo_adelante`, `extremo_atras` o `all` (por defecto), `tolerance` por
defecto `0.000001` y, en modo tabla, de 3 a 20 puntos igualmente espaciados.

Fórmula de 5 puntos: el mismo cuerpo, con `formula` = `punto_medio_5`,
`extremo_adelante_5`, `extremo_atras_5` o `all` (por defecto) y, en modo
tabla, de 5 a 20 puntos igualmente espaciados.

Método del trapecio, modo función (`n0` de 1 a 1000, por defecto 1;
`max_iterations` de 6 a 22, por defecto 20; `tolerance` por defecto `0.000001`):

```json
{ "mode": "function", "function": "exp(-x^2)", "a": 0, "b": 1, "n0": 1, "tolerance": 0.000001, "max_iterations": 20 }
```

Modo tabla (de 2 a 30 puntos con x estrictamente creciente, espaciado libre;
`compare_function` opcional):

```json
{ "mode": "table", "points": [[0, 0.2], [0.12, 1.309729], [0.22, 1.305241]], "compare_function": "" }
```

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
  reordenamiento), `is_diagonally_dominant`, `reordered`, `row_order` y
  `verification`: la comprobación en el orden original de las ecuaciones
  (`solution`; `equations` con, por ecuación, `row` —índice original, desde
  0—, `terms` —`{coefficient, variable, value, term}` de cada coeficiente no
  nulo—, `lhs`, `b`, `residual` e `is_zero`; `max_residual`, `reordered` y
  `rounded_to_integers`, si la solución se vio entera y se comprobó con enteros).
- **Punto Fijo:** por ecuación, el despeje `g_i` (en LaTeX y en texto) y su
  paso a paso (`isolation`); `x0`; `failure`; `verification`: la comprobación
  (`solution` —con las variables enteras ya redondeadas—, `integers` —si cada
  variable se trató como entera—, `equations` con, por ecuación,
  `function_latex`, `function_text`, `terms` —`{sign, template, text, value}`
  de cada término de `f_i`, con marcadores `@@j@@` en lugar de cada
  variable—, `residual` e `is_zero`; `max_residual`, `raw_max_residual` —con
  los valores sin redondear— y `uses_trigonometry`).
- **Newton:** la función `f_i` de cada ecuación y sus términos, la Jacobiana
  simbólica con el desglose de cada derivada (`jacobian`), `x0`, `failure` y
  `verification` (la misma estructura que en Punto Fijo). En
  cada iteración, `extra` incluye `F`, `J`, `D`, `D_i` con sus matrices y
  `Δx`.
- **Bairstow:** `polynomial` (grado, coeficientes, LaTeX, texto y modo de
  entrada), `r0`, `s0`, `tolerance_percent`, `zero_roots` (raíces nulas
  extraídas en el paso previo), `factors` (por factor: polinomio que se
  divide, método —`bairstow`, `cuadratica_directa` o `lineal_directa`—,
  `iteration_indices` hacia `iterations`, `r`, `s`, discriminante, raíces,
  cociente y residuo), `roots` (`{re, im, check}` con `check = |f(raíz)|`),
  `factorization` (LaTeX), `notes` y `failure`. `iterations` reúne las
  iteraciones de todos los factores (cada `extra` lleva su `factor`, las
  tablas `b` y `c`, el sistema 2×2, los determinantes, `Δr`, `Δs`, `ε_r` y
  `ε_s`); `solution` y `variables` son el `[r, s]` del último factor
  iterado.
- **Diferencias finitas:** `mode`, `formula`, `formulas` (por fórmula: `key`,
  `name`, `symbol_latex`, `formula_latex`, `bound_latex`, `order`,
  `expected_ratio`, `nodes`…), `function` (`latex`, `text`, `template` con
  `@@0@@`, `uses_trigonometry`, `derivative` con su `steps` y
  `higher_derivatives`; `null` en modo tabla sin función), `sampling_points`
  y `verification`. En modo función, además, `x0`, `x0_display`, `h0`,
  `tolerance`, `max_iterations`, `exact` (`f'(x₀)` o `null`) y
  `differentiable`; en modo tabla, `points` y `uniform`. Cada elemento de
  `iterations` es una fila (modo función) o un punto (modo tabla); su `extra`
  lleva `h` (exacto: `exact`, `text`, `latex`, `approx`) y, por cada fórmula,
  `D`, `estimated_error`, `real_error`, `bound`, `M`, `x_M`, `ratio`,
  `rounding` (`R_k`), `within_bound`, `by_rounding`, `points` (nodos con su
  valor y su texto con `decimals` decimales) y `numerator_display`.
  `solution` es el último `D` de cada fórmula y `variables` sus claves.
- **Fórmula de 3 puntos:** lo mismo, y además `rounding_text` (la regla de
  `R_k`); en cada fórmula, `products_display` (cada `cᵢ·f(xᵢ)`) y
  `denominator_display` (`factor·h`); en modo función, `comparison` (por fila
  comparada: `k`, `h`, `forward` y `backward` con `D` y `real_error`, y
  `text`) y `verification.identities`; en modo tabla, `recommended`
  (`key`, `name`, `D`) en cada punto y `verification.identities` por punto.
- **Fórmula de 5 puntos:** lo mismo que la de 3 puntos; `comparison` lleva
  además `midpoint_3` y la respuesta, `comparison_title`. Las identidades son
  de tipo `romberg` (`base` = `D₃(h)`, `double` = `D₃(2h)`, `value`, `D`, sus
  textos `*_display`, `rounding_difference` y `ok`). En modo tabla, `formulas`
  y `variables` incluyen el punto medio de 3 puntos (`punto_medio`) de
  referencia.

- **Método del trapecio:** `mode`, `rule` (la regla como datos: `factor`,
  `ends`, `interior`, `formula_latex`, `bound_latex`, `expected_ratio`…),
  `function` (`latex`, `text`, `uses_trigonometry`, `first` y `second` con
  `f'` y `f''`; `null` en modo tabla sin función), `integral` (`kind` —
  `exact`, `reference` o `null`—, `value`, `label`, `special`, `timed_out`,
  `antiderivative`), `curve` (300 puntos de `f`), `chart_rows` (los puntos de
  cada fila con `n ≤ 64`), `notes`, `a_display`, `b_display`,
  `sampling_points` y `verification` (`upper` y `lower` con `F(b)` y `F(a)`
  término a término, `final`, `failed_rows`, `all_within`; en modo tabla,
  `areas`, `areas_sum`, `total_display` y `data`). En modo función, además,
  `n0`, `tolerance`, `max_iterations`, `width_display`, `mean_second`
  (`f'(a)`, `f'(b)` y `f̄''`) y `M2` (valor y `x`); cada `extra` de
  `iterations` lleva `n`, `h`, `T`, `previous_T`, `estimated_error`,
  `true_error`, `relative_error`, `approx_error`, `bound`, `rounding`,
  `within_bound`, `by_rounding`, `ratio` y `step` (el paso a paso con sus
  textos). En modo tabla, `points`, `total`, `uniform` y `composite`; cada
  `extra` es un segmento (`width`, `y`, `pair_sum`, `area`, `area_display`,
  `cumulative`, `bound`).

Los errores de validación de la entrada responden **400** con listas planas de
mensajes por campo. Un despeje imposible en Punto Fijo responde **400** con el
motivo en `detail`.

---

## Estructura del proyecto

```
metodos/
├── docker-compose.yml               # Ejecución con Docker (nginx + gunicorn) en :8080
├── .env.example                     # Variables de entorno de ejemplo para Docker
├── iniciar.bat, detener.bat,        # Scripts de doble clic para Docker en Windows
│   reconstruir.bat
├── backend/
│   ├── Dockerfile                   # Imagen del backend (Python 3.12 + gunicorn)
│   ├── core/                        # Configuración de Django (settings, urls)
│   └── numeric_methods/             # App principal
│       ├── registry.py              # Registro de métodos: slug, nombre, categoría, serializer y solver
│       ├── views.py, urls.py        # Una ruta /api/solve/<slug>/ por método registrado + methods, examples, preview
│       ├── examples_data.py         # Ejemplos precargados por método
│       ├── serializers/             # Validación de entrada: linear.py, nonlinear.py, polynomial.py,
│       │                            # differentiation.py, integration.py, expressions.py
│       ├── expressions/             # Manejo simbólico de ecuaciones (sympy)
│       │   ├── parser.py            #   Parseo seguro de texto del usuario
│       │   ├── differentiate.py     #   Derivadas parciales, gradiente y Jacobiano
│       │   ├── normalize.py         #   Forma evaluada de una expresión parseada y estimación de su grado
│       │   ├── to_latex.py          #   Conversión a LaTeX
│       │   └── to_text.py           #   Conversión a texto plano (mensajes y PDF)
│       ├── linalg/cramer.py         # Determinante por cofactores y regla de Cramer (Python puro)
│       ├── solvers/
│       │   ├── base.py              #   SolverResult / IterationStep: formato común de la respuesta
│       │   ├── validation.py        #   Constantes comunes (tolerancia, máx. y mín. de iteraciones)
│       │   ├── linear/              #   Jacobi, Gauss-Seidel, dominancia y reordenamiento
│       │   ├── nonlinear/           #   Punto Fijo (+ despeje paso a paso) y Newton (+ derivadas paso a paso)
│       │   ├── polynomial/          #   Bairstow: bairstow.py (iteración, deflación y cierres),
│       │                            #   synthetic.py (divisiones sintéticas b y c), validation.py
│       │                            #   (grado, coeficientes, texto → coeficientes), latex.py
│       │   └── differentiation/     #   Motor de fórmulas: formulas.py (cada fórmula como datos:
│       │                            #   nodos, coeficientes, factor, orden y cota),
│       │                            #   finite_differences.py (motor común: modos función y tabla,
│       │                            #   cota, comprobación; y las diferencias), three_point.py
│       │                            #   (fórmula de 3 puntos sobre el mismo motor), five_point.py
│       │                            #   (fórmula de 5 puntos), display.py
│       │                            #   (h exacto y decimales del paso a paso)
│       │   └── integration/         #   rules.py (cada regla compuesta como datos: pesos y factor),
│       │                            #   exact.py (integral exacta o de referencia, con límite de
│       │                            #   tiempo), trapezoid.py (modos función y tabla, recurrencia)
│       └── tests/                   # Tests unitarios y de API
└── frontend/
    ├── Dockerfile                   # Compila con Node y sirve dist/ con nginx
    ├── nginx.conf                   # Fallback a index.html, proxy /api/, gzip y caché
    └── src/
        ├── main.js                  # Carga el catálogo de métodos antes de montar la app
        ├── style.css                # Tipografía, espaciado y estilos base (consume los colores del tema)
        ├── assets/theme.css         # Paleta de colores del tema claro y del oscuro (variables CSS)
        ├── api/client.js            # Cliente Axios
        ├── router/index.js          # Rutas /resolver/<slug> y /teoria/<slug>, generadas desde el registro
        ├── views/                   # SolverView (genérica para todos los métodos) y TheoryView
        ├── methods/
        │   ├── registry.js          # Asocia cada categoría (y método) con su interfaz
        │   ├── linear/              # Formulario, detalle de iteración, PDF y teoría de Jacobi / Gauss-Seidel
        │   ├── nonlinear/           # Formularios, detalles, PDF y teoría de Punto Fijo y Newton
        │   ├── polynomial/          # Bairstow: formulario (texto o coeficientes), vista de resultado
        │   │                        # por factores, tablas sintéticas, paso a paso, PDF y teoría
        │   └── differentiation/     # Diferencias, 3 y 5 puntos: formulario (función o tabla), vista de
        │                            # resultado, tablas de refinamiento, paso a paso, comprobación, PDF
        │                            # y teoría (theory/, con las respuestas del solver en JSON)
        │   └── integration/         # Trapecio: vista de resultado, tabla de refinamiento con paso a
        │                            # paso, tabla de segmentos, comprobación y PDF
        ├── components/              # ResultsTable, ConvergenceChart, MathFormula, MatrixInput,
        │   │                        # MathSymbolToolbar, MathSyntaxHelp, NavMenu,
        │   │                        # NumericFieldsInput (x0, r0/s0, coeficientes), EquationPreview,
        │   │                        # FunctionTableInput (formulario función/tabla de diferenciación e
        │   │                        # integración), TrapezoidChart (gráfico de una regla de integración)
        │   └── theory/              # Piezas comunes de las páginas de teoría
        ├── composables/             # useExpressionPreviews (vista previa en vivo),
        │                            # useTheme (tema claro/oscuro, preferencia del sistema y elección guardada)
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
  `methods/linear/index.js`. Si su resultado no encaja en la tabla única de
  iteraciones (como Bairstow, con varios factores), puede declarar su propia
  vista en `resultView`, y ajustar `toleranceLabel`, `defaultTolerance` y
  `maxIterationsLabel`.
- Para que el método aparezca en «Teoría ▾», basta con agregar su sección a
  `THEORY_SECTIONS` en la página de teoría de su categoría.

No hace falta tocar `App.vue`, el router ni `NavMenu.vue`.

### Agregar una fórmula de derivación (por ejemplo, la de 5 puntos)

1. **Fórmulas** en `solvers/differentiation/formulas.py`: una `Formula` por
   variante con `key`, `name`, `symbol_latex` (con superíndice, para que
   `D^{…}_{k}` sea LaTeX válido), `nodes` (`(dᵢ, cᵢ)` en el orden en que se
   escriben), `divisor` (el factor de `factor·h`), `order` (`p` de `O(hᵖ)`),
   `bound_derivative` y `bound_coefficient` (la cota `c·hᵖ·máx|f⁽ⁿ⁾|` en el
   intervalo del menor al mayor desplazamiento), y los textos de la fórmula y
   la cota. Luego, su dict de opciones del selector (como
   `THREE_POINT_CHOICES`).
2. **Solver**, como `three_point.py` o `five_point.py`: llama a
   `_function_mode` y `_table_points` de `finite_differences.py` con sus
   opciones, su regla de redondeo (la `rounding` de `three_point.py` sirve
   para cualquier fórmula) y las derivadas extra, y agrega lo propio
   (comprobación, columna recomendada…). La línea de comparación es
   `_comparison` de `three_point.py`, con las fórmulas de referencia como
   parámetro. `build_result` arma el `SolverResult`.
3. **Serializer**: una subclase de `DifferentiationSerializer` con su campo
   `formula`, su tolerancia y su `min_points` (y validaciones extra de la
   tabla, como el espaciado uniforme; el mensaje usa su `method_label`).
4. **Registro y ejemplos**: `registry.py` y `examples_data.py`.
5. **Frontend**: en `methods/differentiation/index.js`, una entrada en
   `methods[slug]` con su `createStore` (opciones del selector, fórmula por
   defecto, mínimo de puntos y filas iniciales, ver `store.js`) y su
   `defaultTolerance`. La
   vista, las tablas, el paso a paso, el gráfico y el PDF ya dependen sólo de
   `result.formulas` y de los campos opcionales de la respuesta
   (`products_display`, `comparison`, `identities`, `recommended`,
   `rounding_text`).

### Agregar una regla de integración (por ejemplo, Simpson 1/3)

1. **Regla** en `solvers/integration/rules.py`: una `CompositeRule` con
   `factor` (`1/3`), `ends` (`1`), `interior` (`(4, 2)`: el patrón de pesos
   interiores), `segments_multiple` (`2`: n par), `order`,
   `bound_derivative`, `bound_divisor` y los textos LaTeX. `apply(rule,
   valores, h)` ya calcula la regla compuesta y el paso a paso de la fila 1
   (`_first_row_display`) agrupa los interiores por peso.
2. **Solver**: el modo función y el modo tabla de `trapezoid.py` reciben la
   regla como parámetro; la recurrencia `T_k = T_(k−1)/2 + h·Σ nuevos` es
   propia del trapecio (y la base de Romberg). La integral exacta o de
   referencia sale de `exact.definite_integral` para cualquier regla.
3. **Serializer, registro y ejemplos**: `IntegrationSerializer` sirve tal
   cual (o una subclase con validaciones extra, como `n` par).
4. **Frontend**: la categoría `integration` ya tiene formulario, gráfico de
   trapecios (`TrapezoidChart`, que recibe los puntos de cada fila), tablas,
   comprobación y PDF; un método nuevo sólo necesita su entrada en
   `methods[slug]` si cambia algo.

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

**400 tests**, todos en verde:

| Archivo | Tests | Qué cubre |
| --- | --- | --- |
| `test_solvers.py` | 23 | Jacobi y Gauss-Seidel, y su comprobación (términos y residuos exactos, solución que se ve entera, coeficiente 0, solución decimal, orden original tras reordenar, no convergencia) |
| `test_dominance.py` | 8 | Dominancia diagonal y reordenamiento de filas |
| `test_api.py` | 13 | Endpoints de los métodos lineales y de ejemplos |
| `test_registry.py` | 13 | Registro de métodos, catálogo y ejemplos por método |
| `test_expressions.py` | 49 | Parser seguro, derivación y LaTeX |
| `test_preview.py` | 31 | Endpoint de vista previa, logaritmos y límites de seguridad |
| `test_fixed_point.py` | 41 | Punto Fijo: despeje automático, rechazos, actualización secuencial, endpoint y comprobación (soluciones enteras, decimales con funciones, «lado = lado», no convergencia) |
| `test_isolation_steps.py` | 20 | Despeje paso a paso de Punto Fijo |
| `test_newton.py` | 38 | Newton y regla de Cramer: iteraciones calculadas a mano, Jacobiana singular, endpoint y comprobación (tres ejercicios con solución entera, ejemplo decimal, funciones trigonométricas, no convergencia) |
| `test_newton_steps.py` | 16 | Derivadas parciales paso a paso y sustitución en F |
| `test_differentiation.py` | 30 | Diferencias progresiva y regresiva: fórmulas exactas con `x²`, cúbica, Burden y Faires (filas 1, 2 y parada), respuestas guardadas para la teoría iguales a las del solver, filas de parada de los ejemplos, mínimo de 6 filas, no convergencia, razón ≈ 0.5, error real ≤ cota, h exacto, errores 400, modo tabla (secante común, datos, espaciado no uniforme), comprobación término a término, `abs(x)` y endpoint |
| `test_three_point.py` | 27 | Fórmula de 3 puntos: fracciones exactas (cúbica y `x²`), Burden y Faires (filas 1, 2, parada 11 y comparación con diferencias), filas de parada y primeras filas de los ejemplos, cuadrática exacta, razón ≈ 0.25, error real ≤ cota + R, identidades, productos del paso a paso, modo tabla (valores, «—», recomendada, identidades por punto, `x³` con errores iguales a la cota, dato alterado), errores 400 (tabla no uniforme, 2 puntos, dominio en «x₀ − 2h», tolerancia, máximo), respuestas guardadas para la teoría (filas 1 y 2, identidades e iguales a las del solver) y endpoint |
| `test_five_point.py` | 28 | Fórmula de 5 puntos: fracciones exactas (`x⁵` y cuártica), Burden y Faires (filas 1 y 2, parada en 6, comparación, identidad de Richardson y productos del paso a paso), filas de parada de los ejemplos, `x⁵` con error = cota, cuártica exacta, razón ≈ 0.0625, error real ≤ cota + R, `f⁽⁵⁾` término a término, modo tabla (valores, «—», punto medio de 3 puntos, recomendada, identidad por punto con el caso de redondeo de `x = 2.2`, `x⁴` con función, una sola fórmula, 5 datos, dato alterado), errores 400 (tabla no uniforme, 4 puntos, dominio en «x₀ − 4h», tolerancia, máximo) y endpoint |
| `test_trapezoid.py` | 31 | Método del trapecio: fracciones exactas (`x²` en [0, 2] con `Eₜ = Eₐ`, polinomio de Chapra), ejemplo 1 (filas 1 a 3, parada en 13, razón ≈ 0.25, comprobación término a término, paso a paso de la fila 1), recurrencia igual a la fórmula directa (ejemplos 1 y 6, filas 2 a 8, y a mano), filas de parada de los ejemplos, recta exacta, `\|Eₜ\| ≤ cota + R`, `x²` con error = cota, integral exacta o de referencia (erf, `sin`, `1/x`), límite de tiempo (simulado y real), notas de concavidad, modo tabla (uniforme, no uniforme, dato alterado, sin función), singularidad interior, errores 400 y endpoint |
| `test_bairstow.py` | 30 | Bairstow: divisiones sintéticas, primera iteración de Chapra calculada a mano, ejemplos, raíces nulas, raíz doble, cierres directos, fallos, endpoint y comprobación de raíces (sustitución término a término, potencias faltantes, par complejo, raíz nula y residuo) |

---

## Notas y alcance

- No hay autenticación ni persistencia: los resultados no se guardan y los
  ejemplos viven en `backend/numeric_methods/examples_data.py`.
- Los métodos para sistemas no lineales admiten de 2 a 6 ecuaciones; los
  lineales, de 3 a 12 variables en el formulario; Bairstow, polinomios de
  grado 3 a 10; diferencias finitas, de 6 a 30 refinamientos de h o de 2 a
  20 puntos; la fórmula de 3 puntos, de 6 a 30 refinamientos o de 3 a 20
  puntos igualmente espaciados; la de 5 puntos, de 6 a 30 refinamientos o de
  5 a 20 puntos igualmente espaciados.
- En diferencias finitas y en las fórmulas de 3 y 5 puntos, `M = máx |f''|`
  (o `|f'''|`, `|f⁽⁵⁾|`) se estima por muestreo (401 puntos), no se calcula exactamente:
  entre dos muestras podría haber un máximo algo mayor.
- En el método del trapecio, `M₂ = máx |f''|` se estima con 2001 puntos (401
  por segmento en modo tabla). Los límites `a` y `b` aceptan números y
  fracciones, no expresiones como `pi` (el formulario compartido con
  diferenciación no las admite): el ejemplo de `sin(x)` usa
  `b = 3.141592653589793`. `n_k` se limita a 2²¹ segmentos (con `n₀` grande
  y muchas filas se detiene con una advertencia).
- La página de Teoría del método del trapecio queda para otra tarea: hasta
  entonces no aparece en «Teoría ▾».
