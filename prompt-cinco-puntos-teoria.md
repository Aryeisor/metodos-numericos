# Prompt — Fórmula de 5 puntos (sección Teoría)

> Configuración en Claude Code: modelo **Opus 5**, Effort **High**. Sesión nueva (`/clear`). Haz commit del estado actual antes de empezar.

---

Vas a crear la **página de Teoría** del método **«Fórmula de 5 puntos»** (slug `cinco-puntos`, categoría **Diferenciación numérica**). Su Resolver ya está implementado y ajustado: **no cambies el solver ni la vista Resolver**, salvo que la Fase 0 encuentre algo indispensable para la teoría. En ese caso, explícalo en el informe.

Es la **última página de la categoría**. Ya existen las teorías de **«Diferencias progresiva y regresiva»**, que contiene el fundamento común de la categoría, y de **«Fórmula de 3 puntos»**. Esta página:
- **no repite** el fundamento común: lo comparte con el mismo mecanismo que usan las otras dos;
- **cierra la categoría** con una comparación de las tres páginas y un puente hacia la integración numérica.

Todo en español.

## Fase 0 — Inspección obligatoria (antes de cambiar nada)

1. Lee **completa** la página de teoría de 3 puntos, que es la referencia directa: secciones, figura con selector de fórmula, derivaciones, tablas, cómo obtiene los datos reales del solver, cómo comparte el fundamento y referencias. Revisa también la de diferencias y `THEORY_SECTIONS` de la categoría.
2. Revisa cómo quedó el Resolver de 5 puntos:
   - claves de las fórmulas;
   - campos de la respuesta;
   - paso a paso con productos coeficiente·valor;
   - identidad de Richardson y cómo trata el caso de redondeo;
   - línea de comparación con 3 puntos y diferencias;
   - columna «Recomendada» y su regla de preferencia;
   - columna de referencia del punto medio de 3 puntos.

   La teoría debe usar **la misma notación y los mismos componentes**.
3. Revisa qué se dejó en lugar de esta teoría (una página «próximamente» o la entrada oculta) y reemplázalo.

Resume en el informe lo que encontraste.

## Estructura de la página

Usa **el mismo formato y orden** que la teoría de 3 puntos. Las fórmulas van en LaTeX con `MathFormula.vue`. Los números siguen las reglas del proyecto: 6 decimales como máximo, sin ceros finales y sin notación científica, salvo en las tablas de orden de magnitud, donde se indica. **Todos los números de este prompt están verificados con un script.**

### 1. Fundamento común

El de la categoría, compartido y no copiado. Agrega una introducción propia en 3 o 4 líneas:
- La progresiva usa 2 puntos (una recta) y tiene error `O(h)`.
- La fórmula de 3 puntos usa una parábola y tiene error `O(h²)`.
- La fórmula de 5 puntos usa un **polinomio de grado 4** y tiene error `O(h⁴)`.
- Es la opción cuando los datos son precisos y se necesitan muchas cifras correctas sin usar un `h` muy pequeño.

### 2. Definición formal (Burden y Faires)

Las fórmulas van con su error **exacto**.

**Punto medio:**

$$f'(x_0)=\frac{f(x_0-2h)-8f(x_0-h)+8f(x_0+h)-f(x_0+2h)}{12h}+\frac{h^4}{30}f^{(5)}(\xi),\qquad \xi\in(x_0-2h,\,x_0+2h)$$

**Extremo hacia adelante:**

$$f'(x_0)=\frac{-25f(x_0)+48f(x_0+h)-36f(x_0+2h)+16f(x_0+3h)-3f(x_0+4h)}{12h}+\frac{h^4}{5}f^{(5)}(\xi),\qquad \xi\in(x_0,\,x_0+4h)$$

**Extremo hacia atrás:** los mismos coeficientes con el signo cambiado, en `x₀, x₀ − h, …, x₀ − 4h`. Mismo término de error, con `ξ ∈ (x₀ − 4h, x₀)`.

Notas:
- Burden presenta una sola fórmula de extremo y obtiene la de atrás con `h < 0`. En el sistema, `h` siempre es positivo.
- El punto medio usa **5 puntos**, aunque el coeficiente de `f(x₀)` es 0 y no aparece en la fórmula.
- Los coeficientes de cada fórmula suman 0, igual que en las fórmulas anteriores.

### 3. Interpretación geométrica

- La aproximación es la pendiente en `x₀` del **polinomio de grado 4** que pasa por los 5 puntos.
- **Figura SVG**, con el mismo estilo y los mismos controles que la figura de 3 puntos (colores de `theme.css`, tema claro y oscuro):
  - la curva y la tangente exacta;
  - el polinomio de grado 4 con sus 5 puntos;
  - un selector de fórmula (punto medio, extremo hacia adelante, extremo hacia atrás);
  - como referencias tenues, la parábola de 3 puntos y la secante de la progresiva, para que se vea cómo cada polinomio se pega más a la curva.

  Usa un `h` grande en la figura (por ejemplo 0.4) o el deslizador que ya exista. Los valores en vivo se calculan en el frontend y son solo ilustrativos.
- **Signo del error:** con `x·eˣ` (`f⁽⁵⁾ > 0`), las tres fórmulas **subestiman**, porque `D − f'(x₀) ≈ −(h⁴/30)f⁽⁵⁾` y `−(h⁴/5)f⁽⁵⁾`. En el ejemplo: `22.165915 < 22.166312 < 22.166996 < 22.167168`.

  Compara con la de 3 puntos, donde el punto medio sobreestimaba. El signo del término principal cambia de una familia a otra.

### 4. Derivación

#### 4.1 Por extrapolación de Richardson (para el punto medio)

Es la derivación más corta y conecta con las páginas anteriores. Paso a paso:
1. Por la página de 3 puntos, el error del punto medio de 3 puntos solo tiene potencias pares:

   $$D_3(h)=f'(x_0)+\frac{h^2}{6}f'''(x_0)+\frac{h^4}{120}f^{(5)}(x_0)+\cdots$$
2. Con `2h` en lugar de `h`:

   $$D_3(2h)=f'(x_0)+\frac{4h^2}{6}f'''(x_0)+\frac{16h^4}{120}f^{(5)}(x_0)+\cdots$$
3. Se multiplica la primera por 4, se le resta la segunda y se divide entre 3. El término en `h²` se cancela:

   $$\frac{4D_3(h)-D_3(2h)}{3}=f'(x_0)-\frac{h^4}{30}f^{(5)}(x_0)+\cdots$$
4. Al escribir `D₃(h)` y `D₃(2h)` con sus puntos y simplificar, se obtiene la fórmula del punto medio de 5 puntos (muestra el álgebra):

   $$\frac{1}{3}\left[4\cdot\frac{f(x_0+h)-f(x_0-h)}{2h}-\frac{f(x_0+2h)-f(x_0-2h)}{4h}\right]=\frac{f(x_0-2h)-8f(x_0-h)+8f(x_0+h)-f(x_0+2h)}{12h}$$

**Coherencia del coeficiente del error:** `(4·1/120 − 16/120)/3 = (−12/120)/3 = −1/30`. Coincide con el término `+h⁴/30·f⁽⁵⁾` de la definición formal, que está escrito del lado de `f'(x₀)`.

#### 4.2 Por coeficientes indeterminados (para el extremo)

Para el extremo no hay una combinación tan simple. Se usa el método de **coeficientes indeterminados**, una alternativa a derivar el polinomio de Lagrange de grado 4, que es largo:
1. Se busca `D = (c₀f₀ + c₁f₁ + c₂f₂ + c₃f₃ + c₄f₄)/(12h)`, donde `f_j = f(x₀ + j·h)`.
2. Se desarrolla cada `f_j` con Taylor y se exige que el resultado sea `f'(x₀)` exacto para `1, x, x², x³, x⁴`. Eso da 5 ecuaciones:

   $$\sum c_j=0,\quad \sum c_j\,j=12,\quad \sum c_j\,j^2=0,\quad \sum c_j\,j^3=0,\quad \sum c_j\,j^4=0$$
3. La solución es `c = (−25, 48, −36, 16, −3)`. Muestra la verificación de cada ecuación:
   - `−25 + 48 − 36 + 16 − 3 = 0`;
   - `48 − 72 + 48 − 12 = 12`;
   - `48 − 144 + 144 − 48 = 0`;
   - `48 − 288 + 432 − 192 = 0`;
   - `48 − 576 + 1296 − 768 = 0`.
4. El error sale de la siguiente potencia: `Σ c_j j⁵ = 48 − 1152 + 3888 − 3072 = −288`. El término de error es `−288/(12·5!)·h⁴f⁽⁵⁾ = −(h⁴/5)f⁽⁵⁾`.

En una línea: con los puntos `−2, −1, 0, 1, 2` el mismo procedimiento da `(1, −8, 0, 8, −1)` y `Σc_j j⁵ = −48`, de donde sale `−48/1440 = −1/30`. Es el punto medio, y coincide con 4.1.

#### 4.3 Desarrollo del error (tabla, coeficientes verificados)

| Fórmula | `D − f'(x₀)` |
|---|---|
| Punto medio de 3 puntos | `+(h²/6)f''' + (h⁴/120)f⁽⁵⁾ + …` |
| Punto medio de 5 puntos | `−(h⁴/30)f⁽⁵⁾ − (h⁶/252)f⁽⁷⁾ − …` |
| Extremo hacia adelante de 5 puntos | `−(h⁴/5)f⁽⁵⁾ − (h⁵/3)f⁽⁶⁾ − (13h⁶/42)f⁽⁷⁾ − …` |
| Extremo hacia atrás de 5 puntos | `−(h⁴/5)f⁽⁵⁾ + (h⁵/3)f⁽⁶⁾ − (13h⁶/42)f⁽⁷⁾ − …` |

Consecuencias:
- El punto medio solo tiene potencias **pares** (`h⁴`, `h⁶`, …), así que su razón es casi exactamente `0.0625` desde la fila 2.
- Los extremos tienen el término principal **6 veces mayor** (`h⁴/5` frente a `h⁴/30`) y un término en `h⁵`. Por eso su razón se acerca a 0.0625 desde abajo (adelante) y desde arriba (atrás), igual que pasaba en 3 puntos.
- **Exactitud para polinomios:** son exactas para grado ≤ 4. Con `x⁵`, `x₀ = 1` y `h = 0.5`, el punto medio da 4.75 (error 0.25 = `(h⁴/30)·120`) y los extremos dan 3.5 (error 1.5 = `(h⁴/5)·120`). El error coincide exactamente con la cota porque `f⁽⁵⁾ = 120` es constante.

#### 4.4 La escalera de Richardson (puente hacia Romberg)

Muestra esta tabla triangular con datos verificados (`x·eˣ`, `x₀ = 2`). Cada nivel combina dos valores del nivel anterior:

| h | Nivel 1: `D₃(h)`, `O(h²)` | Nivel 2: `(4D₃(h) − D₃(2h))/3`, `O(h⁴)` | Nivel 3: `(16D₅(h) − D₅(2h))/15`, `O(h⁶)` |
|---|---|---|---|
| 0.2 | 22.414161 (error 0.246992) | | |
| 0.1 | 22.228787 (error 0.061619) | 22.166996 (error 0.000173) | |
| 0.05 | 22.182565 (error 0.015397) | 22.167158 (error 0.000011) | 22.167168 (error ≈ 0.00000001) |

Una línea de conclusión:
- Con solo tres valores de la fórmula de 3 puntos se llega a un error del orden de 10⁻⁸.
- Repetir esta escalera es exactamente lo que hace la **integración de Romberg**, aplicada a la regla del trapecio en lugar de a las derivadas. Se verá en la próxima categoría.

El nivel 3 es solo ilustrativo: **no** es parte del Resolver. Indícalo.

### 5. Error y convergencia

- **Cotas** que usa el sistema:

  $$|D_{\text{medio}}-f'(x_0)|\le\frac{h^4}{30}M_5,\qquad |D_{\text{extremo}}-f'(x_0)|\le\frac{h^4}{5}M_5,\qquad M_5=\max|f^{(5)}(x)|$$

  Orden `O(h⁴)`: al dividir `h` entre 2, el error se divide entre aproximadamente **16**.
- **Tabla de convergencia** (`x·eˣ`, `x₀ = 2`, `h₀ = 0.1`; valores verificados). Los errores se muestran como en el Resolver: a 6 decimales, y lo que redondea a 0 se ve `0`. Para que se vea la razón, agrega una columna «error (orden de magnitud)» con potencias de 10.

  | k | h | Punto medio | Error | Razón | Adelante | Error | Razón | Atrás | Error | Razón |
  |---|---|---|---|---|---|---|---|---|---|---|
  | 1 | 0.1 | 22.166996 | 1.73·10⁻⁴ | — | 22.165915 | 1.25·10⁻³ | — | 22.166312 | 8.57·10⁻⁴ | — |
  | 2 | 0.05 | 22.167158 | 1.08·10⁻⁵ | 0.0624 | 22.167097 | 7.12·10⁻⁵ | 0.0567 | 22.167109 | 5.88·10⁻⁵ | 0.0687 |
  | 3 | 0.025 | 22.167168 | 6.74·10⁻⁷ | 0.0625 | 22.167164 | 4.24·10⁻⁶ | 0.0596 | 22.167164 | 3.85·10⁻⁶ | 0.0655 |
  | 4 | 0.0125 | 22.167168 | 4.21·10⁻⁸ | 0.0625 | 22.167168 | 2.59·10⁻⁷ | 0.061 | 22.167168 | 2.47·10⁻⁷ | 0.064 |
  | 5 | 0.00625 | 22.167168 | 2.63·10⁻⁹ | 0.0625 | 22.167168 | 1.6·10⁻⁸ | 0.0618 | 22.167168 | 1.56·10⁻⁸ | 0.0632 |
  | 6 | 0.003125 | 22.167168 | 1.66·10⁻¹⁰ | 0.0629 | 22.167168 | 1·10⁻⁹ | 0.0629 | 22.167168 | 9.84·10⁻¹⁰ | 0.0631 |

  Esta tabla es la **única excepción** a la regla de no usar notación científica en la página, porque los errores son menores que 0.0000005. Indícalo en una nota.

  En la fila 6 la razón se aleja de 0.0625 porque el redondeo ya empieza a influir. Coméntalo en una línea.

  Si el mecanismo de datos reales del solver lo permite, genera la tabla desde la respuesta del solver; los valores deben coincidir.
- **Comparación de toda la categoría** (mismo ejemplo, `h = 0.1`):

  | Fórmula | Puntos | Aproximación | Error real | Veces menor que la progresiva |
  |---|---|---|---|---|
  | Progresiva | 2 | 23.708446 | 1.541278 | 1 |
  | Punto medio de 3 puntos | 3 | 22.228787 | 0.061619 | 25 |
  | Extremo de 5 puntos (adelante) | 5 | 22.165915 | 0.001254 | 1229 |
  | **Punto medio de 5 puntos** | **5** | **22.166996** | **0.000173** | **≈ 8900** |
- **Eficiencia:** el `h` necesario para tener cierto error real en este ejemplo, refinando `h₀ = 0.1` entre 2:

  | Error objetivo | Progresiva | Punto medio de 3 puntos | Punto medio de 5 puntos |
  |---|---|---|---|
  | ≤ 0.0001 | fila 15 (`h ≈ 0.000006`) | fila 6 (`h = 0.003125`) | fila 2 (`h = 0.05`) |
  | ≤ 0.000001 | fila 22 (`h ≈ 0.00000005`) | fila 9 (`h = 0.000390625`) | fila 3 (`h = 0.025`) |

  Por aproximación, la de 5 puntos evalúa `f` en 4 puntos, contra 2 de las otras. A cambio, trabaja con un `h` cientos o miles de veces mayor, lo que la aleja del problema de redondeo.
- **Redondeo y `h` óptimo:** el error total del punto medio es aproximadamente

  $$E(h)\approx\frac{h^4}{30}M_5+\frac{3\varepsilon|f(x_0)|}{2h}$$

  Su mínimo está en

  $$h^{*}=\left(\frac{45\,\varepsilon|f(x_0)|}{4M_5}\right)^{1/5}$$

  En el ejemplo, `h* ≈ 0.0009`. Muestra la tabla del **orden de magnitud** del error real con las tres fórmulas, escrita con potencias de 10:

  | h | 10⁻¹ | 10⁻² | 10⁻³ | 10⁻⁴ | 10⁻⁵ | 10⁻⁶ | 10⁻⁸ | 10⁻¹⁰ |
  |---|---|---|---|---|---|---|---|---|
  | Progresiva | 10⁰ | 10⁻¹ | 10⁻² | 10⁻³ | 10⁻⁴ | 10⁻⁵ | 10⁻⁷ | 10⁻⁶ |
  | Punto medio de 3 puntos | 10⁻² | 10⁻⁴ | 10⁻⁶ | 10⁻⁸ | 10⁻¹⁰ | 10⁻¹⁰ | 10⁻⁷ | 10⁻⁶ |
  | Punto medio de 5 puntos | 10⁻⁴ | 10⁻⁸ | 10⁻¹² | 10⁻¹¹ | 10⁻¹⁰ | 10⁻¹⁰ | 10⁻⁷ | 10⁻⁵ |

  Conclusión en una línea: cuanto mayor es el orden de la fórmula, menor es el error mínimo alcanzable (10⁻⁷, 10⁻¹⁰ y 10⁻¹²) y mayor es el `h` donde se logra. Con `h` muy pequeño, todas terminan dominadas por el redondeo.

  Si las páginas anteriores tienen el gráfico log-log de la «V», agrega aquí el mismo gráfico con las **tres** curvas.

### 6. Restricciones y precauciones

En tarjetas, con el mismo estilo de la página de 3 puntos:
1. **Para que la cota valga, `f` debe tener quinta derivada continua** en el intervalo que usa la fórmula. Si `f` no es tan suave, la fórmula de 5 puntos puede no mejorar a la de 3 puntos.
2. **Todos los puntos deben estar en el dominio de `f`.** El extremo llega hasta `x₀ ± 4h`. Por ejemplo, `ln x` con `x₀ = 0.35`, `h = 0.1` y el extremo hacia atrás necesita `ln(−0.05)`. Es el mismo caso que rechaza el Resolver.
3. **Más datos:** se necesitan dos datos a cada lado para el punto medio y cuatro a un lado para el extremo. Una tabla debe tener al menos 5 datos, con espaciado uniforme.
4. **Qué fórmula usar en una tabla** (la regla de la columna «Recomendada»):
   - el punto medio de 5 puntos donde existe;
   - si no, el extremo de 5 puntos;
   - el punto medio de 3 puntos solo cuando no hay ninguna de 5. Por ejemplo, en el segundo punto de una tabla de 5 datos.

   Ejemplo verificado: en `x = 1.7` de la tabla de 9 datos, el extremo de 5 puntos tiene error 0.000906 y el punto medio de 3 puntos, 0.042907.
5. **Datos con ruido:** con un error de hasta `δ` en cada dato, el punto medio lo amplifica hasta `(1+8+8+1)δ/(12h) = 1.5δ/h` y el extremo hasta `(25+48+36+16+3)δ/(12h) ≈ 10.67δ/h`.
   - Con `δ = 0.001` y `h = 0.01`, hasta 0.15 en el punto medio y 1.07 en el extremo.
   - El extremo de 5 puntos es la fórmula de la categoría **más sensible al ruido**: con datos medidos con poca precisión, una fórmula de menor orden puede dar mejor resultado.
   - Ejemplo real: la tabla del libro (redondeada a 6 decimales) da 22.166999 en `x = 2`, frente a 22.166996 con la función exacta. El redondeo de los datos ya cambia el sexto decimal (diferencia de unos 0.000003). Con `h = 0.1` todavía es pequeño frente al error de truncamiento (0.000173), pero con un `h` más pequeño pasaría a dominar.
6. **`h` ni muy grande ni muy pequeño**, y con esta fórmula el redondeo aparece antes (ver la sección 5).
7. **Funciones trigonométricas en radianes.**

### 7. Algoritmo (en tarjetas)

Refleja lo que hace el Resolver, con el mismo formato que la página de 3 puntos:
1. **Datos.**
2. **Puntos:**
   - punto medio: `x₀ ± h` y `x₀ ± 2h`;
   - extremos: `x₀, x₀ ± h, …, x₀ ± 4h`.
3. **Evaluar** `f` en los puntos.
4. **Combinar:** calcular los productos coeficiente·valor, sumarlos y dividir entre `12h`.
5. **Errores:**
   - error estimado;
   - error real;
   - cota `(h⁴/30)·M₅` o `(h⁴/5)·M₅`.
6. **Refinar:** `h ← h/2` y repetir desde el paso 2.
7. **Parar:** con el error estimado `≤ tolerancia` y al menos 6 filas, o al llegar al máximo.
8. **Comprobar:**
   - sustituir `x₀` en `f'(x)`;
   - verificar que error real `≤ cota`;
   - verificar la identidad de Richardson (solo en el punto medio);
   - comparar con 3 puntos y con diferencias.

En una línea: modo tabla, con espaciado uniforme, la regla de la columna recomendada y la columna de referencia de 3 puntos.

### 8. Ejemplo resuelto (datos reales del solver)

**Ejemplo 1 del Resolver (Burden y Faires):** `f(x) = x·eˣ`, `x₀ = 2`, `h₀ = 0.1`, «Todas». La derivada exacta es `f'(2) = 22.167168` y `f⁽⁵⁾(x) = (5 + x)eˣ`.

**Fila 1, detallada** con los mismos componentes del paso a paso del Resolver (productos y colores):
- Evaluaciones:

  | x | 1.6 | 1.7 | 1.8 | 1.9 | 2.0 | 2.1 | 2.2 | 2.3 | 2.4 |
  |---|---|---|---|---|---|---|---|---|---|
  | f(x) | 7.924852 | 9.305711 | 10.889365 | 12.703199 | 14.778112 | 17.148957 | 19.85503 | 22.94062 | 26.455623 |

- **Punto medio:** `(10.889365 − 8(12.703199) + 8(17.148957) − 19.85503)/1.2 = 22.166996`. Error real 0.000173, cota 0.000217 ✔.
- **Extremo hacia adelante** (`x = 2.0` a `2.4`): 22.165915. Error real 0.001254, cota 0.001631 ✔.
- **Extremo hacia atrás** (`x = 1.6` a `2.0`): 22.166312. Error real 0.000857, cota 0.001034 ✔.
- **Identidad de Richardson:** `D₃(0.1) = 22.228787`, `D₃(0.2) = 22.414161` y `(4(22.228787) − 22.414161)/3 = 22.166996` ✔.

Los productos, sumas y decimales intermedios deben ser **exactamente** los que devuelve el solver, con su regla de decimales.

**Resto:**
- **Fila 2:** 22.167158, 22.167097 y 22.167109.
- La parada en la fila 6.
- La línea de comparación con 3 puntos y diferencias.
- Un botón o enlace «Resolver este ejemplo», si las otras páginas lo tienen.

**Mini-ejemplo de datos:** el ejemplo 7 del Resolver (9 datos de `x·eˣ` entre 1.6 y 2.4). Muestra la tabla con las columnas del Resolver:
- punto medio de 5 puntos;
- extremo hacia adelante;
- extremo hacia atrás;
- punto medio de 3 puntos;
- recomendada;
- exacta.

Destaca estos puntos:
- en `x = 2.0` da 22.166999, el valor del libro;
- en `x = 1.7`, la recomendada es el extremo de 5 puntos;
- en `x = 2.2` está el caso de redondeo de la identidad, si el Resolver lo muestra con una nota.

Toma los datos del solver.

### 9. Tabla comparativa (cierre de la categoría)

| Aspecto | Progresiva / Regresiva | Punto medio de 3 puntos | Extremo de 3 puntos | Punto medio de 5 puntos | Extremo de 5 puntos |
|---|---|---|---|---|---|
| Puntos | 2 | 3 (`f(x₀)` con coeficiente 0) | 3 | 5 (`f(x₀)` con coeficiente 0) | 5 |
| Denominador | `h` | `2h` | `2h` | `12h` | `12h` |
| Orden del error | `O(h)` | `O(h²)` | `O(h²)` | `O(h⁴)` | `O(h⁴)` |
| Término principal del error | `±(h/2)f''` | `+(h²/6)f'''` | `−(h²/3)f'''` | `−(h⁴/30)f⁽⁵⁾` | `−(h⁴/5)f⁽⁵⁾` |
| Exacta para grado | ≤ 1 | ≤ 2 | ≤ 2 | ≤ 4 | ≤ 4 |
| Razón al dividir `h` entre 2 | ≈ 0.5 | ≈ 0.25 | ≈ 0.25 | ≈ 0.0625 | ≈ 0.0625 |
| Amplificación del ruido | `2δ/h` | `δ/h` | `4δ/h` | `1.5δ/h` | `≈ 10.67δ/h` |
| Error en el ejemplo (`h = 0.1`) | 1.541278 / 1.418041 | 0.061619 | 0.134863 / 0.112647 | 0.000173 | 0.001254 / 0.000857 |
| Se obtiene por Richardson de | — | promedio de progresiva y regresiva | `2D⁺(h) − D⁺(2h)` | `(4D₃(h) − D₃(2h))/3` | coeficientes indeterminados |

**Cómo elegir**, en 3 viñetas:
- Datos precisos y se necesita mucha exactitud: 5 puntos.
- Datos con ruido moderado o pocos puntos: 3 puntos (punto medio).
- Solo hay valores a un lado, o el cálculo es rápido y sencillo (por ejemplo, el método de Euler): progresiva o regresiva.

**Puente hacia la integración**, en 2 o 3 líneas:
- La diferenciación numérica **amplifica** el ruido de los datos; la integración lo **suaviza**.
- La misma herramienta (interpolar con polinomios y combinar resultados con Richardson) aparecerá en el trapecio, en Simpson y en Romberg.

### 10. Referencias (APA, con las mismas ediciones que las otras páginas de la categoría)

- Burden, R. L., Faires, J. D., & Burden, A. M. (2017). *Análisis numérico* (10.ª ed.). Cengage Learning. (Sección 4.1, Diferenciación numérica, y Sección 4.2, Extrapolación de Richardson.)
- Chapra, S. C., & Canale, R. P. (2015). *Métodos numéricos para ingenieros* (7.ª ed.). McGraw-Hill Education.
- Mathews, J. H., & Fink, K. D. (2000). *Métodos numéricos con MATLAB* (3.ª ed.). Prentice Hall.

Si las otras páginas usan otras ediciones o más referencias, usa **las mismas** y explícalo en el informe.

## Requisitos generales

- **Modo oscuro:** todos los colores salen de `theme.css`, también los de las figuras.
- **Menú:** la página aparece en «Teoría ▾» bajo «Diferenciación numérica», después de 3 puntos.
- **Responsive:** se ve bien a 390 px de ancho, sin desplazamiento horizontal de la página. Las tablas anchas (convergencia, comparativa de 6 columnas, escalera de Richardson) se desplazan dentro de su contenedor.
- **Consola:** sin errores en el navegador.
- **README:** en «Vista Teoría», el número de páginas (ya son ocho) y la viñeta de la categoría con lo que agrega esta página: Richardson, coeficientes indeterminados, la escalera hacia Romberg y la comparación de la categoría.
- **Tests:** si la página usa datos del backend, agrega un test con las filas 1 y 2 del ejemplo 1 y la identidad. Los tests existentes deben seguir en verde.

## Verificación

1. `python manage.py test numeric_methods`: todo en verde. Reporta el total.
2. `npm run build` sin errores.
3. **Playwright en modo desarrollo:**
   - recorrer todas las secciones;
   - comprobar que los números del ejemplo coincidan con el Resolver (filas 1, 2 y 6, e identidad);
   - probar el selector de fórmula de la figura;
   - capturas completas en claro, en oscuro y a 390 px.
4. **Regresión:** las páginas de teoría de diferencias y de 3 puntos se ven igual que antes, incluido el fundamento compartido.
5. **Docker:** `docker compose up -d --build`, y revisar la página en `http://localhost:8080`.
6. Las páginas de teoría de los otros métodos siguen funcionando.

## Informe final (en español)

- Resumen de la Fase 0.
- Archivos creados y modificados.
- Lista de secciones, con una línea de qué contiene cada una.
- Valores del ejemplo en la página frente a los de este prompt.
- Tests antes y después.
- Capturas y resultado en desarrollo y en Docker.
- Diferencias con esta especificación y por qué.

**No hagas commit.**
