# Apartado «Comprobación» en Newton

Responde siempre en español.

Jacobi, Gauss-Seidel, Punto Fijo y Bairstow ya tienen la sección **«Comprobación»**. Falta **Newton**. Hay que agregarla con **exactamente el mismo comportamiento y estilo que la de Punto Fijo**: reemplazar la solución en cada ecuación original fᵢ = 0 y mostrar que da 0.

**No cambies** la lógica del solver, la Jacobiana, Cramer, el criterio de parada, los ejemplos ni la Teoría.

La aplicación se ejecuta con **Docker** (http://localhost:8080). Los cambios solo se ven ahí después de reconstruir las imágenes. El modo desarrollo también debe seguir funcionando.

---

## Fase 0 — Inspección obligatoria

Lee y resume cómo está hecha la comprobación de **Punto Fijo**, porque Newton debe reutilizarla:

- backend: cómo `fixed_point.py` arma `verification` (términos de fᵢ, sustitución, criterio de entero, criterio de «≈ 0», residuo máximo, bandera de funciones trigonométricas);
- frontend: `methods/nonlinear/verification.js`, `NonlinearVerification.vue` y `methods/nonlinear/index.js` (según el informe anterior, la sección está **desactivada para Newton** ahí);
- `methods/nonlinear/pdf.js` (sección «Comprobación» del PDF);
- `solvers/nonlinear/newton.py`: qué guarda de cada fᵢ y de sus términos.

Si la lógica de la comprobación está dentro de `fixed_point.py`, **muévela a un módulo compartido** de la categoría no lineal (por ejemplo, `solvers/nonlinear/verification.py`) y úsala desde los dos métodos. No dupliques código. Punto Fijo debe seguir dando exactamente lo mismo.

Si algo del código real contradice este prompt de forma importante, detente y repórtalo.

---

## 1. Qué debe hacer

Las mismas reglas de Punto Fijo, sin excepciones:

- **Ubicación:** al final del resultado de Newton, después de la tabla de iteraciones y el paso a paso.
- **Línea fija:** «Se reemplaza la solución en cada ecuación original, escrita como f(x) = 0; el resultado debe dar 0.»
- **Solución usada** antes de las ecuaciones, en el **orden de las variables declarado** por el usuario.
- **Por ecuación:** fᵢ = 0, la sustitución término a término, el valor de cada término, el resultado y la marca.
- **Enteros sin decimales:** si un valor está a distancia despreciable de un entero (el mismo criterio de Punto Fijo), se muestra y se sustituye como entero: `x = 3, y = 3` y `(3)² − (3)(3) + 2(3) + 2(3) − 12 = 9 − 9 + 6 + 6 − 12 = 0 ✔`. Nunca `3.000000`.
- **Valores negativos entre paréntesis**, coeficiente 1 omitido, signos ya resueltos.
- **Sin notación científica** en ningún número (errores, residuos, términos): 6 decimales como máximo; los que redondean a 0 se muestran `0` y no se agrega nota de residuo.
- **Soluciones no enteras:** «≈ 0 ✔» o «⚠» con los mismos criterios de Punto Fijo.
- **Funciones trigonométricas:** la misma nota de radianes.
- **No convergió:** el mismo aviso de «última aproximación calculada».
- **Línea final** «Residuo máximo: …».
- **PDF:** la misma sección, con la misma convención de texto, en tema claro.
- **Modo claro y oscuro:** las mismas variables de `theme.css`.
- El botón **«Limpiar»** también borra la comprobación.

---

## 2. Tests

En `tests/test_newton.py`, con tolerancia 0.000001:

1. **Variables x, y.** `y^2 - x*y + 2*x + 2*y - 12 = 0`, `y^2 + x*y - y - 15 = 0`, x⁽⁰⁾ = (2, 2). Solución (3, 3) tratada como entera; los términos de f₁ son 9, −9, 6, 6, −12 y los de f₂ son 9, 9, −3, −15 (sin importar el orden); resultados 0.
2. **Variables x, y.** `x^2 + x*y - 2*x - y + 1 = 0`, `2*x^2 - 2*x + y + 1 = 0`, x⁽⁰⁾ = (0, 0). Solución (1, −1) entera; términos de f₁: 1, −1, −2, 1, 1; de f₂: 2, −2, −1, 1; resultados 0.
3. **Variables x, y.** `x^2 - x*y - 3*y + 7 = 0`, `y^2 - x*y + 3*x - 2*y - 1 = 0`, x⁽⁰⁾ = (2, 1). Solución (1, 2) entera; resultados 0.
4. Un ejemplo precargado de Newton con solución **no entera**: residuos ≈ 0 y marcados como tales.
5. Un caso que **no converge** (máximo de iteraciones bajo o Jacobiana singular): la comprobación existe con la última aproximación y su residuo máximo no es ≈ 0.
6. Los tests de comprobación de **Punto Fijo** siguen pasando sin cambios.

De paso, verifica que en los casos 1, 2 y 3 las iteraciones coinciden con estos valores (son ejercicios resueltos a mano por el usuario):

| Caso | Iteraciones (x, y) | Errores |
|---|---|---|
| 1 | (4, 3), (3, 3), (3, 3) | 2, 1, 0 |
| 2 | (0.5, 0), (1, −0.5), (1, −1), (1, −1) | 0.5, 0.5, 0.5, 0 |
| 3 | (2.5, 2.5), (0.5, 1.5), (1, 2), (1, 2) | 1.5, 2, 0.5, 0 |

Si no coinciden, **no cambies el solver**: repórtalo en el informe con los valores que da la app.

`python manage.py test numeric_methods`: todos los tests en verde.

---

## 3. README

En «Detalle de cada método → Newton», agrega el apartado «Comprobación». En la API, el nuevo campo de la respuesta de Newton. Actualiza el conteo de tests.

---

## 4. Verificación

1. `python manage.py test numeric_methods` en verde y `npm run build` sin errores.
2. En el navegador (Playwright), en tema claro y oscuro: los casos 1, 2 y 3 muestran la comprobación con enteros; un ejemplo precargado con decimales muestra «≈ 0 ✔»; el PDF de Newton incluye la sección; Punto Fijo se ve igual que antes.
3. **Docker:** `docker compose up -d --build`, esperar a que el backend esté `healthy` y comprobar el caso 3 en http://localhost:8080. Si Docker no está disponible, deja los comandos.

---

## Informe final

En español: archivos creados y modificados, qué se movió a un módulo compartido, texto de la comprobación del caso 3, si las iteraciones de la tabla coinciden, resultado de tests, build y verificación en Docker. No hagas commit.
