# Métodos Numéricos Iterativos

Aplicación web full-stack para resolver, paso a paso, sistemas de ecuaciones
**lineales** y **no lineales**, las **raíces de polinomios** con métodos
iterativos, la **derivada numérica** con fórmulas de diferencias finitas y la
**integral numérica** con reglas de integración (métodos del trapecio y de Simpson, integración de Romberg y cuadratura gaussiana), y para
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
| Integración numérica | **Método de Simpson** | `∫ₐᵇ f(x) dx` con las reglas 1/3 (`n` par) y 3/8 (`n` múltiplo de 3), simples y compuestas, refinando `n`, o desde una tabla igualmente espaciada (de 3 a 30 puntos; con `n` impar, la combinación 1/3 + 3/8) |
| Integración numérica | **Integración de Romberg** | `∫ₐᵇ f(x) dx` con la **tabla triangular**: trapecios con `n = 1, 2, 4, …` (columna 1) mejorados con la extrapolación de Richardson (Simpson 1/3, Boole, …); desde `f(x)` (de 6 a 20 filas) o desde una tabla igualmente espaciada de `2ᵐ + 1` puntos (3, 5, 9, 17 o 33) |
| Integración numérica | **Cuadratura gaussiana** | `∫ₐᵇ f(x) dx` con Gauss-Legendre de `m` puntos (simple, `N = 1`, o compuesta en `N` subintervalos), agregando un punto por fila; sólo desde `f(x)` (los nodos son irracionales: no hay modo tabla) y sin evaluar `f` en los extremos |

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

- **Ejemplos precargados** por método (78 en total: 6 lineales compartidos por
  Jacobi y Gauss-Seidel, 4 de Punto Fijo, 3 de Newton, 9 de Bairstow, 8 de
  diferencias finitas, 8 de la fórmula de 3 puntos, 8 de la de 5 puntos, 8
  del método del trapecio, 8 del método de Simpson, 8 de Romberg y 8 de la
  cuadratura gaussiana),
  que se cargan en el
  formulario con un clic.
- **Botón «Limpiar»** al lado de «Resolver», en los doce métodos: deja la
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
  - Método de Simpson: el mismo formulario, con el selector **Regla**
    («Simpson 1/3», «Simpson 3/8» o «Ambas», por defecto) y un `n₀` por regla
    visible (1/3: par, de 2 a 1000, por defecto 2; 3/8: múltiplo de 3, de 3
    a 999, por defecto 3). En modo tabla, de 3 a 30 puntos **igualmente
    espaciados**.
  - Integración de Romberg: el mismo formulario sin `n₀` (siempre empieza con
    `n = 1`), con **máximo de filas** de 6 a 20 (por defecto 15). En modo
    tabla, `2ᵐ + 1` puntos igualmente espaciados (3, 5, 9, 17 o 33).
  - Cuadratura gaussiana: sólo el modo **Función**. En lugar del selector de
    modo, una nota explica por qué no hay modo tabla (los nodos son
    irracionales) con enlaces al Resolver del trapecio, Simpson y Romberg. En
    la configuración, los **subintervalos `N`** (de 1 a 50, por defecto 1, con
    su explicación), la tolerancia (`0.000001`) y el **máximo de puntos** (12,
    de 6 a 20). «Limpiar» deja `f`, `a` y `b` vacíos, `N = 1`, `0.000001` y 12.
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
  reutilizan Simpson (con el **gráfico de parábolas y cúbicas**), Romberg
  (con el **gráfico de segmentos** de las columnas 1 a 3) y la cuadratura
  gaussiana (con el **gráfico de rectángulos**).
- En el **método de Simpson**, la misma organización: resumen por regla con
  la **comparación con el trapecio** (mismo `n`, filas 1 y última), derivadas
  hasta `f⁽⁴⁾`, el **gráfico de parábolas y cúbicas** (selector de regla y de
  `n`), una tabla de refinamiento por regla con sus glosarios y su paso a
  paso, el gráfico de convergencia y la «Comprobación» con la **identidad con
  el trapecio** (ver su [detalle](#método-de-simpson)).
- En la **integración de Romberg**, la **tabla triangular** como resultado
  central: columnas con nombre y orden del error (Trapecio `O(h²)`, Simpson
  1/3 `O(h⁴)`, Boole `O(h⁶)`, Nivel k…) y tooltip, diagonal resaltada,
  resaltado de las dos celdas de las que sale cada `Rᵢ,ₖ` al pasar el cursor
  o tocarla, leyenda «¿Cómo se lee esta tabla?» y botón «Ver tabla de
  errores» (`Eₜ = I − Rᵢ,ₖ` en cada celda); antes de la tabla, el **gráfico
  de segmentos** (columnas 1 a 3, selector de columna y de `n`); la tabla de convergencia de la
  diagonal, el gráfico de convergencia (`|Eₜ|` de las columnas 1 y 2 y de la
  diagonal, error estimado y tolerancia), el paso a paso plegable de cada
  fila y la «Comprobación» con las identidades y la comparación de costo
  (ver su [detalle](#integración-de-romberg)).
- En la **cuadratura gaussiana**: resumen (`G` de la última fila con `m` y
  `N`, la integral con su rótulo, `Eₜ`, `εₜ`, evaluaciones totales y de la
  última fila), datos con el **cambio de variable** a `[−1, 1]` y su glosario,
  las derivadas pares para la cota (plegadas si son largas), las fórmulas con
  sus glosarios, el **gráfico de rectángulos** (selector de `m`), la tabla de
  refinamiento con tooltips y leyenda, el gráfico de convergencia, el paso a
  paso de cada fila y la «Comprobación» con los **momentos** y la comparación
  de costo (ver su [detalle](#cuadratura-gaussiana)).

### Vista «Teoría» (`/teoria/<método>`)

Una página por método, con el mismo formato en las doce (Jacobi,
Gauss-Seidel, Punto Fijo, Newton, Bairstow, diferencias progresiva y
regresiva, fórmulas de 3 y 5 puntos, método del trapecio, método de
Simpson, integración de Romberg y cuadratura gaussiana): fundamento común
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
- **Integración numérica:** fundamento común pensado también para Simpson,
  Romberg y cuadratura gaussiana (área con signo, por qué no basta la
  antiderivada, Newton-Cotes y Gauss, forma general `Σ wᵢ·f(xᵢ)`, reglas
  simples y compuestas, y por qué integrar **suaviza** el ruido que la
  diferenciación amplifica). El **método del trapecio** agrega: definición
  simple, compuesta y con segmentos desiguales; figura de los trapecios de
  Chapra con selector de `n` y las zonas que se pierden o se agregan, y el
  signo del error con `sin x` y `x²`; **derivación del error** (`−(b − a)³f''(ξ)/12`
  y su versión compuesta, de donde salen la cota y el `Eₐ` de Chapra); la
  fórmula de **Euler-Maclaurin**; la **recurrencia** al duplicar `n`; el
  **puente a Simpson y Romberg** por Richardson; tabla de razones ≈ 0.25,
  funciones periódicas; el ejemplo de Chapra y el de segmentos desiguales con
  datos reales del solver; tabla comparativa de la categoría. El **método de
  Simpson** comparte ese fundamento y agrega: reglas 1/3 y 3/8, simples y
  compuestas, y la combinación de Chapra para `n` impar; figura con selector
  de regla (trapecio, 1/3, 3/8) y de `n`, con las piezas en dos tonos; los
  **pesos 1, 4, 1 por Lagrange** (y 1, 3, 3, 1 para la cúbica) y
  `S = (2M + T)/3`; la **exactitud para cúbicas** por simetría; el error
  simple y compuesto (`(b − a)h⁴/180` y `/80`), con la cota y el `Eₐ` de
  Chapra; **1/3 frente a 3/8** (mismo intervalo o mismos puntos); Simpson
  como trapecio mejorado por **Richardson** (`(4Tₙ − T_(n/2))/3`) y el puente
  a Romberg; tabla trapecio frente a Simpson con razón 0.0625 y **eficiencia**
  (1601, 47 y 58 evaluaciones para `|Eₜ| ≤ 0.000001`); el ejemplo de Chapra
  y la combinación con `n = 5` con datos reales del solver, con un botón
  «Resolver este ejemplo» que lo carga y lo resuelve en Resolver
  (`/resolver/simpson?ejemplo=simp-chapra`); tabla comparativa de la
  categoría con las columnas de Simpson completas. La **integración de
  Romberg** comparte el mismo fundamento y agrega: la definición con la
  notación de Chapra (`Rᵢ,₁ = T(n = 2^(i−1))` y
  `Rᵢ,ₖ = (4^(k−1)Rᵢ,ₖ₋₁ − Rᵢ₋₁,ₖ₋₁)/(4^(k−1) − 1)`, con los casos 3, 15
  y 63) y el criterio de parada; la **tabla triangular** del Resolver con el
  resaltado de las celdas de origen y la lectura por filas y por columnas
  (trapecio, Simpson 1/3, Boole, nivel k); el **gráfico de segmentos** con
  selector de columna (`n = 4`); la derivación desde **Euler-Maclaurin**
  (enlazada a la tarjeta del trapecio), los dos primeros escalones y la regla
  general, con la sustitución del Resolver (8 decimales en `R₃,₃`); una
  tarjeta con los **pesos** de `R₂,₂`, `R₃,₃` (Boole) y `R₄,₄`, todos
  positivos, frente a los negativos de Newton-Cotes de 9 puntos; razones por
  columna y la **tabla triangular de errores** de `e^(−x²)` (con potencias de
  10 y la fila 4 en que `R₄,₃` supera a la diagonal); la tabla de **costo**
  de los ejemplos 1 a 5 y el caso lento de **√x** (razón ≈ 0.355); el
  ejemplo de Chapra (filas 1 a 3 con el paso a paso del Resolver, tablas,
  identidades, costo y «Resolver este ejemplo»). La **tabla comparativa de la
  categoría** es ahora un solo componente compartido por las tres páginas,
  con la columna de Romberg completa y las evaluaciones del trapecio y de
  Simpson contando cualquier `n` y duplicando `n` (1601 / 2049 y 47 / 65).
  La **cuadratura gaussiana** cierra la categoría con el mismo fundamento y
  agrega: por qué elegir también los nodos da exactitud hasta grado `2m − 1`;
  la definición en `[−1, 1]`, el **cambio de variable** a `[a, b]` y la
  versión compuesta, con la tabla de nodos y pesos en forma exacta
  (`m ≤ 4`); el **gráfico de rectángulos** del Resolver con selector
  `m = 1` a 4 y el área, la exacta y el error en vivo; una figura de los 3
  puntos de Simpson frente a los 3 nodos de Gauss con sus pesos; la
  derivación de **Gauss de 2 puntos por coeficientes indeterminados** (y la
  comprobación con `t⁴`), por qué `2m − 1` frente a Newton-Cotes, una tarjeta
  de los **polinomios de Legendre** (recurrencia, ortogonalidad, por qué sus
  raíces sirven y la fórmula de los pesos) y el **error** con sus constantes
  hasta `m = 5` (comprobado con `x⁶`); la convergencia de `e^(−x²)` y la
  **tabla de costo** de la categoría (Gauss 3, 4 y 5 evaluaciones); la
  tarjeta de **funciones singulares** (`1/√x`, con su gráfico, la compuesta
  y el cambio de variable `x = u²`; `sin(x)/x`); el ejemplo de Chapra con
  `m = 2` y `m = 3` en el paso a paso del Resolver, la tabla de refinamiento,
  los momentos de `m = 3`, la comprobación, la comparación con 3 y 2
  evaluaciones, el mini-ejemplo compuesto (`N = 2`) y «Resolver este
  ejemplo» (`/resolver/gauss?ejemplo=gauss-chapra`); y la guía **«¿Qué
  método de integración usar?»**. La tabla comparativa compartida queda
  completa en las cuatro páginas, con las filas nuevas «Dónde evalúa»,
  «`f` no definida en un extremo», «Reutiliza evaluaciones al refinar» y
  «Chapra con 3 evaluaciones». Todas las fórmulas importantes llevan su
  glosario «¿Qué significa cada símbolo?».

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
  pesos `1, 2, …, 2, 1` multiplicados por `h/2`. Simpson se declara igual,
  con `1, 4, 2, …, 4, 1` y `h/3` (ver [Método de Simpson](#método-de-simpson)).
- **Tabla de refinamiento:** la fila `k` usa `n_k = n₀·2^(k−1)` y
  `h_k = (b − a)/n_k`. Columnas: `k`, `n`, `h` (exacto con hasta 12 decimales;
  si no, `(b − a)/n` con su aproximación), `T`, error estimado
  `|T_k − T_(k−1)|`, `Eₜ`, `εₜ`, `Eₐ`, cota, razón `Eₜ,k/Eₜ,(k−1)` (→ 0.25) y
  «`|Eₜ| ≤ cota`». **Marca R:** `|Eₜ| ≤ cota·(1 + 10⁻⁹)` es ✔ normal (si además
  `|Eₜ|` y la cota difieren menos de `10⁻⁹` relativo, se escribe
  «|Eₜ| = cota ✔», con «la igualdad ocurre porque f'' es constante» cuando lo
  es, como en `x²`); la marca ✔ᴿ y su nota aparecen sólo si `|Eₜ|` supera ese
  margen y el ✔ depende del redondeo `R_k = 2ε·Σ|wᵢ·f(xᵢ)|·(h/2)`. Ningún
  ejemplo precargado la necesita. Se detiene cuando
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
- **Derivadas de f(x)** (en «Datos del problema»): para qué sirve cada una
  (`f'` para `Eₐ`, `f''` para la cota) y su desglose **término a término con
  la regla aplicada**, el mismo de Newton y diferenciación
  (`derivative_steps.entry_steps`): `d/dx(x²) = 2·x = 2x`,
  `d/dx(−200x²) = (−200)·2·x = −400x`, `d/dx(eˣ) = eˣ`; `f''` se obtiene
  derivando `f'` igual. Un término que el desglose no sabe separar muestra el
  resultado con «derivada calculada simbólicamente». La integral se escribe
  `∫₀² x² dx`: el integrando lleva paréntesis sólo si es una suma o resta.
- **Glosarios** (`methods/integration/glossary.js`, componentes
  `GlossaryBlock` e `InfoTip`): debajo de cada fórmula (regla compuesta, `Eₐ`
  y cota) un bloque plegable «¿Qué significa cada símbolo?» (visible por
  defecto) explica cada símbolo en una línea (`I`, `≈`, `a, b`, `n`, `h`,
  `xᵢ`, `f(xᵢ)`, `Σ`, el 2, `h/2`; `Eₐ`, `f̄''`, el signo menos, el 12; `|Eₜ|`,
  `≤`, `M₂`, `h²`). Cada encabezado de la tabla de refinamiento, de la de
  segmentos y de la de comparación tiene un tooltip (se abre también al
  tocarlo) y debajo de cada tabla va la leyenda «¿Qué significa cada
  columna?». Con valor de referencia, las leyendas de `Eₜ` y `εₜ` lo dicen.
- **Paso a paso explicado** (`methods/integration/explain.js`): cada paso
  tiene título, una o dos frases, la fórmula sustituida y el resultado.
  Fila 1: ancho `h₁ = (2 − 0)/1 = 2`; puntos `xᵢ = a + i·h`; tabla con la
  **sustitución** de cada `f(xᵢ)` término a término, el peso y `peso × f(xᵢ)`;
  suma ponderada `1·0 + 1·4 = 0 + 4 = 4` y área `T₁ = (2/2)·4 = 1·4 = 4`.
  Filas siguientes: `n` y `h` nuevos, por qué sólo se evalúan los puntos
  nuevos, cada punto nuevo con su cálculo y su sustitución (en verde), su suma
  (`f(0.5) + f(1.5) = 0.25 + 2.25 = 2.5`), la recurrencia con `T_(k−1)` en azul
  (`T₃ = 3/2 + 0.5·2.5 = 1.5 + 1.25 = 2.75`) y el error estimado comparado con
  la tolerancia. En todas: `Eₜ` y `εₜ` con una frase según el signo; `Eₐ`
  evaluando `f'(b)` y `f'(a)` término a término, `f̄''` y
  `−[(2)(2)²/12]·2 = −(8/12)·2 = −1.333333`; la cota con `f''` y `M₂` (si
  `f''` no es constante, `M₂ = |f''(x)|` sustituida donde se alcanzó, por
  ejemplo `f''(0) = −400` en Chapra), la comparación con la cota y la razón.
  Con más de 16 puntos se pliegan (8 primeros y 8 últimos); con 1024 o menos
  el botón «Mostrar todos los puntos» los muestra todos, y con más se indica
  «Se muestran 16 de N puntos; la suma usa todos». Los valores usan 6
  decimales y se agregan decimales (hasta 15) si hiciera falta para que el
  resultado visible sea coherente con ellos. En modo tabla, cada segmento:
  ancho, alturas, área y área acumulada.
- **Nota de `Eₜ` que se ve 0:** si `|Eₜ| < 0.0000005` y `εₜ` no se ve 0, se
  aclara debajo de la tabla, en el paso a paso y en la comprobación (ejemplo
  6: «… en porcentaje del valor exacto es 0.000008 %»).
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
- **Comprobación:** una frase de introducción y, con valor exacto, la
  **antiderivada paso a paso**: `∫ f dx` término a término con la regla
  (potencia `∫xⁿ dx = xⁿ⁺¹/(n + 1)`, constante, `eˣ`, `sin`, `cos`, `1/x`):
  `∫x² dx = x^(2+1)/(2+1) = (1/3)x³`; en Chapra, `0.2x`, `12.5x²`,
  `−(200/3)x³`, `168.75x⁴`, `−180x⁵` y `(200/3)x⁶`. Si sympy obtuvo `F` con
  otra técnica (sustitución, partes…), se muestra `F` con «antiderivada
  obtenida con integración simbólica; la técnica no se detalla aquí». Luego la
  **verificación `F' = f`**: se deriva `F` término a término con las mismas
  reglas y se marca «= f(x) ✔». Después, el teorema fundamental del cálculo
  («la integral de a a b es F(b) − F(a)»), `F(x)` en LaTeX (coeficientes
  racionales como fracciones, `\frac{200}{3}x^3`), `F(b)` y `F(a)` término a término
  (`F(0.8) = 0.2(0.8) + 12.5(0.8)² − (200/3)(0.8)³ + … ≈ 0.16 + 8 −
  34.133333 + 69.12 − 58.9824 + 17.476267 ≈ 1.640533`; `F(0) = 0`, «todos sus
  términos se anulan»), la comparación `T`, `I`, `Eₜ`, `εₜ`, cota con ✔/⚠
  (encabezados con tooltip y leyenda), una frase de conclusión («Con n = 4096
  trapecios el resultado coincide con la integral exacta en 6 decimales») y
  una línea sobre todas las filas. Con valor de referencia, se explica en
  palabras que la antiderivada no se puede escribir con funciones elementales
  y qué es el valor de referencia. En modo tabla:
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

### Método de Simpson

- **Reglas** (notación de Chapra y Canale), declaradas como datos en
  `solvers/integration/rules.py` (`SIMPSON_13` y `SIMPSON_38`), con
  `h = (b − a)/n` y `xᵢ = a + i·h`:

  | Regla | Condición sobre n | Pesos | Factor | Error compuesto | Error simple |
  | --- | --- | --- | --- | --- | --- |
  | Simpson 1/3 | par, ≥ 2 | `1, 4, 2, 4, …, 2, 4, 1` | `h/3` | `−(b − a)h⁴/180 · f⁽⁴⁾(ξ)` | `−(b − a)⁵/2880 · f⁽⁴⁾(ξ)` (n = 2) |
  | Simpson 3/8 | múltiplo de 3, ≥ 3 | `1, 3, 3, 2, 3, 3, 2, …, 3, 3, 1` | `3h/8` | `−(b − a)h⁴/80 · f⁽⁴⁾(ξ)` | `−(b − a)⁵/6480 · f⁽⁴⁾(ξ)` (n = 3) |

  Cada parábola usa 3 puntos seguidos (pesos 1, 4, 1) y cada cúbica 4 (1, 3,
  3, 1); donde dos piezas se tocan el punto se cuenta en las dos (1 + 1 = 2).
- **Refinamiento (modo función):** la fila `k` usa `n_k = n₀·2^(k−1)` en
  cada regla (al duplicar, la condición sobre `n` se mantiene) y se calcula
  con la **fórmula de pesos**; las alturas de la fila anterior se reutilizan
  (son los `xᵢ` con `i` par) y sólo se evalúan los puntos nuevos. Un test
  comprueba que coincide con la fórmula de pesos directa
  (`≤ 10⁻¹²·máx(1, |S|)`). Mínimo 6 filas; **para cuando todas las reglas
  pedidas** cumplen la tolerancia del error estimado en la misma fila. Con
  «Ambas», una tabla por regla, apiladas.
- **Errores** por fila: `Eₜ = I − S` y `εₜ`, como en el trapecio; el error
  aproximado de Chapra `Eₐ = −[(b − a)h⁴/C]·f̄⁽⁴⁾` con `C = 180` o `80` y
  `f̄⁽⁴⁾ = [f'''(b) − f'''(a)]/(b − a)` (el promedio exacto de `f⁽⁴⁾`); la cota
  `[(b − a)h⁴/C]·M₄`, con `M₄ = máx |f⁽⁴⁾|` estimado con 2001 puntos (y el `x`
  donde se alcanzó); la razón entre errores verdaderos consecutivos, que se
  acerca a **0.0625** (el error es `O(h⁴)`), y la marca R con el mismo
  criterio del trapecio (`R_k = 2ε·Σ|wᵢ·f(xᵢ)|·factor·h`). Si `f⁽⁴⁾` tiene un
  solo signo, se indica que Simpson sobreestima (`f⁽⁴⁾ > 0`) o subestima
  (`f⁽⁴⁾ < 0`): `Eₜ = −k·f⁽⁴⁾(ξ)` con `k > 0`.
- **Derivadas:** `f'`, `f''`, `f'''` y `f⁽⁴⁾` término a término con la regla
  aplicada (`f'''` para `Eₐ`, `f⁽⁴⁾` para la cota; `f'` y `f''` son pasos
  intermedios). En Chapra, `f⁽⁴⁾ = 48000x − 21600`, `f'''(0) = 4050` y
  `f'''(0.8) = 2130`.
- **Paso a paso de cada fila:** ancho `h`, puntos `xᵢ = a + i·h`, tabla de
  evaluaciones con la sustitución, el peso y **por qué** («extremo → 1»,
  «impar → 4», «par interior → 2»; en 3/8, «no múltiplo de 3 → 3» y
  «múltiplo de 3 → 2») y `peso × f(xᵢ)`, la suma ponderada, `S = (h/3)·suma`
  (o `(3h/8)·suma`), el error estimado, `Eₜ`, `εₜ`, `Eₐ` (con `f'''(b)` y
  `f'''(a)` sustituidas), la cota (con `f⁽⁴⁾` y `M₄` sustituida) y la razón.
  Mismo plegado y botón «Mostrar todos los puntos» que el trapecio.
- **Comparación con el trapecio** (debajo del resumen, por regla, filas 1 y
  última): lo que da el trapecio con el mismo `n`, su `Eₜ` y cuántas veces
  menor es el error de Simpson. Chapra, `n = 2`: trapecio 1.0688
  (`Eₜ = 0.571733`), Simpson 1/3 1.367467 (`Eₜ = 0.273067`), 2.1 veces menor;
  con `n = 16`, 149.8 veces.
- **Gráfico de parábolas y cúbicas** (`TrapezoidChart` con `row.pieces`): el
  backend muestrea la parábola (3 puntos) o la cúbica (4 puntos) de cada
  pieza; cada pieza alterna dos tonos de `theme.css`. Selector de `n`
  (filas con `n ≤ 64`) y, con «Ambas», de regla. En la combinación del modo
  tabla, la parte 1/3 y la 3/8 llevan colores distintos y su leyenda.
- **Modo tabla** (de 3 a 30 puntos, **espaciado uniforme obligatorio**; si
  no, un 400 que sugiere el método del trapecio). Con `n` segmentos:
  «Simpson 1/3» exige `n` par y «Simpson 3/8» `n` múltiplo de 3 (si no, un
  400 que sugiere otra opción); con «Ambas», 1/3 si `n` es par, 3/8 si `n` es
  múltiplo de 3 (con `n = 6`, las dos por separado) y, si `n` es impar y
  mayor que 3, la **combinación de Chapra**: 1/3 en los primeros `n − 3`
  segmentos y 3/8 en los últimos 3. Tabla de puntos con `i`, `xᵢ`, `yᵢ`, peso,
  `peso × yᵢ` y regla; el punto de unión pertenece a las dos partes (peso
  «1 + 1»). Resultado por partes y su suma; con función para comparar, `Eₐ` y
  la cota por partes, sumadas.
- **Comprobación:** la del trapecio (antiderivada paso a paso, `F' = f`,
  `F(b) − F(a)`, tabla de comparación por regla con leyenda, conclusión,
  modo referencia, datos contra la función) y la **identidad con el
  trapecio** (sólo Simpson 1/3, filas 1 y última):
  `S_n = (4T_n − T_(n/2))/3`, «Simpson 1/3 es el trapecio mejorado con la
  extrapolación de Richardson». El ✔ se decide sin redondeo
  (`≤ 10⁻⁹·máx(1, |S|)`); la sustitución usa los valores visibles. Chapra:
  `(4(1.0688) − 0.1728)/3 = 1.367467 ✔`. En modo tabla aplica sólo con 1/3 en
  todos los segmentos. Para 3/8 no hay una identidad tan simple.
- **Teoría:** página propia en «Teoría ▾», después del trapecio (ver la
  sección «Vista Teoría»).
- **Ejemplos** (tolerancia `0.000001`, máximo 20):

  | # | Datos | Regla | Resultado |
  | --- | --- | --- | --- |
  | 1 | Chapra en `[0, 0.8]` | Ambas | exacta 1.640533; 1/3: 1.367467, 1.623467, 1.639467 (fila 1: Eₜ = Eₐ = 0.273067, cota 2.4576 con M₄ = 21600 en x = 0); 3/8: 1.51917, 1.632948, 1.640059; para en la fila 7 (n = 128 y 192) |
  | 2 | `exp(-x^2)` en `[0, 1]` | Ambas | referencia 0.746824; 1/3: 0.74718, 0.746855, 0.746826; 3/8: 0.746992, 0.746838, 0.746825; fila 6 |
  | 3 | `sin(x)` en `[0, π]` | 1/3 | exacta 2; 2.094395, 2.00456, 2.000269; sobreestima; fila 6 |
  | 4 | `x^3` en `[0, 2]` | Ambas | exacta 4 en todas las filas, error y cota 0; fila 6 |
  | 5 | `x^4` en `[0, 2]` | Ambas | exacta 6.4; 1/3: 6.666667, 6.416667, 6.401042; 3/8: 6.518519, 6.407407, 6.400463; `\|Eₜ\|` = cota = `\|Eₐ\|`, sin R; fila 7 |
  | 6 | `1/x` en `[1, 2]` | 3/8 | exacta ln 2; 0.69375, 0.693195, 0.69315; fila 6 |
  | 7 | Tabla de Chapra con h = 0.1 (n = 8) + función | Ambas | sólo 1/3; suma ponderada 49.184; S = 1.639467; Eₜ = 0.001067 (0.065 %); identidad ✔ (T₈ = 1.6008, T₄ = 1.4848) |
  | 8 | Tabla de Chapra con n = 5 + función | Ambas | combinación: 1/3 en [0, 0.32] = 0.380324, 3/8 en [0.32, 0.8] = 1.264753; total 1.645077; Eₜ = −0.004544 (0.277 %) |

### Integración de Romberg

- **Columna 1 (trapecio):** `Rᵢ,₁ = T(2^(i−1))`, calculada con la
  recurrencia del trapecio (`Rᵢ,₁ = Rᵢ₋₁,₁/2 + hᵢ·Σ f(nuevos)`; la fila 1 es
  el trapecio simple). `solvers/integration/romberg.py` reutiliza de
  `trapezoid.py` la recurrencia y su paso a paso (`_first_step`,
  `_recurrence_step`), la integral exacta o de referencia y la comprobación
  de los datos.
- **Columnas siguientes (Richardson),** para `k = 2, …, i`:
  `Rᵢ,ₖ = (4^(k−1)·Rᵢ,ₖ₋₁ − Rᵢ₋₁,ₖ₋₁)/(4^(k−1) − 1)`. Al reducir `h` a la
  mitad, `h²` se divide entre 4, `h⁴` entre 16 y `h⁶` entre 64: con esos
  factores se cancela el término del error que se quiere eliminar.

  | Columna | Nombre | Orden del error | Exacta para grado |
  | --- | --- | --- | --- |
  | 1 | Trapecio | `O(h²)` | ≤ 1 |
  | 2 | Simpson 1/3 | `O(h⁴)` | ≤ 3 |
  | 3 | Boole | `O(h⁶)` | ≤ 5 |
  | k ≥ 4 | Nivel k | `O(h^(2k))` | ≤ 2k − 1 |

- **Mejor valor de cada fila:** la diagonal `Rᵢ,ᵢ`. **Error estimado**
  `|Rᵢ,ᵢ − Rᵢ₋₁,ᵢ₋₁|` («—» en la fila 1) y, como columna informativa, el
  error aproximado de Chapra `εₐ = |(Rᵢ,ᵢ − Rᵢ₋₁,ᵢ₋₁)/Rᵢ,ᵢ|·100 %` («—» si
  `|Rᵢ,ᵢ| < 10⁻¹²`).
- **Criterio de parada:** error estimado `≤` tolerancia y al menos 6 filas.
  Si se llega al máximo de filas (de 6 a 20, por defecto 15) sin cumplirlo,
  `converged = false` con una advertencia. Las validaciones son las del
  trapecio (`a < b`, dominio en `a` y `b`, una sola variable `x`); una
  singularidad interior detiene el método con advertencia.
- **Coherencia de decimales del paso a paso:** cada extrapolación se
  sustituye con los valores visibles a 6 decimales; si el resultado no
  coincide con el valor guardado (redondeado a 6), ese paso usa 8, 10 o 12
  decimales (el mínimo que haga coincidir). Chapra, `R₃,₃`:
  `(16(1.62346667) − 1.36746667)/15 = 24.60800005/15 = 1.64053334 ≈ 1.640533`
  (con 6 decimales daría 1.640534).
- **Modo tabla:** `2ᵐ + 1` puntos igualmente espaciados (3, 5, 9, 17 o 33);
  si no, un 400 sugiere el trapecio o Simpson. Hay `m + 1` filas: la fila
  `i` usa uno de cada `2^(m−i+1)` datos (fila 1: los extremos; fila 2: 0,
  mitad y final…) y el paso a paso indica qué datos usa. Aquí no aplica el
  mínimo de 6 filas (con 9 puntos sólo se pueden armar 4).
- **Identidades** (siempre, también sin valor exacto): `Rᵢ,₁` es el trapecio
  con `n = 2^(i−1)` calculado con la fórmula directa de pesos y `Rᵢ,₂` es
  Simpson 1/3 con el mismo `n` calculado con su motor (`rules.apply`); ✔ si
  la diferencia es `≤ 10⁻¹²·máx(1, |valor|)`.
- **Comparación de costo** (con exacta o referencia): evaluaciones de `f` de
  Romberg (`2^(filas−1) + 1`), la primera fila en que la diagonal tuvo
  `|Eₜ| ≤ tolerancia` y cuántas habrían necesitado el trapecio y Simpson 1/3
  duplicando `n` desde 1 y desde 2 (hasta `n = 2²²`; si no llegan, «más de
  4 194 305»). Ejemplo 1: «Romberg llegó a |Eₜ| ≤ 0.000001 en la fila 3, con
  5 evaluaciones; el trapecio habría necesitado 2049 y Simpson 65. Por el
  mínimo de 6 filas, el sistema usó 33». El mínimo de 6 filas es un
  requisito del curso, no del método.
- **Advertencia de función poco suave:** si en las últimas 3 filas la razón
  entre errores estimados consecutivos de la diagonal es mayor que 0.1. Sólo
  cuentan las razones en que los dos errores son mayores que
  `1000·ε·máx(1, |Rᵢ,ᵢ|)` (más chicos son ruido de redondeo, como las filas 4
  a 6 del ejemplo 1) y hacen falta al menos 2 que cuenten.
- **Gráfico de segmentos** (`TrapezoidChart`, el mismo del trapecio y de
  Simpson): cada celda `Rᵢ,ₖ` de las columnas 1 a 3 es una regla de
  Newton-Cotes compuesta con `n = 2^(i−1)` segmentos, así que se dibuja: la
  columna 1 con rectas (trapecios), la 2 con parábolas por 3 puntos (desde la
  fila 2) y la 3 con polinomios de grado 4 por 5 puntos (Boole, desde la fila
  3). Selector de columna (por defecto la 1) y de `n` (sólo las filas con
  `n ≤ 64` en que existe la columna); la leyenda muestra `Rᵢ,ₖ`, la exacta o
  de referencia y `Eₜ`, y el área sombreada es esa celda (test: la integral
  exacta de las piezas coincide con `Rᵢ,ₖ` con diferencia
  `≤ 10⁻⁹·máx(1, |R|)`). El backend manda `chart_rows` (`i`, `n`, `x`, `y`,
  `columns`: las piezas de cada columna, 2 puntos por recta y 30 por
  parábola o curva de grado 4) y `curve`. **Desde la columna 4 no hay
  figura:** Romberg combina resultados de forma algebraica y el valor ya no
  equivale a reemplazar la curva por piezas de un polinomio con esos puntos.
  En el modo tabla las piezas pasan por los datos que usa cada fila y la
  curva de `f` sólo aparece con función para comparar. El PDF incluye el
  gráfico elegido en pantalla (por defecto, columna 1 con el mayor `n ≤ 8`).
  Ejemplo 5 (√x, 13 filas): la respuesta pasa de ~466 KB a ~607 KB.
- **Teoría:** `/teoria/romberg`, en «Teoría ▾» después de Simpson (ver la
  sección «Vista Teoría»). Usa respuestas guardadas del solver
  (`theory/rombergExample.json`: ejemplos 1, 2 y 5), que
  `test_romberg.TheoryExampleTests` compara con el solver.
- **Ejemplos** (tolerancia `0.000001`, máximo 15):

  | # | Datos | Resultado |
  | --- | --- | --- |
  | 1 | Chapra en `[0, 0.8]` | exacta 1.640533; filas 1 a 3: [0.1728], [1.0688, 1.367467], [1.4848, 1.623467, 1.640533] (R₃,₃ ya es exacto); para en la fila 6 (33 evaluaciones); costo: fila 3 con 5, trapecio 2049, Simpson 65 |
  | 2 | `exp(-x^2)` en `[0, 1]` | referencia 0.746824; diagonal 0.68394, 0.74718, 0.746834, 0.746824; fila 6; costo: fila 4 con 9, trapecio 257, Simpson 17 |
  | 3 | `sin(x)` en `[0, π]` | exacta 2; diagonal 0, 2.094395, 1.998571, 2.000006, 2; fila 6; costo: fila 5 con 17, trapecio 2049, Simpson 65 |
  | 4 | `x^5` en `[0, 2]` | exacta 32/3; filas 1 a 3: [32], [17, 12], [12.3125, 10.75, 10.666667]; fila 6; costo: fila 3 con 5, trapecio 8193, Simpson 129 |
  | 5 | `sqrt(x)` en `[0, 1]` | exacta 2/3; la diagonal mejora lentamente (advertencia de función poco suave); fila 13 (4097 evaluaciones); costo: fila 12 con 2049, trapecio 4097, Simpson 2049 |
  | 6 | `1/x` en `[1, 2]` | exacta ln 2; diagonal 0.75, 0.694444, 0.693175, 0.693147; fila 6; costo: fila 4 con 9, trapecio 257, Simpson 17 |
  | 7 | Tabla de Chapra con h = 0.1 (9 puntos) + función | 4 filas: [0.1728], [1.0688, 1.367467], [1.4848, 1.623467, 1.640533], [1.6008, 1.639467, 1.640533, 1.640533]; Eₜ = 0 |
  | 8 | Tabla de `e^(−x²)` en x = 0, 0.25, …, 1 (5 puntos) | 3 filas: [0.68394], [0.73137, 0.74718], [0.742984, 0.746855, 0.746834]; mejor valor 0.746834 |

### Cuadratura gaussiana

- **Fórmula** (Gauss-Legendre, notación de Chapra). Simple (`N = 1`), con `m`
  puntos: `I ≈ (b − a)/2 · Σ wᵢ·f(xᵢ)` con el **cambio de variable**
  `xᵢ = (b + a)/2 + (b − a)/2·tᵢ` (`dx = (b − a)/2·dt`: lleva `[a, b]` a
  `[−1, 1]`, donde están calculados los nodos y pesos). **Compuesta:** `[a, b]`
  en `N` subintervalos de ancho `H = (b − a)/N`, centros
  `c_j = a + (j − ½)H` y la fórmula simple en cada uno:
  `I ≈ Σⱼ H/2 · Σᵢ wᵢ·f(c_j + H/2·tᵢ)`.
- **Nodos y pesos** (`solvers/integration/gauss.py`, `nodes_and_weights`):
  los nodos son las raíces del polinomio de Legendre `P_m(t)`, calculadas con
  el método de Newton sobre la recurrencia
  `(k + 1)P_(k+1) = (2k + 1)·t·P_k − k·P_(k−1)` desde `cos(π(i − ¼)/(m + ½))`
  hasta que el cambio sea menor que `10⁻¹⁵`; las negativas son el reflejo de
  las positivas (y 0 si `m` es impar). Pesos `wᵢ = 2/[(1 − tᵢ²)·P'_m(tᵢ)²]`.
  Para `m ≤ 4` se envía además la forma exacta en LaTeX (`±1/√3`;
  `0, ±√(3/5)` con `8/9, 5/9`; `±√(3/7 ∓ (2/7)√(6/5))` con `(18 ± √30)/36`).
  Los tests comparan con esas formas (`≤ 10⁻¹⁴`) y, para `m = 1..20`,
  revisan que los pesos sumen 2 y los nodos sean simétricos.
- **Refinamiento por `m`:** la fila `k` usa `m = k` puntos con el `N` elegido
  fijo: `G_m`, error estimado `|G_m − G_(m−1)|` («—» en la fila 1), `Eₜ`,
  `εₜ`, la cota y las evaluaciones `m·N` (Gauss no reutiliza nodos). No hay
  columna razón: el error no baja en una proporción fija (como 0.25 en el
  trapecio) sino cada vez más rápido; la leyenda lo explica. **Parada:**
  error estimado `≤` tolerancia y al menos 6 filas; si se llega al máximo de
  puntos (de 6 a 20, por defecto 12), `converged = false` con advertencia.
- **Cota** (hasta `m = 5`):
  `|Eₜ| ≤ (b − a)·H^(2m)·(m!)⁴/((2m + 1)[(2m)!]³)·M₂ₘ`, con `M₂ₘ = máx|f⁽²ᵐ⁾|`
  muestreado en 2001 puntos (con `N = 1` es la de Chapra,
  `(b − a)^(2m+1)·…`). Las derivadas hasta `f⁽¹⁰⁾` se calculan en un proceso
  hijo con el mismo límite de 3 s que la antiderivada (`exact.derivatives`,
  que conserva las ya terminadas). Con `m > 5`, tiempo agotado o `f⁽²ᵐ⁾` no
  finita en una muestra (por ejemplo `1/√x` en 0), la cota es «no disponible»
  con una nota. Criterio ✔/⚠/R como en los otros métodos, con
  `R = 2ε·[(H/2)·Σ wᵢ·Σₖ|términoₖ(xᵢ)| + |G|]`: se suman los valores
  absolutos de los términos de `f` porque en el polinomio de Chapra se cancelan
  y el redondeo de `f(xᵢ)` es mayor que `ε·|f(xᵢ)|`.
- **Sin modo tabla:** los nodos son irracionales; el formulario lo explica y
  enlaza al trapecio, Simpson y Romberg (y el API responde 400 a `mode: table`).
- **No evalúa los extremos:** no se exige que `f` esté definida en `a` ni en
  `b`; si no lo está, una nota lo dice («Gauss no evalúa los extremos, así que
  puede calcular la integral, pero la convergencia puede ser lenta»), como una
  ventaja frente a los otros métodos. Sí se exige (400) que `f` sea real y
  finita en todos los nodos de la fila 1 (el mensaje dice el nodo y su `x`); un
  nodo no finito en una fila posterior detiene el método con advertencia.
- **Paso a paso de cada fila:** nodos y pesos (forma exacta y decimal), cada
  nodo llevado a `[a, b]` (`x₁ = 0.4 + 0.4(−0.57735) = 0.16906`; con `N > 1`,
  por subintervalo con `c_j` y `H/2`), `f(xᵢ)` sustituida en verde, `wᵢ·f(xᵢ)`
  y su suma, el factor `(b − a)/2` (o `H/2` y la suma de subintervalos), el
  error estimado en azul y verde, `Eₜ` y `εₜ`, y la cota con `f⁽²ᵐ⁾`, `M₂ₘ`
  sustituida y la constante. Los nodos y productos usan la regla de coherencia
  de decimales de los otros métodos; con `m·N > 16` las tablas se pliegan.
- **Gráfico de rectángulos** (`TrapezoidChart` con `row.rects`): en cada nodo,
  un rectángulo de altura `f(xᵢ)` y ancho `wᵢ·H/2` centrado en el nodo, con dos
  tonos alternos semitransparentes (se ve dónde se superponen), los nodos
  marcados, líneas tenues en los bordes de los subintervalos y selector de `m`.
  Test: la suma de las áreas es `G_m` (`≤ 10⁻¹²·máx(1, |G|)`) y la de los
  anchos, `b − a`.
- **Momentos** (comprobación, con el `m` de la última fila): `Σ wᵢtᵢᵏ` frente a
  `∫₋₁¹ tᵏ dt` (2/(k + 1) si `k` es par, 0 si es impar) para `k = 0, …, 2m − 1`
  (✔) y la fila `k = 2m`, que ya no coincide (`m = 3`, `k = 6`: 0.24 frente a
  2/7). Con `m` grande se muestran los 4 primeros, los 3 últimos y la fila `2m`.
- **Comparación de costo** (con exacta o referencia): la primera fila de Gauss
  con `|Eₜ| ≤ tolerancia` (`m·N` evaluaciones) frente al trapecio y Simpson
  1/3 duplicando `n` y Romberg (primera fila de la diagonal), hasta `n = 2²²`.
  Si `f` no está definida en `a` o en `b`, esos tres son «no aplicable
  (evalúan los extremos)».
- **Teoría:** `/teoria/gauss`, en «Teoría ▾» después de Romberg (ver la
  sección «Vista Teoría»). Usa respuestas guardadas del solver
  (`theory/gaussExample.json`: ejemplos 1, 2, 4, 5 y 7), que
  `test_gauss.TheoryExampleTests` compara con el solver.
- **Ejemplos** (tolerancia `0.000001`, máximo 12):

  | # | Datos | N | Resultado |
  | --- | --- | --- | --- |
  | 1 | Chapra en `[0, 0.8]` | 1 | exacta 1.640533; `x = 0.4 + 0.4t`; m = 1, 2, 3: 1.9648 (Eₜ = −0.324267, 19.7659 %, cota 8.533333), 1.822578 (Eₜ = −0.182044, 11.0967 %, cota 1.6384), 1.640533 (cota 0); m = 2: x = 0.16906 y 0.63094, f = 1.291851 y 3.264593, 0.4·4.556444 = 1.822578; fila 6; costo: Gauss 3, Romberg 5, Simpson 65, trapecio 2049 |
  | 2 | `exp(-x^2)` en `[0, 1]` | 1 | referencia 0.746824; 0.778801, 0.746595, 0.746815, 0.746824; fila 6; costo: Gauss 4, Romberg 9, Simpson 17, trapecio 257 |
  | 3 | `sin(x)` en `[0, π]` | 1 | exacta 2; 3.141593, 1.93582, 2.001389, 1.999984, 2; cotas 1.291928, 0.070838, 0.001498, 0.000017, 0; fila 6; costo: Gauss 5, Romberg 17, Simpson 65, trapecio 2049 |
  | 4 | `x^6` en `[−1, 1]` | 1 | exacta 2/7; 0, 0.074074, 0.24, 0.285714 (exacta desde m = 4); m = 3: Eₜ = cota = 0.045714 sin R; fila 6 |
  | 5 | `1/sqrt(x)` en `[0, 1]` | 1 | exacta 2; nota de ventaja (f no definida en 0); 1.414214, 1.65068, 1.750863, 1.806343, 1.8416, 1.865992, …, 1.930337; no converge con 12; cota no disponible; costo de los otros «no aplicable» |
  | 6 | `sin(x)/x` en `[0, π]` | 1 | referencia 1.851937 (Si(x)); nota (f no definida en 0); 2, 1.848572, 1.851976, 1.851937; fila 6 |
  | 7 | Chapra compuesta | 2 | exacta 1.640533; H = 0.4; 1.9008, 1.651911 (Eₜ = −0.011378, cota 0.1024), 1.640533; m = 2: x = 0.08453, 0.31547, 0.48453, 0.71547; fila 6 (12 evaluaciones en la última) |
  | 8 | `exp(x)` en `[0, 4]` | 4 | exacta e⁴ − 1; 51.428356, 53.586127, 53.598124, 53.59815; fila 6 |

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
| POST | `/api/solve/simpson/` | Aproxima `∫ₐᵇ f(x) dx` con el método de Simpson (reglas 1/3 y 3/8) |
| POST | `/api/solve/romberg/` | Aproxima `∫ₐᵇ f(x) dx` con la integración de Romberg (tabla triangular) |
| POST | `/api/solve/gauss/` | Aproxima `∫ₐᵇ f(x) dx` con la cuadratura gaussiana (Gauss-Legendre) |
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

Método de Simpson: el mismo cuerpo que el trapecio, con `rule` =
`simpson13`, `simpson38` o `both` (por defecto) y, en modo función, `n0_13`
(par, de 2 a 1000, por defecto 2) y `n0_38` (múltiplo de 3, de 3 a 999, por
defecto 3) en lugar de `n0`. En modo tabla, de 3 a 30 puntos igualmente
espaciados:

```json
{ "mode": "function", "function": "exp(-x^2)", "a": 0, "b": 1, "rule": "both", "n0_13": 2, "n0_38": 3 }
```

La respuesta de Simpson trae `rules` (modo función: por regla, `rule`, `n0`,
`rows` con `S`, errores, `trapezoid`, `identity` y `step`, `chart_rows` con
las `pieces` del gráfico y `verification`), `mean_fourth` y `M4`; en modo
tabla, `applications` (cada regla aplicada con sus `parts`, `points`, `total`,
`final` e `identity`).

Integración de Romberg: el mismo cuerpo que el trapecio sin `n0`, con
`max_iterations` = máximo de filas (de 6 a 20, por defecto 15). En modo
tabla, `2ᵐ + 1` puntos igualmente espaciados (3, 5, 9, 17 o 33):

```json
{ "mode": "function", "function": "0.2 + 25x - 200x^2 + 675x^3 - 900x^4 + 400x^5", "a": 0, "b": 0.8, "tolerance": 0.000001, "max_iterations": 15 }
```

Cada `iterations[i].extra` es una fila de la tabla triangular: `values`
(`Rᵢ,₁ … Rᵢ,ᵢ`), `best` (la diagonal), `errors` (`Eₜ` de cada celda),
`estimated_error`, `approx_error` (`εₐ` %), `true_error`, `relative_error`,
`trapezoid` (la fila del trapecio con su `step`), `extrapolations` (cada
`Rᵢ,ₖ` con los textos coherentes del paso a paso) y, en modo tabla,
`data_points` y `new_points`. La respuesta trae además `columns` (nombre y
orden de cada columna), `evaluations`, `cost` (comparación de costo y su
texto) y `verification` (`identities`, `final` y, en modo tabla, `data`).

Cuadratura gaussiana: sólo modo función (`mode: "table"` responde 400), sin
`n0`, con `subintervals` = `N` (de 1 a 50, por defecto 1) y `max_iterations`
= máximo de puntos (de 6 a 20, por defecto 12):

```json
{ "function": "exp(-x^2)", "a": 0, "b": 1, "subintervals": 1, "tolerance": 0.000001, "max_iterations": 12 }
```

Cada `iterations[i].extra` es una fila (`m`, `evaluations`, `G`,
`estimated_error`, `true_error`, `relative_error`, `bound`, `bound_reason`
—`order`, `timeout` o `not_finite` si no hay cota—, `bound_info` con la
constante, `(b − a)·H^(2m)` y `M`, `rounding`, la marca y `step`: nodos y
pesos con su forma exacta y, por subintervalo, los puntos con su sustitución y
productos). La respuesta trae además el cambio de variable (`center_display`,
`half_width_display`, `H_display`, `half_display`, `centers`),
`undefined_ends`, `function.derivatives`, `evaluations`, `cost`, `curve`,
`chart_rows` (los rectángulos de cada `m`) y `verification` (`final`,
`moments` y, si hay exacta, la antiderivada).

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
  `function` (`latex`, `text`, `is_sum`, `uses_trigonometry`,
  `substitution_terms` —las plantillas de `f` para sustituir cada punto—,
  `first` y `second` con `f'` y `f''` y su desglose `steps`, y
  `second.constant`; `null` en modo tabla sin función), `integral` (`kind` —
  `exact`, `reference` o `null`—, `value`, `label`, `special`, `timed_out`,
  `antiderivative` con `latex`, `text`, `steps` —`detailed` y los términos
  con su regla— y `check` —`F'` término a término, `sum_latex`, `ok`—),
  `mean_second` (`fa`, `fb`, `value` y `fa_substitution`/`fb_substitution`),
  `M2` (`value`, `x`, `x_display` y `substitution`, `f''` sustituida donde se
  alcanzó o `null` si es constante), `min_rows`, `curve` (300 puntos de `f`), `chart_rows` (los puntos de
  cada fila con `n ≤ 64`), `notes`, `a_display`, `b_display`,
  `sampling_points` y `verification` (`upper` y `lower` con `F(b)` y `F(a)`
  término a término, `final`, `failed_rows`, `all_within`; en modo tabla,
  `areas`, `areas_sum`, `total_display` y `data`). En modo función, además,
  `n0`, `tolerance`, `max_iterations` y `width_display`; cada `extra` de
  `iterations` lleva `n`, `h`, `T`, `previous_T`, `estimated_error`,
  `below_tolerance`, `true_error`, `relative_error`, `approx_error`,
  `coefficient_numerator` (`(b − a)·h²`), `bound`, `rounding`,
  `within_bound`, `by_rounding`, `equals_bound`, `ratio` y `step` (el paso a
  paso con sus textos; cada punto con `x`, `f`, los valores de cada término
  en `terms` y, en la fila 1, `weight` y `product`; llegan todos si son 1024
  o menos, si no los 8 primeros y los 8 últimos). En modo tabla, `points`, `total`, `uniform` y `composite`; cada
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
│       │                            #   tiempo), trapezoid.py (modos función y tabla, recurrencia),
│       │                            #   simpson.py (reglas 1/3 y 3/8, combinación y tabla),
│       │                            #   romberg.py (tabla triangular, identidades y costo),
│       │                            #   gauss.py (nodos y pesos, filas por m, cota, momentos y costo)
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
        │   └── integration/         # Trapecio, Simpson, Romberg (Romberg*.vue, romberg*.js: tabla
        │                            # triangular, convergencia, paso a paso por fila y PDF) y Gauss
        │                            # (Gauss*.vue, gauss*.js: vista, paso a paso, comprobación y PDF). Vistas de resultado, tabla de refinamiento con
        │                            # paso a paso explicado (explain.js, simpsonExplain.js), glosarios
        │                            # (glossary.js, simpsonGlossary.js), tabla de segmentos o de puntos,
        │                            # comprobación (AntiderivativeCheck compartida), PDF (pdf.js exporta
        │                            # pdfTools; simpsonPdf.js) y teoría (theory/, con las respuestas del solver en JSON)
        ├── components/              # ResultsTable, ConvergenceChart, MathFormula, MatrixInput,
        │   │                        # MathSymbolToolbar, MathSyntaxHelp, NavMenu,
        │   │                        # NumericFieldsInput (x0, r0/s0, coeficientes), EquationPreview,
        │   │                        # FunctionTableInput (formulario función/tabla de diferenciación e
        │   │                        # integración), TrapezoidChart (gráfico de una regla de integración),
        │   │                        # GlossaryBlock (glosario plegable), InfoTip (tooltip que se abre
        │   │                        # al tocar), DerivationSteps (desglose término a término con su regla)
        │   └── theory/              # Piezas comunes de las páginas de teoría
        ├── composables/             # useExpressionPreviews (vista previa en vivo),
        │                            # useTheme (tema claro/oscuro, preferencia del sistema y elección guardada)
        └── utils/                   # PDF, formato numérico, fórmulas LaTeX, LaTeX → texto (PDF),
                                     # entrada con fracciones
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

### Agregar una regla de integración (como Simpson; después Romberg y Gauss)

1. **Regla** en `solvers/integration/rules.py`: una `CompositeRule` con
   `factor`, `ends`, `interior` (el patrón de pesos interiores: `(2,)` en el
   trapecio, `(4, 2)` en 1/3, `(3, 3, 2)` en 3/8), `segments_multiple`
   (2: n par; 3: múltiplo de 3), `order`, `bound_derivative`,
   `bound_divisor` y los textos LaTeX (fórmula, cota y, opcionales,
   `error_latex`, `simple_error_latex`, `approx_latex`, `simple_divisor` y
   `piece`). `apply(rule, valores, h)` calcula la regla compuesta.
2. **Solver**, como `simpson.py`: reutiliza de `trapezoid.py` la integral
   exacta o de referencia (`_integral`, con el límite de tiempo de
   `exact.py`), el criterio de la marca R (`_errors`), el formato de `h` y de
   los puntos (`_step`, `_x_display`), la suma ponderada del paso a paso
   (`_first_row_display`, que agrupa los interiores por peso), el máximo de
   una derivada por muestreo (`_second_derivative(…, order=d)`), el desglose
   de las derivadas (`_derivative_steps`) y la comprobación de los datos
   (`_data_checks`). La recurrencia `T_k = T_(k−1)/2 + h·Σ nuevos` es propia
   del trapecio (la base de Romberg); `simpson.py` muestra cómo reutilizar
   las evaluaciones de la fila anterior sin dejar la fórmula de pesos.
3. **Serializer, registro y ejemplos**: una subclase de
   `IntegrationSerializer` (como `SimpsonSerializer`, con sus campos y
   validaciones; `min_points` fija el mínimo de puntos), `registry.py` y
   `examples_data.py`.
4. **Frontend**: en `methods/integration/index.js`, una entrada en
   `methods[slug]` con su `createStore` (`createIntegrationStore({ minPoints })`
   extendido, como `createSimpsonStore`), sus `configFields` y, si su
   resultado cambia de forma, su `resultView`. Se reutilizan
   `IntegrationRefinementTable` (con `block`: filas de una regla y la palabra
   del valor, ver `simpsonWords` en `glossary.js`), `TrapezoidStepDetail`
   (con `customSteps` y `weightReason`), `TrapezoidChart` (con `row.pieces`
   y `partLabels`), `AntiderivativeCheck` (antiderivada, `F' = f` y
   `F(b) − F(a)`), `criterionCheck` y `tinyErrorNote` de `explain.js`, y
   `pdfTools` de `pdf.js` (escritura, glosarios, paso a paso, tabla de puntos
   e integral por otro camino) para el PDF.

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

**510 tests**, todos en verde:

| Archivo | Tests | Qué cubre |
| --- | --- | --- |
| `test_solvers.py` | 23 | Jacobi y Gauss-Seidel, y su comprobación (términos y residuos exactos, solución que se ve entera, coeficiente 0, solución decimal, orden original tras reordenar, no convergencia) |
| `test_dominance.py` | 8 | Dominancia diagonal y reordenamiento de filas |
| `test_api.py` | 13 | Endpoints de los métodos lineales y de ejemplos |
| `test_registry.py` | 13 | Registro de métodos, catálogo (con Gauss después de Romberg) y ejemplos por método |
| `test_expressions.py` | 49 | Parser seguro, derivación y LaTeX |
| `test_preview.py` | 31 | Endpoint de vista previa, logaritmos y límites de seguridad |
| `test_fixed_point.py` | 41 | Punto Fijo: despeje automático, rechazos, actualización secuencial, endpoint y comprobación (soluciones enteras, decimales con funciones, «lado = lado», no convergencia) |
| `test_isolation_steps.py` | 20 | Despeje paso a paso de Punto Fijo |
| `test_newton.py` | 38 | Newton y regla de Cramer: iteraciones calculadas a mano, Jacobiana singular, endpoint y comprobación (tres ejercicios con solución entera, ejemplo decimal, funciones trigonométricas, no convergencia) |
| `test_newton_steps.py` | 16 | Derivadas parciales paso a paso y sustitución en F |
| `test_differentiation.py` | 30 | Diferencias progresiva y regresiva: fórmulas exactas con `x²`, cúbica, Burden y Faires (filas 1, 2 y parada), respuestas guardadas para la teoría iguales a las del solver, filas de parada de los ejemplos, mínimo de 6 filas, no convergencia, razón ≈ 0.5, error real ≤ cota, h exacto, errores 400, modo tabla (secante común, datos, espaciado no uniforme), comprobación término a término, `abs(x)` y endpoint |
| `test_three_point.py` | 27 | Fórmula de 3 puntos: fracciones exactas (cúbica y `x²`), Burden y Faires (filas 1, 2, parada 11 y comparación con diferencias), filas de parada y primeras filas de los ejemplos, cuadrática exacta, razón ≈ 0.25, error real ≤ cota + R, identidades, productos del paso a paso, modo tabla (valores, «—», recomendada, identidades por punto, `x³` con errores iguales a la cota, dato alterado), errores 400 (tabla no uniforme, 2 puntos, dominio en «x₀ − 2h», tolerancia, máximo), respuestas guardadas para la teoría (filas 1 y 2, identidades e iguales a las del solver) y endpoint |
| `test_five_point.py` | 28 | Fórmula de 5 puntos: fracciones exactas (`x⁵` y cuártica), Burden y Faires (filas 1 y 2, parada en 6, comparación, identidad de Richardson y productos del paso a paso), filas de parada de los ejemplos, `x⁵` con error = cota, cuártica exacta, razón ≈ 0.0625, error real ≤ cota + R, `f⁽⁵⁾` término a término, modo tabla (valores, «—», punto medio de 3 puntos, recomendada, identidad por punto con el caso de redondeo de `x = 2.2`, `x⁴` con función, una sola fórmula, 5 datos, dato alterado), errores 400 (tabla no uniforme, 4 puntos, dominio en «x₀ − 4h», tolerancia, máximo) y endpoint |
| `test_trapezoid.py` | 43 | Método del trapecio: fracciones exactas (`x²` en [0, 2] con `Eₜ = Eₐ`, polinomio de Chapra), ejemplo 1 (filas 1 a 3, parada en 13, razón ≈ 0.25, comprobación término a término, paso a paso de la fila 1), recurrencia igual a la fórmula directa (ejemplos 1 y 6, filas 2 a 8, y a mano), filas de parada de los ejemplos, recta exacta, `\|Eₜ\| ≤ cota + R`, `x²` con error = cota, integral exacta o de referencia (erf, `sin`, `1/x`), límite de tiempo (simulado y real), notas de concavidad, modo tabla (uniforme, no uniforme, dato alterado, sin función), singularidad interior, errores 400 y endpoint. Explicaciones: ejemplo 4 fila 1 (sustituciones, suma ponderada, `f'(a)`, `f'(b)`, `f̄''`, `Eₐ`, `M₂`, cota, igualdad sin R) y filas 2 y 3 (puntos nuevos, sumas, `T`), desglose de `f'` y `f''` (`x²`, Chapra, `eˣ`), `M₂` sustituida en Chapra, antiderivada por términos y `F' = f` (`x²`, Chapra, `x·eˣ` sin desglose), nota de `Eₜ` que se ve 0 (ejemplo 6), ninguna R con `\|Eₜ\| ≤ cota·(1 + 10⁻⁹)`, paréntesis de la integral y puntos enviados (1024 o 16). Teoría: filas 1 a 3 del ejemplo 1 y respuestas guardadas iguales a las del solver |
| `test_simpson.py` | 35 | Método de Simpson: fracciones exactas (`x⁴` con 1/3 y 3/8, Chapra con n = 2, 3 y 4), exactitud para cúbicas, ejemplo 1 (filas 1 a 3 de las dos reglas, `Eₐ = Eₜ`, `f̄⁽⁴⁾ = −2400`, `M₄ = 21600` en x = 0, parada en la fila 7, comparación con el trapecio 2.1 y 149.8 veces, identidad `(4T₂ − T₁)/3`, razón ≈ 0.0625, pesos del paso a paso), identidad en fracciones para n = 2, 4 y 8, reutilización de evaluaciones igual a la fórmula de pesos (ejemplos 1 y 6, filas 1 a 8), filas de parada de los ejemplos, `x⁴` con `\|Eₜ\|` = cota sin R, `\|Eₜ\| ≤ cota + R`, notas de concavidad, modo tabla (ejemplos 7 y 8 con pesos, suma, partes y punto de unión; `x⁴` en x = 0..6 con 1556 y 1557; n = 3 sólo 3/8; dato alterado), derivadas `f'''` y `f⁽⁴⁾`, errores 400 (n₀ impar, n₀ no múltiplo de 3, tabla no uniforme con la sugerencia, n impar con 1/3, n no múltiplo de 3 con 3/8, 2 puntos, a ≥ b, `1/x` en a = 0), endpoint y piezas del gráfico. Teoría: fila 1 de las dos reglas del ejemplo 1 y respuestas guardadas iguales a las del solver |
| `test_romberg.py` | 35 | Integración de Romberg: gráfico de segmentos (área de las piezas = `Rᵢ,ₖ` en las columnas 1 a 3 de los ejemplos 1, 2 y 7, valores de control, sólo `n ≤ 64` y columnas ≤ 3, modo tabla); fracciones exactas (Chapra en [0, 4/5] filas 1 a 3; `x⁵` en [0, 2] filas 1 a 4), ejemplo 1 (filas 1 a 3, `R₃,₃` mostrado con 8 decimales por la coherencia, parada en la fila 6 con 33 evaluaciones, error estimado 0.273067 y `εₐ` = 16.644993 % en la fila 3, comparación de costo, tabla de errores), identidades columna 1 = trapecio directo y columna 2 = motor de Simpson (filas 1 a 8 de los ejemplos 1, 2 y 6), filas de parada y diagonales de los ejemplos 2 a 6, advertencia de función poco suave (sólo el ejemplo 5; el 1 es el caso del ruido de redondeo), comparación de costo de los ejemplos 2 a 6 y el texto «más de …», modo tabla (ejemplos 7 y 8 con todas sus celdas, 7 puntos y espaciado no uniforme con 400 y la sugerencia, 3 y 33 puntos, dato alterado), errores 400 (a ≥ b, `1/x` en a = 0, otra variable, máximo de filas fuera de 6..20), singularidad interior y endpoint. Teoría: filas 1 a 3 del ejemplo 1 y respuestas guardadas (ejemplos 1, 2 y 5) iguales a las del solver |
| `test_gauss.py` | 28 | Cuadratura gaussiana: nodos y pesos iguales a las formas exactas (m = 1 a 4, `≤ 10⁻¹⁴`), pesos que suman 2 y nodos simétricos (m = 1 a 20), exactitud para `tᵏ` con `k ≤ 2m − 1` y no con `k = 2m` (m = 1 a 6; 0.24 con m = 3), ejemplo 1 (filas 1 a 3 con G, Eₜ, εₜ y cota; detalle de m = 2; parada en la fila 6; costo 3, 5, 65 y 2049; momentos), ejemplo 4 (Eₜ = cota sin R con m = 3, exacto desde m = 4), filas de parada y valores de los ejemplos 2, 3, 6, 7 y 8, ejemplo 5 (200 sin `f(0)`, nota, no converge, cota no disponible, costo «no aplicable»), compuesta (nodos del ejemplo 7, N = 1 igual a la simple, área de los rectángulos = G y anchos = b − a), `\|Eₜ\| ≤ cota + R` en todas las filas, límite de tiempo de las derivadas (simulado y real), errores 400 (a ≥ b, otra variable, N fuera de 1..50, máximo fuera de 6..20, modo tabla, `1/(x − 0.4)` en el nodo de m = 1) y endpoint. Teoría: m = 2 y m = 3 del ejemplo 1 y respuestas guardadas (ejemplos 1, 2, 4, 5 y 7) iguales a las del solver |
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
- En el método de Simpson, `M₄ = máx |f⁽⁴⁾|` se estima con 2001 puntos (en
  todo `[a, b]` o en cada parte de la combinación), con las mismas
  limitaciones de los límites `a` y `b` y el mismo tope de 2²¹ segmentos que
  el trapecio. La parada exige que todas las reglas pedidas cumplan la
  tolerancia en la misma fila. El modo tabla exige espaciado uniforme
  (`|hᵢ − h₁| ≤ 10⁻⁹·máx(1, |h₁|)`); con datos desiguales hay que usar el
  trapecio (el mensaje lo sugiere; no hay un enlace que cargue los datos en
  su Resolver). Con una regla exacta (cúbicas) y cota 0, un residuo de punto
  flotante en `Eₜ` puede mostrar la marca ✔ᴿ, que es lo que dice el criterio
  de redondeo.
- En la integración de Romberg no hay cota del error (ni marca R): la
  comprobación compara con la integral, revisa las identidades de las
  columnas 1 y 2 y la comparación de costo. Esta última calcula el trapecio
  hasta `n = 2²²` (unos 4 millones de evaluaciones de `f` en el peor caso,
  varios segundos) y obtiene Simpson con `S_n = (4T_n − T_(n/2))/3`, que es
  la misma fórmula que el motor de Simpson salvo el redondeo. En modo tabla
  no hay comparación de costo (no hay `f` que evaluar con más puntos). Los
  límites `a` y `b` tienen las mismas limitaciones que el trapecio.
- En la cuadratura gaussiana, la cota sólo se calcula hasta `m = 5` (necesita
  `f⁽¹⁰⁾`) y `M₂ₘ` se estima con 2001 puntos, extremos incluidos: si `f` no
  está definida en un extremo, la cota no está disponible aunque la integral
  sí se calcule (ejemplos 5 y 6). Las derivadas se calculan en un proceso hijo
  (en Windows su arranque suma unos 2 s la primera vez que se resuelve cada
  función; luego quedan en caché). La comparación de costo calcula el
  trapecio, Simpson y Romberg igual que la de Romberg (hasta `n = 2²²`). Con
  `N = 50` y 20 puntos la respuesta lleva todos los nodos de todas las filas
  (más de 10 000 puntos con su sustitución): es pesada pero funciona.
