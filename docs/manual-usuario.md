# Manual de usuario 

# Sistema de Métodos Numéricos Iterativos

**Guía completa para usar la aplicación web**

|  |  |
|---|---|
| **Sistema** | Métodos Numéricos Iterativos (aplicación web) |
| **Repositorio** | https://github.com/Aryeisor/metodos-numericos |
| **Autores** | _[completar]_ |
| **Asignatura** | _[completar]_ |
| **Docente** | _[completar]_ |
| **Institución** | _[completar]_ |
| **Versión del documento** | 1.2 |
| **Fecha** | 16 de noviembre de 2026 |
| **Estado del código documentado** | rama `main`, commit `9aff3ae` |

# Control de versiones del documento

| Versión | Fecha | Autor | Cambios |
|---|---|---|---|
| 1.0 | 13 de noviembre de 2026 | _[completar]_ | Versión inicial |
| 1.1 | 16 de noviembre de 2026 | _[completar]_ | Nueva vista del resultado (tarjeta de respuesta, franja fija y botones «Descargar PDF» y «Limpiar»), botón «Manual de usuario» en la barra superior y figuras tomadas con el navegador en español |
| 1.2 | 16 de noviembre de 2026 | _[completar]_ | Marca del sistema en la barra superior y en la pestaña, título propio de la pestaña en cada página, aviso «Resolviendo…» en los cálculos largos, página «Esta página no existe» para las direcciones desconocidas y nuevo pie de página; figuras de la barra superior y del menú rehechas |

# 1. Antes de empezar

## 1.1 Para quién es este manual y qué vas a poder hacer con él

Este manual está escrito para ti si vas a usar el sistema por primera vez, aunque no sepas programar y aunque no recuerdes bien los métodos numéricos que viste en clase. Con él vas a poder encender el sistema en tu computador, encontrar el método que necesitas, llenar el formulario sin equivocarte, entender cada número, tabla y gráfica que aparece en pantalla, guardar el resultado en un archivo PDF y salir del paso cuando algo no funcione como esperabas. No necesitas leerlo de corrido: si es tu primera vez, lee los capítulos 2 a 5 en orden; después, usa el resto como consulta.

## 1.2 Qué resuelve el sistema

El sistema resuelve, paso a paso, cinco familias de problemas. En todas ellas el computador no encuentra la respuesta de un solo golpe, sino que la va acercando poco a poco y te muestra cada intento.

**Sistemas de ecuaciones lineales.** Son varias ecuaciones en las que las incógnitas aparecen solo multiplicadas por números, sin potencias ni funciones. El sistema las resuelve con los métodos de Jacobi y de Gauss-Seidel. Aparecen, por ejemplo, cuando se reparte una corriente eléctrica entre varios cables de un circuito, o cuando se calculan las fuerzas en las barras de una estructura.

**Sistemas de ecuaciones no lineales.** Son varias ecuaciones en las que las incógnitas aparecen elevadas a potencias, multiplicadas entre sí o dentro de funciones como el seno o la exponencial. El sistema las resuelve con los métodos de Punto Fijo y de Newton. Aparecen, por ejemplo, cuando se busca el punto en que dos trayectorias curvas se cruzan, o el equilibrio de una reacción química.

**Raíces de polinomios.** Un polinomio es una expresión como $x^3 - 6x^2 + 11x - 6$, y sus raíces son los valores de $x$ que lo hacen valer cero. El sistema encuentra todas las raíces, incluidas las complejas, con el método de Bairstow. Aparecen, por ejemplo, al estudiar las frecuencias a las que vibra un puente o la estabilidad de un sistema de control.

**Diferenciación numérica.** Consiste en calcular la derivada, es decir, la rapidez con que cambia una cantidad, a partir de una función o de una tabla de datos medidos. El sistema usa las diferencias progresiva y regresiva y las fórmulas de 3 y de 5 puntos. Aparece, por ejemplo, cuando tienes las posiciones de un carro medidas cada décima de segundo y quieres saber su velocidad en un instante.

**Integración numérica.** Consiste en calcular el área bajo una curva entre dos valores. El sistema usa el método del trapecio, el método de Simpson, la integración de Romberg y la cuadratura gaussiana. Aparece, por ejemplo, cuando quieres saber la distancia total recorrida a partir de la velocidad, o el volumen de agua que pasó por un canal a partir del caudal medido.

## 1.3 Qué necesitas

**Un computador** con Windows 10 o 11 (el sistema también funciona en Linux y macOS, pero este manual describe Windows). Conviene que tenga al menos 8 GB de memoria RAM, porque el programa que mantiene el sistema encendido (Docker Desktop) pide unos 4 GB para él solo; la aplicación en sí ocupa menos de 300 MB de memoria mientras está encendida. Deja libres al menos 3 GB de disco: la aplicación construida ocupa unos 450 MB, y la primera construcción descarga y guarda archivos intermedios.

**Un navegador** (el programa con el que abres páginas web) actualizado: Google Chrome, Microsoft Edge o Mozilla Firefox. Las capturas de este manual se tomaron con un navegador de la familia Chrome.

**Docker Desktop instalado.** Docker es un programa que permite ejecutar aplicaciones dentro de «contenedores», que son como cajas cerradas que traen dentro todo lo que la aplicación necesita para funcionar. Gracias a Docker no tienes que instalar nada más. Si no lo tienes, descárgalo desde la página oficial de Docker e instálalo con las opciones que te proponga; en Windows te pedirá activar una función llamada WSL 2, acéptala.

**Lo que no necesitas.** No tienes que instalar Python ni Node (los lenguajes con los que está hecho el sistema), no tienes que crear ninguna cuenta ni iniciar sesión, y no necesitas internet para usarlo: solo hace falta conexión la primera vez que lo enciendes, porque en ese momento Docker descarga los componentes. A partir de ahí funciona sin conexión.

## 1.4 Cómo está organizado este manual

El capítulo 2 te enseña a encender y apagar el sistema. Los capítulos 3 y 4 te muestran la pantalla y cómo moverte por ella. El capítulo 5 es un ejercicio completo, guiado de principio a fin; si solo vas a leer un capítulo, lee ese. El capítulo 6 explica cómo llenar el formulario de cada tipo de método, el 7 cómo leer el resultado, el 8 qué hay en las páginas de teoría y el 9 cómo cambiar entre modo claro y oscuro. El capítulo 10 reúne los problemas que pueden aparecer y cómo resolverlos, el 11 responde las preguntas más frecuentes y el 12 es un glosario de términos. Al final hay dos anexos: el índice de figuras y una tabla para elegir el método adecuado.

En todo el manual vas a encontrar estas convenciones:

- Los textos que aparecen en la pantalla (botones, títulos, etiquetas de los campos) se escriben entre comillas angulares, tal como se ven: por ejemplo, el botón «Resolver».
- Lo que tienes que escribir exactamente igual en el teclado aparece en letra de máquina de escribir, por ejemplo `x^2 + 3*x`.
- Las **notas** dan un dato útil que no es imprescindible. Los **avisos** advierten de algo que puede hacerte perder datos o tiempo; léelos siempre.
- Las capturas de pantalla están numeradas como figuras (Figura 1, Figura 2, …) en el orden en que aparecen, y el texto se refiere a ellas por ese número. Al final del manual, el Anexo A las lista todas.

# 2. Encender y apagar el sistema

## 2.1 Encenderlo

Sigue estos pasos cada vez que quieras usar el sistema.

1. **Abre Docker Desktop.** Búscalo en el menú Inicio de Windows y ábrelo. Espera a que en su ventana aparezca el mensaje «Engine running» (motor funcionando), que suele estar en la esquina inferior izquierda. Puede tardar uno o dos minutos después de encender el computador. Mientras no aparezca, el sistema no puede arrancar.
2. **Abre la carpeta del proyecto** en el Explorador de archivos de Windows. Dentro vas a ver, entre otras cosas, tres archivos que se abren con doble clic: `iniciar.bat`, `detener.bat` y `reconstruir.bat`, como en la Figura 1. Son los únicos que necesitas tocar.

> **CAPTURA U-01 — Carpeta del proyecto**
>
> - **Archivo:** `docs/img/usuario/U-01-carpeta-del-proyecto.png`
> - **Qué debe verse:** la ventana del Explorador de archivos de Windows abierta en la carpeta raíz del proyecto, con las carpetas `backend`, `docs` y `frontend` y los archivos `iniciar.bat`, `detener.bat`, `reconstruir.bat`, `docker-compose.yml` y `README.md` a la vista.
> - **Cómo llegar:** abrir el Explorador de archivos, entrar en la carpeta donde se descargó o copió el proyecto y elegir la vista «Detalles» para que se lean bien los nombres.
> - **Qué resaltar:** los tres archivos `.bat`, con un recuadro o una flecha sobre `iniciar.bat`.
> - **Recorte sugerido:** solo la ventana del Explorador, sin la barra de tareas ni el escritorio; que la lista de archivos se lea completa y sin barras de desplazamiento.

![Figura 1 — La carpeta del proyecto, con los archivos de doble clic para iniciar, detener y reconstruir](img/usuario/U-01-carpeta-del-proyecto.png)

3. **Haz doble clic en `iniciar.bat`.** Se abre una ventana negra con el título «Metodos Numericos - Iniciar» y el mensaje «Iniciando la aplicacion (la primera vez tarda varios minutos)...».
4. **Espera.** La primera vez que lo hagas, el sistema se construye desde cero: Docker descarga los componentes de internet, los instala y prepara la aplicación. Eso puede tardar entre cinco y quince minutos, según tu conexión y tu computador, y vas a ver pasar muchas líneas de texto. No cierres la ventana. Las veces siguientes ya no hay nada que construir y el arranque toma pocos segundos.
5. **Comprueba que terminó.** Cuando el sistema está listo, la ventana muestra el mensaje «Lista en http://localhost:8080», como en la Figura 2, y unos segundos después se cierra sola. Al mismo tiempo se abre tu navegador en esa dirección.

> **CAPTURA U-02 — Ventana de iniciar.bat al terminar**
>
> - **Archivo:** `docs/img/usuario/U-02-ventana-iniciar.png`
> - **Qué debe verse:** la ventana negra de la consola con el título «Metodos Numericos - Iniciar», la línea «Iniciando la aplicacion (la primera vez tarda varios minutos)...», las líneas de Docker que indican que los contenedores `metodos-backend-1` y `metodos-frontend-1` quedaron «Healthy» o «Started», y al final la línea «Lista en http://localhost:8080».
> - **Cómo llegar:** con Docker Desktop abierto y en «Engine running», hacer doble clic en `iniciar.bat` y tomar la captura justo cuando aparece «Lista en http://localhost:8080» (la ventana se cierra sola a los tres segundos; si no alcanzas, usa la tecla Impr Pant apenas aparezca el mensaje).
> - **Qué resaltar:** la última línea, «Lista en http://localhost:8080».
> - **Recorte sugerido:** solo la ventana de la consola, con su barra de título; sin el escritorio alrededor.

![Figura 2 — La ventana de iniciar.bat cuando el sistema ya está listo](img/usuario/U-02-ventana-iniciar.png)

6. **Usa el navegador.** Si el navegador no se abrió solo, ábrelo tú y escribe en la barra de direcciones `http://localhost:8080` y pulsa Enter. «localhost» es el nombre con el que tu computador se llama a sí mismo, y 8080 es la «puerta» (el puerto) por la que atiende el sistema. Vas a ver la pantalla de la Figura 3: el sistema abre directamente el método de Jacobi, listo para trabajar. Arriba de todo, la página dice en qué método estás: la categoría en letras pequeñas («SISTEMAS LINEALES»), el nombre del método en grande («Jacobi») y una línea que explica qué hace.

![Figura 3 — El sistema recién abierto en el navegador](img/usuario/U-03-aplicacion-abierta.png)

> **Nota.** Si no apagaste el sistema con `detener.bat` la última vez, vuelve a encenderse solo cuando abres Docker Desktop. En ese caso basta con abrir el navegador en `http://localhost:8080`.

## 2.2 Apagarlo

Cuando termines, cierra la pestaña del navegador y haz doble clic en `detener.bat`. Se abre una ventana negra con el título «Metodos Numericos - Detener» que apaga los dos contenedores del sistema y se cierra sola a los pocos segundos. Si después quieres, puedes cerrar también Docker Desktop.

Conviene apagarlo porque, mientras está encendido, el sistema y sobre todo Docker Desktop ocupan memoria del computador aunque no los estés usando, y eso puede volver más lentos los demás programas. Apagarlo no borra nada: la próxima vez que lo enciendas estará igual, y como el sistema no guarda tus ejercicios (ver el capítulo 11), no hay nada que se pierda.

## 2.3 Si algo falla al encender

**Docker Desktop no está abierto.** *Cómo se ve:* al hacer doble clic en `iniciar.bat`, la ventana negra muestra «Docker Desktop no esta iniciado.» y debajo «Abrelo, espera a que diga "Engine running" y vuelve a ejecutar este archivo.», y se queda esperando a que pulses una tecla. *Por qué pasa:* el sistema vive dentro de Docker, y si Docker no está funcionando no hay dónde encenderlo. También pasa si Docker Desktop está abierto pero todavía arrancando. *Qué hacer:* pulsa una tecla para cerrar la ventana, abre Docker Desktop, espera a que diga «Engine running» y vuelve a hacer doble clic en `iniciar.bat`.

**El puerto ya está ocupado por otro programa.** *Cómo se ve:* la ventana negra muestra un error en inglés que contiene «port is already allocated» o «address already in use», seguido de «La aplicacion no pudo iniciarse.». *Por qué pasa:* otro programa de tu computador ya está usando la puerta 8080 (algunos servidores de prueba, otros proyectos con Docker o programas de bases de datos lo hacen). Dos programas no pueden atender por la misma puerta. *Qué hacer:* cierra el otro programa (si es otro proyecto de Docker, apágalo desde Docker Desktop) y vuelve a ejecutar `iniciar.bat`. Si no sabes cuál es o no puedes cerrarlo, pide a quien mantiene el sistema que cambie el puerto; el manual técnico explica cómo.

**La página carga en blanco o da un error de servidor.** *Cómo se ve:* el navegador muestra «No se puede acceder a este sitio» o una página en blanco; o la página carga, pero en vez del formulario aparece el recuadro rojo «No fue posible cargar los métodos desde el servidor. Verifica que el backend esté corriendo.»; o `iniciar.bat` termina con «La aplicacion no pudo iniciarse. Revisa los logs con: docker compose logs backend». *Por qué pasa:* el sistema tiene dos partes, la página que ves (en el contenedor llamado `frontend`) y el servidor que hace los cálculos (en el contenedor llamado `backend`). Si abriste el navegador antes de que el servidor terminara de arrancar, o si el servidor se detuvo, la página no tiene de dónde sacar los métodos. *Qué hacer:* espera un minuto y recarga la página con la tecla F5. Si sigue igual, abre Docker Desktop, entra en la sección «Containers» y revisa que el grupo `metodos` tenga sus dos contenedores en verde; si alguno está detenido, ejecuta `detener.bat` y después `iniciar.bat`. Si el problema persiste, copia el texto de la ventana negra y entrégaselo a quien mantiene el sistema.

## 2.4 Para quien desarrolla

Si alguien cambia el código del sistema, tiene que volver a construirlo con un doble clic en `reconstruir.bat`; si no lo hace, el navegador sigue mostrando la versión anterior.

# 3. Un recorrido por la pantalla

Cuando abres el sistema ves una pantalla como la de la Figura 3. Está formada por tres franjas: la barra superior, el área central y el pie de página.

## 3.1 La barra superior

La barra superior está siempre visible, aunque bajes por la página. La Figura 4 la muestra de cerca.

![Figura 4 — La barra superior: la marca y el nombre del sistema, los menús «Resolver» y «Teoría», el botón «Manual de usuario» y el botón del tema](img/usuario/U-04-barra-superior.png)

De izquierda a derecha tiene estas partes:

- **La marca y el nombre del sistema**: un cuadrito azul petróleo con el signo de integral (∫), el mismo dibujo que ves en la pestaña del navegador, seguido de «Métodos Iterativos». Los dos juntos son un enlace: al pulsarlos vuelves al inicio, el método de Jacobi. En pantallas muy angostas, como un celular, queda solo el cuadrito.
- **El menú «Resolver ▾».** Abre la lista de los doce métodos para trabajar un ejercicio. Mientras estás resolviendo, aparece subrayado para indicarte en qué sección estás.
- **El menú «Teoría ▾».** Abre la misma lista, pero cada método te lleva a su página de explicación teórica. Mientras lees teoría, el subrayado pasa a este menú.
- **El botón «Manual de usuario»**, con el dibujo de un libro. Abre este manual dentro del sistema, sin salir de él. El mismo enlace está en el pie de página.
- **El botón del tema**, el cuadrito con una luna (en modo claro) o un sol (en modo oscuro). Cambia los colores de la pantalla; el capítulo 9 lo explica. Si dejas el puntero quieto sobre él aparece el texto «Activar modo oscuro» o «Activar modo claro».

El buscador de métodos no está en la barra a la vista: aparece dentro del menú cuando lo abres, en la esquina superior derecha del panel, con el texto «Buscar método…». El capítulo 4 explica cómo usarlo.

En pantallas angostas (menos de 1024 píxeles de ancho, como un celular, una tableta o una ventana pequeña) los dos menús se reemplazan por un solo botón llamado «Métodos» y el botón del manual muestra solo el libro, sin texto. El apartado 4.4 lo describe.

## 3.2 El área central

El área central es donde trabajas, y cambia según la sección en la que estés.

En **«Resolver»** el área central empieza con el **encabezado del método**: la categoría en letras pequeñas y mayúsculas (por ejemplo «SISTEMAS LINEALES»), el nombre del método en letra grande («Jacobi») y, debajo, una línea que dice en qué consiste. Debajo del encabezado vienen, de arriba abajo: la sección «Ejemplos precargados», con ejercicios listos para cargar, que se pliega sola en cuanto cargas un ejemplo o empiezas a escribir (el paso 4 del capítulo 5 lo muestra); la configuración del método (su título cambia según la categoría, por ejemplo «Configuración del sistema» o «Configuración del método»), donde eliges el método, la tolerancia y el máximo de iteraciones; la tarjeta con los datos del problema (por ejemplo «Sistema A·x = b», «Sistema de ecuaciones f(x) = 0», «Polinomio f(x)» o «Datos»); los botones «Resolver» y «Limpiar»; y, una vez que resuelves, el resultado: primero la tarjeta de respuesta y, debajo, el detalle. Todo esto lo recorre paso a paso el capítulo 5.

En **«Teoría»** el área central empieza con el mismo encabezado (categoría, nombre y descripción del método), para que al pasar de una sección a otra sepas que sigues en el mismo método. Debajo hay un texto largo, como el capítulo de un libro, con las fórmulas, las gráficas y un ejemplo resuelto del método. El capítulo 8 lo describe.

## 3.3 El pie de página

Al final de cada página hay un pie de página de una sola línea con el nombre del sistema, un enlace a este **manual de usuario** y otro al **repositorio**, la página de internet donde está publicado el código del sistema. Cuando no lo dice ya el formulario, el pie recuerda además que «Las funciones trigonométricas se evalúan en radianes»: en los métodos de diferenciación e integración esa nota aparece debajo del campo de la función, así que el pie no la repite. Para comprobar en qué método estás, mira el encabezado de arriba o el título de la pestaña (apartado 3.4).

## 3.4 La dirección del navegador

Cada método tiene su propia dirección (la que aparece en la barra de direcciones del navegador). Las de la sección «Resolver» tienen la forma `http://localhost:8080/resolver/` seguida del nombre del método, y las de teoría, `http://localhost:8080/teoria/` seguida del mismo nombre. Por ejemplo:

```
http://localhost:8080/resolver/trapecio
http://localhost:8080/teoria/trapecio
```

La primera abre el formulario del método del trapecio y la segunda su página de teoría. Esto tiene dos ventajas prácticas. La primera es que puedes guardar en favoritos los métodos que más usas y abrirlos directamente. Cada página tiene además su propio título en la pestaña del navegador, que es el nombre con el que queda guardado el favorito: «Método del trapecio · Resolver · Métodos Iterativos», «Método del trapecio · Teoría · Métodos Iterativos» o «Manual de usuario · Métodos Iterativos». El título cambia solo cada vez que pasas de un método o de una sección a otra. La segunda es que puedes compartir la dirección con un compañero que esté en la misma red, cambiando `localhost` por la dirección del computador donde está encendido el sistema (consulta las preguntas frecuentes del capítulo 11). Ten en cuenta que la dirección lleva al método, no a tus datos: quien la abra verá el formulario vacío.

Si escribes `http://localhost:8080` sin nada más, el sistema te lleva al primer método, Jacobi. Si escribes una dirección que no existe (por ejemplo, un favorito viejo o una dirección con un error de escritura), verás la página «Esta página no existe»; el apartado 10.2 explica qué hacer.

# 4. Moverte por el sistema

## 4.1 Los dos menús

El sistema tiene dos menús en la barra superior. Usa **«Resolver»** cuando quieras trabajar un ejercicio: escribir datos y obtener un resultado. Usa **«Teoría»** cuando quieras leer sobre el método: de dónde sale, cuándo se puede usar y un ejemplo resuelto.

Para abrir un menú, haz clic en su nombre. Se despliega un panel, como en la Figura 5, con las cinco categorías en columnas: «Sistemas lineales», «Ecuaciones no lineales», «Polinomios», «Diferenciación numérica» e «Integración numérica». Cada columna lleva arriba una fórmula que identifica la categoría (por ejemplo $Ax = b$ para los sistemas lineales), su nombre, una frase que la describe y, debajo, sus métodos. Cada método tiene su nombre en negrita y una línea que dice en qué consiste, por ejemplo «Usa cada valor nuevo apenas se calcula» bajo Gauss-Seidel. El método en el que estás aparece resaltado con un fondo de color y una raya a la izquierda.

![Figura 5 — El menú «Resolver» desplegado, con las cinco categorías en columnas](img/usuario/U-05-menu-resolver.png)

Para ir a un método, haz clic en su nombre. El panel se cierra solo y el área central cambia al método elegido.

Para cerrar el menú sin elegir nada, pulsa la tecla Esc, haz clic fuera del panel o vuelve a hacer clic en el nombre del menú. Al pie del panel tienes un recordatorio: «12 métodos en 5 categorías. Pulsa / para buscar y Esc para cerrar.»

## 4.2 El buscador

En la parte superior derecha del panel hay una casilla con una lupa y el texto «Buscar método…». Cuando abres el menú, el cursor ya está dentro de ella, así que puedes empezar a escribir de inmediato. A medida que escribes, el panel deja solo los métodos que coinciden y te dice cuántos encontró, por ejemplo «3 métodos». Las letras que coinciden se resaltan en el nombre del método. La Figura 6 muestra el resultado de escribir «derivada».

![Figura 6 — El buscador del menú con la palabra «derivada» y sus tres resultados](img/usuario/U-06-buscador.png)

El buscador no solo mira el nombre del método, sino también su descripción, su categoría y palabras relacionadas. Por eso «derivada» encuentra los tres métodos de diferenciación aunque ninguno se llame así, e «integral» encuentra los cuatro de integración.

No te preocupes por las tildes ni por las mayúsculas: «integracion», «Integración» e «INTEGRACIÓN» dan el mismo resultado. Si escribes varias palabras, el buscador muestra solo los métodos que contienen todas. Si no encuentra nada, te lo dice así: «No hay métodos que coincidan con «xyzzy». Prueba con «integral», «derivada» o «sistema».» Para borrar la búsqueda, haz clic en la equis (×) que aparece al final de la casilla.

**Atajo de teclado.** Desde cualquier página, pulsa la tecla `/` (la barra inclinada) y se abre el menú con el cursor en el buscador. Escribe el nombre, baja con las flechas del teclado hasta el método y pulsa Enter.

## 4.3 Cambiar entre Resolver y Teoría

Supón que estás resolviendo un ejercicio con el método de Simpson y quieres leer su teoría. Haz clic en «Teoría ▾»: se abre el mismo panel, pero ahora los enlaces llevan a las páginas de teoría, y el método de Simpson aparece resaltado porque es en el que estabas. Haz clic en él y llegas a su teoría. Para volver, haz lo mismo con «Resolver ▾».

Dentro del panel también hay dos botones, «Resolver» y «Teoría», en la esquina superior izquierda. Indican a dónde llevan los enlaces del panel y permiten cambiarlo sin cerrarlo: si abriste «Resolver ▾» pero querías la teoría, pulsa «Teoría» dentro del panel.

> **Aviso.** Al pasar a la teoría, el formulario que estabas llenando se descarta. Si tenías datos escritos a mano que no quieres perder, anótalos o descarga el PDF del resultado (apartado 7.8) antes de cambiar. Una forma cómoda de consultar la teoría sin perder nada es abrirla en otra pestaña: haz clic en el método del menú con la rueda del ratón, o con la tecla Ctrl presionada.

## 4.4 En pantallas pequeñas

Si la ventana del navegador mide menos de 1024 píxeles de ancho (un celular, una tableta, o una ventana de escritorio angosta), la barra superior muestra un solo botón, «Métodos». Al tocarlo, el menú ocupa toda la pantalla, como en la Figura 7.

![Figura 7 — El menú en una pantalla angosta, con las categorías como acordeones](img/usuario/U-07-menu-pantalla-angosta.png)

Arriba están el título «Métodos» y el botón «Cerrar». Debajo, los botones «Resolver» y «Teoría», que eligen a dónde llevan los enlaces, y el buscador. Las categorías aparecen una debajo de otra como **acordeones**: filas que se abren y se cierran al tocarlas, con una flechita a la derecha que apunta hacia abajo cuando están cerradas y hacia arriba cuando están abiertas. Al abrir el menú, la categoría del método en el que estás ya aparece abierta. Toca la categoría que te interesa para ver sus métodos y toca el método para ir a él. Si escribes en el buscador, todas las categorías con coincidencias se abren solas.

## 4.5 Los doce métodos

La tabla siguiente es un mapa de todo lo que el sistema puede hacer. Usa la columna «Para qué sirve» para ubicar rápido el método; el Anexo B te ayuda a elegir cuando tienes un ejercicio concreto.

| Categoría | Método | Para qué sirve |
|---|---|---|
| Sistemas lineales | Jacobi | Resolver un sistema de 3 o más ecuaciones lineales, recalculando todas las incógnitas con los valores de la vuelta anterior. |
| Sistemas lineales | Gauss-Seidel | Resolver el mismo tipo de sistema usando cada valor nuevo apenas se calcula; suele necesitar menos vueltas que Jacobi. |
| Ecuaciones no lineales | Punto Fijo (Iterativo Secuencial) | Resolver de 2 a 6 ecuaciones no lineales despejando cada incógnita de su ecuación. |
| Ecuaciones no lineales | Newton | Resolver de 2 a 6 ecuaciones no lineales con derivadas; suele llegar en muy pocas vueltas si el punto de partida es bueno. |
| Polinomios | Bairstow | Encontrar todas las raíces, reales y complejas, de un polinomio de grado 3 a 10. |
| Diferenciación numérica | Diferencias progresiva y regresiva | Aproximar la derivada en un punto con la pendiente de una recta entre dos puntos. |
| Diferenciación numérica | Fórmula de 3 puntos | Aproximar la derivada con una parábola que pasa por tres puntos; más precisa que la anterior. |
| Diferenciación numérica | Fórmula de 5 puntos | Aproximar la derivada con cinco puntos; la más precisa de las tres. |
| Integración numérica | Método del trapecio | Aproximar una integral uniendo los puntos con rectas; acepta datos con separaciones desiguales. |
| Integración numérica | Método de Simpson | Aproximar una integral uniendo los puntos con parábolas (regla 1/3) o cúbicas (regla 3/8). |
| Integración numérica | Integración de Romberg | Mejorar sucesivamente los resultados del trapecio en una tabla triangular. |
| Integración numérica | Cuadratura gaussiana | Aproximar una integral evaluando la función en puntos elegidos de forma óptima; solo con una función, no con tablas. |

# 5. Tu primer ejercicio, paso a paso

En este capítulo vas a resolver un ejercicio completo con el método de Jacobi, desde abrir el método hasta descargar el PDF y limpiar la pantalla. Vas a usar siempre los mismos datos, un ejemplo precargado llamado «Sistema clásico 3x3 (libro de texto)», para que las figuras coincidan con lo que ves en tu pantalla. El sistema que vas a resolver es este:

$$10x_1 - x_2 + 2x_3 = 6,\qquad -x_1 + 11x_2 - x_3 = 22,\qquad 2x_1 - x_2 + 10x_3 = -10$$

Su solución exacta es $x_1 = 1$, $x_2 = 2$ y $x_3 = -1$. Lo interesante no es la respuesta, que ya conoces, sino ver cómo el método llega a ella.

**Paso 1. Abre el método de Jacobi.**
*Qué hacer:* haz clic en «Resolver ▾» y, en la columna «Sistemas lineales», haz clic en «Jacobi». Si acabas de encender el sistema, ya estás ahí, porque Jacobi es el método que se abre por defecto.
*Qué vas a ver:* arriba de la página, el encabezado dice «SISTEMAS LINEALES», «Jacobi» y «Actualiza todas las variables a la vez con los valores anteriores» (Figura 3). El pie de página dice «Sistemas lineales · Jacobi» y la dirección del navegador termina en `/resolver/jacobi`.
*Por qué:* siempre conviene confirmar en qué método estás antes de escribir datos.

**Paso 2. Mira el formulario vacío.**
*Qué hacer:* baja un poco por la página, hasta las tarjetas «Configuración del sistema» y «Sistema A·x = b». No escribas nada todavía.
*Qué vas a ver:* lo de la Figura 8. En «Configuración del sistema» hay cinco controles: «Número de variables (n ≥ 3)», que vale 3; «Método», un selector que dice «Jacobi»; «Tolerancia (criterio de parada)», que vale 0.000001; «Máximo de iteraciones (mínimo real: 6)», que vale 100; y una casilla marcada, «Reordenar filas automáticamente si mejora la convergencia». En «Sistema A·x = b» hay una cuadrícula de casillas vacías: tres columnas para los coeficientes de $x_1$, $x_2$ y $x_3$, un signo igual y una columna «b» para los términos independientes. Debajo está «Vector inicial x0 (opcional, por defecto ceros)», con tres casillas en cero.
*Por qué:* así conoces el formulario antes de que se llene solo. Cada campo se explica a fondo en el apartado 6.1.

![Figura 8 — El formulario de Jacobi vacío: la configuración y la cuadrícula del sistema](img/usuario/U-08-formulario-jacobi-vacio.png)

> **Nota.** Según el idioma de tu sistema, el navegador puede mostrar el separador decimal de la tolerancia como coma (0,000001, como en las figuras) o como punto (0.000001). Es el mismo número y se escribe igual: el campo acepta las dos formas.

**Paso 3. Mira los ejemplos precargados.**
*Qué hacer:* sube hasta la sección «Ejemplos precargados», justo debajo del encabezado del método.
*Qué vas a ver:* lo de la Figura 9: la sección está abierta, porque acabas de entrar al método, y muestra seis ejemplos en forma de tarjetas, cada uno con su nombre en negrita y una descripción corta debajo. Las descripciones largas se cortan en la segunda línea con puntos suspensivos (…); para leerlas completas, deja el puntero quieto sobre la descripción. Por ejemplo, «Sistema 3x3 sin dominancia diagonal (advertencia)» te avisa de que es un caso en el que el método puede no funcionar. A la derecha del título está «Ocultar», que pliega la sección si quieres hacerle sitio al formulario.
*Por qué:* los ejemplos sirven para ver el método funcionando sin tener que escribir nada, y para comparar con los ejercicios del libro. Cada método tiene los suyos.

![Figura 9 — La lista de ejemplos precargados de Jacobi](img/usuario/U-09-ejemplos-precargados.png)

**Paso 4. Carga el ejemplo.**
*Qué hacer:* haz clic en la tarjeta «Sistema clásico 3x3 (libro de texto)».
*Qué vas a ver:* el formulario se llena solo y la sección de ejemplos **se pliega sola**: queda una sola fila que dice «Ejemplos precargados · *Sistema clásico 3x3 (libro de texto)*», con el botón «Cambiar» a la derecha, como en la Figura 10. Así el formulario sube y lo tienes a la vista.
*Por qué:* cargar un ejemplo llena todos los campos a la vez, incluidas la tolerancia y el máximo de iteraciones que el ejemplo necesita. Una vez cargado, ya no necesitas la lista, y por eso se recoge.

![Figura 10 — El formulario de Jacobi con el ejemplo «Sistema clásico 3x3 (libro de texto)» ya cargado y la sección de ejemplos plegada](img/usuario/U-10-formulario-con-ejemplo.png)

> **Nota.** Para volver a ver los ejemplos, haz clic en la fila plegada. Si hay un ejemplo cargado, el botón dice «Cambiar»; si no lo hay, dice «Mostrar» y la fila indica cuántos ejemplos tiene el método, por ejemplo «Ejemplos precargados (6)». Al abrirla, el ejemplo que cargaste sigue resaltado con un borde de color. La sección también se pliega sola cuando empiezas a escribir en cualquier campo del formulario; cambiar de método con el selector «Método» no la pliega. Cada vez que entras a un método, la sección empieza abierta.

**Paso 5. Revisa cómo se llenaron los campos.**
*Qué hacer:* compara la cuadrícula con el sistema escrito al comienzo del capítulo.
*Qué vas a ver:* la primera fila tiene 10, −1, 2 y, después del signo igual, 6: es la primera ecuación, $10x_1 - x_2 + 2x_3 = 6$. Cada fila es una ecuación y cada columna corresponde a una incógnita. Donde la ecuación no tiene una incógnita, la casilla lleva 0 (en este ejemplo no hay ninguna). El vector inicial queda en 0, 0, 0, la tolerancia en 0.000001 y el máximo en 100.
*Por qué:* cuando escribas tus propios ejercicios, este es el error más común: poner un coeficiente en la columna equivocada o olvidar el signo menos. Mirar cómo se llenó un ejemplo te enseña el orden correcto.

**Paso 6. Resuelve.**
*Qué hacer:* haz clic en el botón «Resolver», que está debajo del formulario.
*Qué vas a ver:* **la página baja sola** hasta el resultado, que aparece debajo del formulario. No tienes que buscarlo. Antes de resolver, en ese lugar hay una línea gris que dice «Al pulsar Resolver, aquí aparecen la respuesta y el detalle de cada iteración.». Si el cálculo tarda más de un tercio de segundo, el botón muestra un círculo que gira y cambia a «Resolviendo…»; mientras tanto no se puede volver a pulsar. Con este ejemplo la respuesta llega antes, así que no alcanzas a verlo.
*Por qué:* al pulsar «Resolver», el sistema envía los datos al servidor, que hace todos los cálculos y devuelve el resultado completo. Con este ejemplo tarda menos de un segundo.

**Paso 7. Lee la tarjeta de respuesta.**
*Qué hacer:* mira la primera tarjeta del resultado, la que quedó arriba de la pantalla (parte superior de la Figura 11).
*Qué vas a ver:* el título «Resultado (Jacobi)»; debajo, la solución en letra grande, cada valor con su nombre: $x_1$ vale 1, $x_2$ vale 2 y $x_3$ vale −1. Después, una línea con una marca de visto: «✔ Alcanzó la tolerancia en 12 iteraciones. Error final: 4.01e-7.». Y al final, dos botones: «Descargar PDF» y «Limpiar».
*Por qué:* la tarjeta de respuesta contesta las dos preguntas más importantes: cuál es la respuesta y si el método llegó a ella. «12 iteraciones» quiere decir que el método necesitó dar doce vueltas para que la respuesta dejara de cambiar más de lo que permite la tolerancia. «4.01e-7» es la forma corta de escribir 0.000000401: el cambio de la última vuelta, ya menor que la tolerancia.

![Figura 11 — El resultado de Jacobi: la tarjeta de respuesta arriba y, debajo, la gráfica y la tabla de iteraciones](img/usuario/U-11-resultado-jacobi.png)

> **Nota.** Cuando bajas por el resultado y la tarjeta de respuesta sale de la pantalla, aparece una franja delgada bajo la barra superior con el nombre del método, la respuesta resumida («3 incógnitas»), los botones «Descargar PDF» y «Limpiar» y el enlace «Ir arriba». Así no tienes que subir para descargar o limpiar. La franja solo aparece en ventanas de 1024 píxeles de ancho o más; el apartado 7.1 la describe.

**Paso 8. Lee la tabla de iteraciones.**
*Qué hacer:* baja hasta «Detalle de iteraciones» (parte inferior de la Figura 11). Entre la tarjeta de respuesta y la tabla hay una gráfica que verás en el paso 12; sáltala por ahora.
*Qué vas a ver:* una tabla con las columnas «Iter.», «x1», «x2», «x3» y «Error». Cada fila es una vuelta del método. En la fila 1, el método calculó $x_1 = 0.6$, $x_2 = 2$, $x_3 = -1$ y el error fue 2. En la fila 2, los valores pasaron a 1, 1.963636 y −0.92, y el error bajó a 0.4. Fila tras fila, los valores se acercan a 1, 2 y −1, y el error se hace cada vez más pequeño.
*Por qué:* la tabla es el corazón del método: te muestra el camino, no solo el destino. La columna «Error» dice cuánto cambió la respuesta entre una vuelta y la anterior (el cambio más grande entre las tres incógnitas). Cuando ese cambio queda por debajo de la tolerancia, el método se detiene. El apartado 7.2 explica la tabla con más detalle.

**Paso 9. Pasa a la segunda página de la tabla.**
*Qué hacer:* debajo de la tabla, haz clic en «Siguiente ›» o en el número «2».
*Qué vas a ver:* la tabla muestra las iteraciones 11 y 12. A la derecha de los botones dice «Mostrando 10 de 12 iteraciones» cuando estás en la primera página.
*Por qué:* la tabla muestra diez filas por página para que no se haga interminable. Con «‹ Anterior» vuelves a la primera página. En la última fila, la 12, el error ya es menor que 0.000001, y por eso el método se detuvo ahí.

**Paso 10. Despliega el cálculo de una iteración.**
*Qué hacer:* vuelve a la primera página y haz clic en la flechita «▸» que está al comienzo de la fila 1. Si dejas el puntero quieto sobre ella aparece el texto «Ver cálculo».
*Qué vas a ver:* la fila se abre hacia abajo y muestra tres bloques: «Fórmula (Jacobi)», con la fórmula general del método; «Sustitución numérica», con la fórmula aplicada a cada incógnita y los números reemplazados; y «Error de la iteración», con la cuenta del error de esa fila. Por ejemplo, para $x_1$ verás $\frac{6 - (-1)(0) - (2)(0)}{10} = 0.6$. Los números que vienen de la vuelta anterior (aquí, los ceros del vector inicial) aparecen en **azul**, como indica la leyenda «■ valores de la iteración anterior». La flechita cambia a «▾»; haz clic otra vez para cerrar.
*Por qué:* este es el paso a paso que necesitas para copiar el ejercicio en tu cuaderno o comprobar una cuenta que no te dio. Puedes abrir tantas filas como quieras.

**Paso 11. Lee la comprobación.**
*Qué hacer:* baja hasta el final del resultado, a la sección «Comprobación» (Figura 12).
*Qué vas a ver:* el texto «Se reemplaza la solución en cada ecuación del sistema original; el lado izquierdo debe dar el término independiente b.», la solución usada y, para cada ecuación, la cuenta completa: por ejemplo, en la ecuación 1, $10(1) - (2) + 2(-1) = 10 - 2 - 2 = 6$, y al lado, entre paréntesis, el valor que debía dar, $(b_1 = 6)$, seguido de una marca de visto verde ✔. Al final, «Residuo máximo: 0».
*Por qué:* la comprobación es la prueba de que la respuesta es correcta: si reemplazas la solución en las ecuaciones originales y todo cuadra, el ejercicio está bien. El «residuo» es lo que sobra o falta en cada ecuación; si es 0 o muy pequeño, la solución es buena. El apartado 7.5 explica qué significa cuando no aparece el visto.

![Figura 12 — La sección «Comprobación», con la marca de visto en cada ecuación](img/usuario/U-14-comprobacion.png)

**Paso 12. Mira la gráfica.**
*Qué hacer:* sube hasta «Convergencia del error», la gráfica que está entre la tarjeta de respuesta y la tabla (Figura 13).
*Qué vas a ver:* una línea azul que baja de izquierda a derecha, con un punto por cada iteración, y una línea verde punteada horizontal casi al fondo. Debajo, la leyenda: «Error por iteración» y «Tolerancia (1×10⁻⁶)». La línea azul cruza la verde entre las iteraciones 11 y 12.
*Por qué:* la gráfica resume la tabla en una imagen. Si la línea azul baja, el método se está acercando a la respuesta; el momento en que cruza la línea verde es cuando se cumple la tolerancia. La escala vertical es especial (cada raya es diez veces más pequeña que la anterior); el apartado 7.6 lo explica.

![Figura 13 — La gráfica «Convergencia del error» del ejemplo](img/usuario/U-15-grafica-convergencia.png)

**Paso 13. Descarga el PDF.**
*Qué hacer:* haz clic en «Descargar PDF». El botón está en la tarjeta de respuesta y también en la franja fija de arriba, así que no hace falta subir.
*Qué vas a ver:* el navegador descarga un archivo llamado `jacobi-3x3-` seguido de la fecha de hoy, por ejemplo `jacobi-3x3-2026-11-13.pdf`. Ábrelo desde la carpeta Descargas o desde el aviso de descarga del navegador. Verás algo como la Figura 14: un documento de dos páginas con el título «Sistemas de ecuaciones lineales — Métodos iterativos», los datos del sistema, el resultado, la gráfica, el «Detalle completo de iteraciones» y la comprobación.
*Por qué:* el PDF es la forma de guardar el ejercicio, imprimirlo o entregarlo, porque el sistema no guarda nada por sí solo.

![Figura 14 — El PDF del ejercicio abierto en el visor del navegador](img/usuario/U-16-pdf-descargado.png)

**Paso 14. Compara con Gauss-Seidel sin volver a escribir nada.**
*Qué hacer:* sube a «Configuración del sistema», cambia el selector «Método» de «Jacobi» a «Gauss-Seidel» y pulsa «Resolver». Después despliega la fila 2 de la tabla.
*Qué vas a ver:* los datos del sistema siguen ahí, porque Jacobi y Gauss-Seidel comparten el formulario. La página baja otra vez hasta el resultado, que ahora dice «Resultado (Gauss-Seidel)» y «Alcanzó la tolerancia en 7 iteraciones»: llega a la misma solución en casi la mitad de vueltas. Al desplegar la fila 2 (Figura 15) verás que ahora hay números de **dos colores**: en **azul**, los valores de la iteración anterior, y en **verde**, los valores que ya se recalcularon en esta misma iteración. La leyenda lo dice: «■ valores de la iteración anterior · ■ valores ya recalculados en esta misma iteración». Fíjate en $x_2^{(2)}$: usa el $x_1$ nuevo (0.988364, en verde) y el $x_3$ viejo (−0.914545, en azul).
*Por qué:* esa es exactamente la diferencia entre los dos métodos. Jacobi solo usa valores azules (todos de la vuelta anterior); Gauss-Seidel aprovecha cada valor nuevo apenas lo tiene, y por eso suele llegar antes. Los colores te muestran de dónde sale cada número.

![Figura 15 — Una iteración de Gauss-Seidel desplegada, con los valores anteriores en azul y los recién calculados en verde](img/usuario/U-13-paso-a-paso-colores.png)

**Paso 15. Limpia para empezar otro ejercicio.**
*Qué hacer:* haz clic en «Limpiar». Hay uno debajo del formulario, al lado de «Resolver», otro en la tarjeta de respuesta y otro en la franja fija; los tres hacen lo mismo.
*Qué vas a ver:* aparece el diálogo de la Figura 16, con la pregunta «¿Borrar el ejercicio actual? Se perderán los datos y el resultado.» y dos botones, «Cancelar» y «Limpiar». Si pulsas «Limpiar», el formulario vuelve a estar como en la Figura 8, el resultado desaparece y la página sube hasta el formulario con el cursor en la primera casilla. Si pulsas «Cancelar», no pasa nada.
*Por qué:* el diálogo existe para que no borres tu trabajo por accidente. Si no has descargado el PDF y quieres conservar el ejercicio, pulsa «Cancelar» y descárgalo primero.

![Figura 16 — El diálogo de confirmación del botón «Limpiar»](img/usuario/U-17-dialogo-limpiar.png)

Si entendiste este recorrido, ya sabes usar todo el sistema: todos los demás métodos funcionan igual. Siempre eliges el método, cargas un ejemplo o escribes tus datos, pulsas «Resolver», lees la respuesta, la tabla, el paso a paso, la comprobación y la gráfica, y descargas el PDF. Lo único que cambia de un método a otro es el formulario, y eso es lo que explica el capítulo siguiente.

# 6. Cómo llenar el formulario de cada tipo de método

Todos los formularios tienen dos partes. La tarjeta de configuración, arriba, donde eliges el método y fijas cuándo debe detenerse; y la tarjeta de datos, abajo, donde escribes el problema. Este capítulo recorre cada categoría. Antes, dos ideas que valen para todas.

**La tolerancia.** Imagina que estás afinando una guitarra: giras la clavija un poco, escuchas, giras otro poco, y en algún momento el cambio es tan pequeño que tu oído ya no lo nota; ahí paras. La tolerancia es ese «ya no lo noto»: el cambio más pequeño entre una vuelta y la siguiente que todavía te importa. Si pones 0.000001, el método sigue dando vueltas hasta que la respuesta cambie menos de una millonésima entre una vuelta y otra. Una tolerancia más pequeña da una respuesta más precisa, pero necesita más vueltas.

**El mínimo de seis vueltas.** Ningún método se detiene antes de la sexta iteración (o la sexta fila, en diferenciación e integración), aunque la tolerancia se cumpla antes. Por eso varios campos dicen «(mínimo real: 6)»: si escribes un máximo menor, el sistema hace igualmente seis vueltas. Es una regla del curso para que siempre haya suficientes filas que analizar.

## 6.1 Sistemas de ecuaciones lineales (Jacobi y Gauss-Seidel)

El formulario es el que conociste en el capítulo 5 (Figuras 8 y 10).

**«Número de variables (n ≥ 3)».** Cuántas incógnitas tiene tu sistema, que es también cuántas ecuaciones tiene. Debe ser 3 o más; el formulario admite hasta 12. Al cambiarlo, la cuadrícula crece o se achica. Si escribes 2, el sistema te pide al menos 3: estos métodos están pensados para sistemas de tres o más ecuaciones.

**«Método».** Elige entre «Jacobi» y «Gauss-Seidel». Puedes cambiar de uno a otro sin perder los datos.

**«Tolerancia (criterio de parada)».** Explicada al comienzo del capítulo. Debe ser un número mayor o igual que cero. Si no sabes qué poner, deja 0.000001, que da seis decimales correctos. Según el idioma de tu sistema, el campo puede mostrarlo con coma (0,000001); es el mismo número y puedes escribirlo con punto o con coma.

**«Máximo de iteraciones (mínimo real: 6)».** El límite de vueltas. Si el método no alcanza la tolerancia antes de ese número, se detiene igual y te avisa (Figura 30, en el capítulo 10). Debe ser un número entero de 1 en adelante. Si no sabes qué poner, deja 100; si el método no llega, súbelo a 500.

**«Reordenar filas automáticamente si mejora la convergencia».** Si está marcada y tu sistema no cumple la condición de «diagonal dominante» (ver el glosario), el sistema intenta cambiar el orden de las ecuaciones para que la cumpla. Cambiar el orden de las ecuaciones no cambia la solución, como dice el texto de ayuda, pero sí puede hacer que el método funcione donde antes no. Déjala marcada salvo que tu profesor te pida resolver el sistema en el orden exacto en que está escrito.

**La cuadrícula «Sistema A·x = b».** Cada fila es una ecuación y cada columna una incógnita. En las columnas «x1», «x2», «x3»… escribe los coeficientes (los números que multiplican a cada incógnita) y en la columna «b» el término independiente (el número que queda al otro lado del igual). Para escribir la ecuación $2x_1 + 3x_3 = 7$ en un sistema de tres incógnitas, la fila queda 2, 0, 3 y, en «b», 7: la incógnita que no aparece lleva 0. Una casilla vacía también vale 0.

Puedes escribir números enteros, decimales con punto o con coma (2.5 o 2,5) y fracciones (6/7). Como dice la ayuda del formulario: «Puedes escribir fracciones, por ejemplo 6/7. Al salir del campo se muestra redondeado a 6 decimales, pero el cálculo usa el valor exacto.» Si escribes algo que no es un número, la casilla se pone roja y debajo aparece «Escribe un número (2.5) o una fracción (6/7).»; si escribes una fracción con denominador cero, «El denominador de una fracción no puede ser cero.».

Hay una regla que el sistema exige: **ningún número de la diagonal principal puede ser cero** (la diagonal son las casillas que van de la esquina superior izquierda a la inferior derecha: fila 1 columna 1, fila 2 columna 2, etc.). El motivo es que cada ecuación se usa para despejar su propia incógnita, y para despejarla hay que dividir entre ese número.

**«Vector inicial x0 (opcional, por defecto ceros)».** Es el punto de partida: los valores con los que el método empieza a adivinar, como cuando le dices a alguien «empieza a buscar desde aquí». Si no sabes qué poner, deja los ceros; en sistemas con diagonal dominante el método llega a la respuesta desde cualquier punto de partida. Si tienes una idea aproximada de la solución, escribirla ahorra vueltas.

## 6.2 Sistemas de ecuaciones no lineales (Punto Fijo y Newton)

En estos métodos las ecuaciones no caben en una cuadrícula de números, así que se escriben como texto. La Figura 17 muestra el formulario de Newton con el ejemplo «Clásico 2x2 (Chapra)» cargado.

![Figura 17 — El formulario de un sistema no lineal (Newton), con el teclado de símbolos y la vista previa de cada ecuación](img/usuario/U-19-formulario-no-lineal.png)

**La configuración** tiene «Método» (con las opciones «Punto Fijo (Iterativo Secuencial)» y «Newton»), «Tolerancia (criterio de parada)» y «Máximo de iteraciones (mínimo real: 6)», que funcionan igual que en el apartado anterior.

**Las variables.** En **Newton** hay un campo «Variables, en orden», donde escribes los nombres de las incógnitas separados por comas, por ejemplo `x, y` o `x, y, z`. Como dice la ayuda: «Separadas por comas. El orden fija las columnas del Jacobiano y el de x0.» En **Punto Fijo** no hay ese campo: cada ecuación tiene a su izquierda una casilla «Variable», donde escribes la incógnita que se despejará de esa ecuación. La ayuda lo explica: «La ecuación de cada fila se despeja automáticamente para la variable de esa fila.» Usa nombres cortos de letras, como `x`, `y`, `z`, `w`; no uses `e` ni `pi`, que están reservados para las constantes.

**Las ecuaciones.** Cada ecuación va en su propia casilla, numerada a la izquierda (1, 2, …). Puedes escribirla igualada a cero, como `x^2 + x*y - 10 = 0`, o con dos lados, como `x^2 + x*y = 10`. Si no escribes ningún signo igual, el sistema entiende que la expresión es igual a cero. Hacen falta tantas ecuaciones como incógnitas, entre 2 y 6. Para añadir una ecuación pulsa «+ Agregar ecuación»; para quitar una, pulsa la «×» a su derecha (con dos ecuaciones no puedes quitar más: el botón dice «Se necesitan al menos 2 ecuaciones»). Cómo escribir cada operación se explica en el apartado 6.6, y el mismo formulario trae al final un recuadro, «Cómo escribir cada operación», con la lista.

**El teclado de símbolos.** Encima de las ecuaciones hay una fila de botones: «√», «xⁿ», «log», «ln», «exp», «sin», «cos», «tan», «π», «e», «|x|», «( )» y «Más funciones ▾». Cada uno escribe por ti la función correspondiente en la ecuación donde está el cursor; a la derecha te recuerda dónde se insertará, por ejemplo «Se inserta en la ecuación 1». Si dejas el puntero quieto sobre un botón, aparece qué hace, por ejemplo «Raíz cuadrada: sqrt()». «Más funciones» despliega las funciones menos usadas (trigonométricas inversas e hiperbólicas).

**La vista previa.** Debajo de cada ecuación aparece, en una franja gris, cómo la entendió el sistema, escrita como en un libro. En la Figura 17, `x^2 + x*y - 10 = 0` se ve como $x^2 + xy - 10 = 0$. Revísala siempre: es la forma más rápida de descubrir un paréntesis mal puesto. Si la ecuación tiene un error, la casilla se pone roja y la franja muestra el problema en rojo, por ejemplo «'seno' no es una variable declarada ni una función conocida.».

**«Punto inicial x0 (opcional, por defecto ceros)».** Una casilla por incógnita, con el valor desde el que el método empieza a buscar. Admite fracciones. En los sistemas no lineales el punto de partida importa mucho: desde un punto puede funcionar y desde otro no, porque estas ecuaciones pueden tener varias soluciones o zonas donde las cuentas no se pueden hacer (por ejemplo, una raíz cuadrada de un número negativo). Si no sabes qué poner, usa el valor que te da el enunciado; si no te da ninguno, prueba con valores pequeños distintos de cero, como 1 y 1, porque desde el cero algunas ecuaciones dejan a Newton sin poder avanzar.

**Lo que exige Punto Fijo.** El sistema despeja cada ecuación por ti, pero solo si el despeje es único y la variable aparece como mucho elevada a la 4. Si la variable aparece al cuadrado y tiene dos despejes posibles (uno con raíz positiva y otro con negativa), te pide que reescribas la ecuación con la variable sola a la izquierda, por ejemplo `x = sqrt(11 - y)`. El capítulo 10 recoge los mensajes exactos.

**Lo que exige Newton.** Cada ecuación debe contener al menos una de las variables declaradas, y cada variable debe aparecer en alguna ecuación.

## 6.3 Raíces de polinomios (Bairstow)

La Figura 18 muestra el formulario de Bairstow con el ejemplo «Cúbica con raíces reales» cargado y la pestaña «Coeficientes» elegida.

![Figura 18 — El formulario de Bairstow con los coeficientes del polinomio](img/usuario/U-20-formulario-bairstow.png)

**La configuración** tiene «Método» (solo «Bairstow»), «Tolerancia εs (%)» y «Máximo de iteraciones por factor (mínimo real: 6)».

**Por qué aquí la tolerancia va en porcentaje.** En los demás métodos la tolerancia es una diferencia absoluta, un número fijo. En Bairstow se mide el error relativo, es decir, cuánto cambió el valor comparado con su propio tamaño, expresado en porcentaje, como hace el libro de Chapra y Canale de donde viene el método. Una tolerancia de 0.0001 % significa que el valor cambió menos de una millonésima de su tamaño. Por eso el valor por defecto es 0.0001 y no 0.000001. Debe ser mayor que cero; si escribes 0, el sistema responde «La tolerancia εs debe ser mayor que 0 (está en porcentaje).».

**El máximo de iteraciones es por factor.** Bairstow saca las raíces de dos en dos, extrayendo factores de grado 2 del polinomio, y cada factor tiene sus propias vueltas. El máximo se aplica a cada factor por separado.

**El polinomio.** Puedes darlo de dos formas, con las pestañas «Escribir polinomio» y «Coeficientes».

- Con **«Escribir polinomio»** escribes el polinomio en una casilla, «Polinomio en x», por ejemplo `x^3 - 6x^2 + 11x - 6`. La ayuda del formulario lo resume: potencias con `^`, productos con `*` o implícitos (`3x^2`), fracciones (`x/2`) y paréntesis (`(x - 1)(x + 2)`); puedes igualarlo a cero o escribir dos lados (`x^3 = 2x - 1`). Debe estar en la variable `x` y no puede llevar funciones como `sin` o `sqrt`. Hay un teclado reducido con los botones «xⁿ», «x», «( )» y «a/b».
- Con **«Coeficientes»** eliges el «Grado del polinomio» (de 3 a 10) y escribes los coeficientes en casillas etiquetadas de la potencia más alta a la más baja: «a₃·x³», «a₂·x²», «a₁·x», «a₀». Para $x^3 - 6x^2 + 11x - 6$ son 1, −6, 11 y −6. Si falta una potencia, su coeficiente es 0: $x^4 - 5x^2 + 4$ se escribe 1, 0, −5, 0, 4. El primer coeficiente no puede ser 0.

El grado debe estar entre 3 y 10. Para grados 1 y 2 no hace falta un método iterativo: el sistema te recuerda que se resuelven despejando o con la fórmula cuadrática.

**«Valores iniciales (opcional, por defecto −1 y −1)».** Son $r_0$ y $s_0$, el punto de partida del factor cuadrático $x^2 - rx - s$ que el método va ajustando (la fórmula aparece al pie de la tarjeta, «Factor cuadrático»). Si no sabes qué poner, deja −1 y −1. Si el método te avisa de que el sistema se volvió singular o no llegó, prueba con otros valores, como 0.5 y −0.5; el ejemplo «Cúbica con par complejo» lo muestra.

## 6.4 Diferenciación numérica (diferencias, 3 puntos y 5 puntos)

Los tres métodos de diferenciación comparten formulario. Calculan $f'(x_0)$, la derivada de una función en un punto, es decir, la pendiente de la curva justo en ese punto. La Figura 19 muestra el formulario de la «Fórmula de 3 puntos» con el ejemplo «x·eˣ en x₀ = 2 (Burden y Faires)» cargado.

![Figura 19 — El formulario de diferenciación en modo «Función»](img/usuario/U-21-diferenciacion-funcion.png)

**«Fórmula».** Elige qué fórmula usar. En «Diferencias progresiva y regresiva» las opciones son «Progresiva» (usa el punto y otro a su derecha), «Regresiva» (el punto y otro a su izquierda) y «Ambas». En «Fórmula de 3 puntos» y «Fórmula de 5 puntos» son «Punto medio» (usa puntos a ambos lados; la más precisa), «Extremo hacia adelante» (solo puntos a la derecha; útil al comienzo de una tabla), «Extremo hacia atrás» (solo a la izquierda; útil al final) y «Todas». **«Ambas» o «Todas»** calcula todas las fórmulas a la vez y las muestra lado a lado, con una tabla para cada una y una comparación al final; es lo más útil para estudiar, porque ves cuál se acerca más.

**«Método».** Cambia entre los tres métodos de diferenciación sin perder los datos.

**«Tolerancia del error estimado» y «Máximo de refinamientos de h».** El método calcula la derivada con un paso $h$, después con $h/2$, con $h/4$, y así sucesivamente: cada nueva fila es un «refinamiento». Se detiene cuando dos filas seguidas difieren en menos que la tolerancia (y ya hay al menos seis filas). El máximo de refinamientos debe estar entre 6 y 30; el valor por defecto es 25. La tolerancia por defecto es 0.0001 en diferencias y 0.000001 en las fórmulas de 3 y 5 puntos. Ambos campos desaparecen en el modo «Tabla de datos», porque con una tabla no se puede achicar el paso.

**«Datos».** Dos botones eligen el modo: «Función» o «Tabla de datos».

**Modo «Función».** Escribe la función en «Función f(x)», en la variable `x`, por ejemplo `x*exp(x)` o `ln(x)`. La ayuda recuerda: «Las funciones trigonométricas se evalúan en radianes.» Tienes el mismo teclado de símbolos y la misma vista previa del apartado 6.2. Debajo, en «Punto x₀ y paso inicial h₀ (h₀ > 0, por defecto 0.1)», hay dos casillas:

- **x₀** es el punto donde quieres la derivada. La función tiene que estar definida en ese punto y en los puntos vecinos que la fórmula usa; por ejemplo, `ln(x)` no sirve en $x_0 = 0$.
- **h₀** es el paso inicial: la distancia entre $x_0$ y los puntos vecinos que la fórmula usa. Tiene que ser mayor que 0. Conviene que sea pequeño (0.1 está bien en casi todos los ejercicios), porque las fórmulas de derivación son más exactas cuanto más cerca están los puntos. Pero tampoco debe ser diminuto: con pasos extremadamente pequeños el computador empieza a perder decimales al restar números casi iguales, y el resultado empeora. El sistema detecta ese momento y te avisa en el resultado.

**Modo «Tabla de datos».** La Figura 20 muestra el mismo método con el ejemplo «Tabla de x·eˣ (Burden y Faires, tabla + función)».

![Figura 20 — El formulario de diferenciación en modo «Tabla de datos»](img/usuario/U-22-diferenciacion-tabla.png)

Escribes los puntos medidos en una tabla con las columnas «xᵢ» y «f(xᵢ)». Pulsa «+ Agregar punto» para añadir una fila y la «×» de la derecha para quitarla. Lo que exige el modo tabla:

- **Puntos suficientes:** al menos 2 en diferencias, 3 en la fórmula de 3 puntos y 5 en la de 5 puntos, y como máximo 20. La ayuda del formulario te dice el rango del método en el que estás, por ejemplo «(de 3 a 20 puntos)».
- **x estrictamente creciente:** cada $x$ debe ser mayor que el anterior, sin repetir.
- **Espaciado igual** en las fórmulas de 3 y 5 puntos: la distancia entre cada $x$ y el siguiente tiene que ser siempre la misma (por ejemplo 1.8, 1.9, 2.0, 2.1). Las diferencias progresiva y regresiva sí aceptan espaciado desigual.

El sistema calcula la derivada en cada punto de la tabla con la fórmula que corresponda. En «Función para comparar (opcional)» puedes escribir la función de la que salieron los datos, si la conoces; con ella el sistema calcula la derivada exacta, el error real y la cota, y además comprueba que los datos coincidan con la función.

## 6.5 Integración numérica (trapecio, Simpson, Romberg y cuadratura gaussiana)

Los cuatro métodos calculan la integral definida $\int_a^b f(x)\,dx$, el área bajo la curva entre $a$ y $b$. La Figura 21 muestra el formulario del trapecio con el ejemplo «Polinomio de Chapra en [0, 0.8]» y, debajo, la gráfica de trapecios que aparece en el resultado.

![Figura 21 — El formulario del método del trapecio y su gráfica de trapecios sombreados](img/usuario/U-24-trapecio-formulario-y-grafica.png)

**«Método».** Cambia entre «Método del trapecio», «Método de Simpson», «Integración de Romberg» y «Cuadratura gaussiana» sin perder los datos.

**«Tolerancia del error estimado».** Como en diferenciación, cada fila del resultado duplica el número de segmentos y el método se detiene cuando dos filas seguidas difieren en menos que la tolerancia. Por defecto, 0.000001 (el campo puede mostrarlo con coma, 0,000001, según el idioma de tu sistema; se escribe igual).

**El máximo de filas** tiene un nombre distinto en cada método, porque cada uno avanza de forma diferente: «Máximo de refinamientos (de 6 a 22)» en el trapecio y en Simpson (por defecto 20), «Máximo de filas (de 6 a 20)» en Romberg (por defecto 15) y «Máximo de puntos m (de 6 a 20)» en la cuadratura gaussiana (por defecto 12). El propio rótulo te dice el rango permitido.

**El número inicial de segmentos.** Es en cuántos pedazos se divide el intervalo en la primera fila.

- En el trapecio, «Segmentos iniciales n₀ (de 1 a 1000)». Cualquier número entero sirve; 1 es lo habitual, porque así la primera fila es la regla simple.
- En Simpson hay un selector «Regla» con «Simpson 1/3», «Simpson 3/8» y «Ambas», y dos campos: «n₀ de Simpson 1/3 (par, de 2 a 1000)» y «n₀ de Simpson 3/8 (múltiplo de 3, de 3 a 999)». La regla 1/3 une los puntos de tres en tres con parábolas, y cada parábola ocupa 2 segmentos: por eso necesita un número **par** de segmentos. La regla 3/8 los une de cuatro en cuatro con cúbicas, y cada cúbica ocupa 3 segmentos: por eso necesita un número **múltiplo de 3**. Si no sabes qué poner, deja 2 y 3.
- Romberg no tiene este campo: siempre empieza con 1 segmento y duplica en cada fila (1, 2, 4, 8, …, siempre **potencias de dos**).
- La cuadratura gaussiana tiene en su lugar «Subintervalos N (de 1 a 50)». La ayuda lo explica: «Con N = 1 se aplica Gauss a todo el intervalo; con N > 1 se divide el intervalo en N partes y se aplica Gauss en cada una (versión compuesta), útil cuando la función cambia mucho en el intervalo.» Si no sabes, deja 1.

**«Datos».** Como en diferenciación, eliges entre «Función» y «Tabla de datos».

**Modo «Función».** Escribe la función en «Función f(x)» y los límites en «Límites de integración (a < b)», en las casillas «a» y «b». El límite inferior debe ser menor que el superior, y la función debe estar definida en todo el intervalo (en la cuadratura gaussiana basta con que esté definida dentro, porque no usa los extremos). Los límites admiten fracciones; para usar $\pi$ como límite escribe su valor decimal, 3.141593, o la fracción que te dé el enunciado.

**Modo «Tabla de datos».** Escribes los puntos medidos, como en diferenciación. Cada método exige algo distinto: el trapecio acepta de 2 a 30 puntos **con cualquier separación**; Simpson necesita de 3 a 30 puntos **igualmente espaciados**; Romberg necesita **3, 5, 9, 17 o 33** puntos igualmente espaciados (uno más que una potencia de dos, porque cada fila duplica los segmentos); y la cuadratura gaussiana **no admite tablas**, como explica el aviso que aparece en su lugar: necesita evaluar la función en puntos especiales que no estarán en tu tabla.

## 6.6 Cómo escribir una función

Las ecuaciones de los sistemas no lineales, los polinomios de Bairstow y las funciones de diferenciación e integración se escriben con el teclado, siguiendo unas reglas sencillas. La tabla resume cómo se escribe cada cosa.

| Lo que quieres escribir | Cómo se escribe |
|---|---|
| Suma, resta | `x + 2`, `x - 2` |
| Multiplicación | `3*x` (también vale `3x`); entre dos letras, siempre `x*y` |
| División | `(x + 1)/2` |
| Potencia $x^2$ | `x^2` o `x**2` |
| Potencia con exponente compuesto, $x^{x+1}$ o $e^{-x^2}$ | `x^(x+1)`, `exp(-x^2)` |
| Raíz cuadrada $\sqrt{x}$ | `sqrt(x)` |
| Raíz cúbica $\sqrt[3]{x}$ | `x^(1/3)` |
| Exponencial $e^x$ | `exp(x)` o `e^x` |
| Logaritmo natural $\ln x$ | `ln(x)` |
| Logaritmo en base 10 | `log(x)` |
| Logaritmo en otra base, $\log_2 x$ | `log(x, 2)` |
| Seno, coseno, tangente | `sin(x)`, `cos(x)`, `tan(x)` |
| Funciones inversas | `asin(x)`, `acos(x)`, `atan(x)` |
| Hiperbólicas | `sinh(x)`, `cosh(x)`, `tanh(x)` |
| Seno al cuadrado, $\sin^2 x$ | `sin(x)^2` |
| Valor absoluto $\lvert x \rvert$ | `abs(x)` |
| Constantes $\pi$ y $e$ | `pi` y `e` |
| Número decimal | `1.5` (con punto) |
| Agrupar | paréntesis `( )`, tantos como necesites |

Ten presentes estos tres avisos:

> **Aviso 1: las funciones trigonométricas trabajan en radianes.** `sin(30)` es el seno de 30 radianes, no de 30 grados. Si tu ejercicio está en grados, conviértelo: 30 grados son `pi/6` radianes, y en general, para pasar de grados a radianes se multiplica por `pi/180`.

> **Aviso 2: escribe el signo de multiplicar.** El sistema entiende `3x` y `2(x + 1)`, pero `xy` lo lee como una variable llamada «xy», que no existe. Para no equivocarte, escribe siempre el `*`: `3*x`, `x*y`, `2*(x + 1)`.

> **Aviso 3: hay funciones que el sistema no acepta.** Solo acepta las de la tabla. No reconoce los nombres en español (`sen`, `tg`, `raiz`), ni otras funciones como `sec`, `csc`, `cot` o `arcsin`, ni símbolos como `√`, `²`, `|x|` o `!`. Usa sus equivalentes: `1/cos(x)` para la secante, `asin(x)` para el arcoseno, `abs(x)` para el valor absoluto. Tampoco distingue mayúsculas de forma flexible: `Sin(x)` o `PI` no sirven; escribe todo en minúsculas.

Cinco ejemplos escritos correctamente:

```
x^3 - 2*x^2 + x
x*exp(x)
sqrt(1 - x^2)
3*x - cos(y) - 1 = 0
exp(-x^2)/(1 + x)
```

Cinco errores frecuentes, con su corrección:

| Lo que se escribió | Por qué falla y cómo corregirlo |
|---|---|
| `sen(x)` | «sen» es el nombre en español; el sistema usa los nombres en inglés. Escribe `sin(x)`. |
| `xy - 3 = 0` | Sin signo de multiplicar, «xy» parece una sola variable. Escribe `x*y - 3 = 0`. |
| `sin x` | Las funciones necesitan paréntesis. Escribe `sin(x)`. |
| `1,5*x` | En las funciones el decimal va con punto (la coma separa argumentos). Escribe `1.5*x`. |
| `x²` o `√x` | Los símbolos especiales no se aceptan. Escribe `x^2` o `sqrt(x)`, o usa los botones «xⁿ» y «√» del teclado de símbolos. |

> **Nota.** En los campos numéricos (las casillas de la matriz, el punto inicial, los límites) sí puedes usar la coma decimal, porque ahí no hay funciones que la confundan. La regla del punto es solo para las casillas donde escribes funciones o ecuaciones.

# 7. Cómo leer el resultado

Cuando pulsas «Resolver», el resultado aparece debajo del formulario y **la página baja sola hasta él**: no tienes que buscarlo. Si en vez de un resultado hay un error, la página te lleva al mensaje de error (apartado 10.1). El resultado tiene dos partes. Arriba, la **tarjeta de respuesta**, con lo que viniste a buscar. Debajo, en un recuadro más discreto, el **detalle**: su forma cambia un poco de un método a otro, pero siempre tiene las mismas piezas, que son un resumen, una o varias tablas, el paso a paso, la comprobación y las gráficas. Este capítulo explica cada una como si nunca hubieras visto una tabla de iteraciones.

## 7.1 La tarjeta de respuesta, la franja fija y el resumen

**La tarjeta de respuesta** es lo primero que ves (parte superior de la Figura 11). Contiene solo tres cosas:

- **La respuesta, en letra grande.** Debajo del título «Resultado (…)», que lleva el nombre del método que produjo el resultado, está cada valor con su nombre encima. En los sistemas, un valor por incógnita. En Bairstow, las raíces, llamadas x1, x2, x3… En diferenciación, la derivada, una por cada fórmula que elegiste (con «Todas» verás varias, cada una con el nombre de su fórmula); si trabajas con una tabla de datos, la derivada en cada punto, como «f′(1.8)». En integración, el valor de la integral, uno por regla (con «Ambas» en Simpson verás «Simpson 1/3» y «Simpson 3/8»). Cuando hay más de cuatro valores se muestran en letra un poco más pequeña, para que quepan.
- **Una línea de estado.** Si todo salió bien, lleva una marca de visto y dice, por ejemplo, «✔ Alcanzó la tolerancia en 12 iteraciones. Error final: 4.01e-7.» (en diferenciación e integración dice «filas» en vez de «iteraciones»). El error final es el de la última vuelta; los errores muy pequeños se escriben en forma corta: 4.01e-7 es 0.000000401. Con una tabla de datos no hay vueltas que contar, y la línea dice «Calculado directamente con los datos de la tabla.». Si el método **no** alcanzó la tolerancia, la línea pasa a un recuadro amarillo: «⚠ No alcanzó la tolerancia: se detuvo tras 6 iteraciones. Error final: 0.001299. Los valores mostrados son los últimos calculados, no una solución.» (Figura 30). Los valores siguen ahí, pero son solo lo último que alcanzó a calcular el método.
- **Los botones «Descargar PDF»** (apartado 7.8) **y «Limpiar»** (apartado 7.9).

**La franja fija.** El detalle del resultado puede ser largo. Cuando bajas y la tarjeta de respuesta sale de la pantalla, aparece bajo la barra superior una franja delgada con el nombre del método, la respuesta resumida (el valor, si es uno solo, o cuántos hay: «3 incógnitas», «3 raíces», «2 reglas»), los botones «Descargar PDF» y «Limpiar» y el enlace «Ir arriba», que te devuelve al comienzo de la página. Cuando vuelves a subir hasta la tarjeta, la franja desaparece. Solo aparece en ventanas de 1024 píxeles de ancho o más; en un celular o una ventana angosta no hay franja, y los botones están en la tarjeta de respuesta.

**El resumen**, debajo de la tarjeta de respuesta, abre el detalle. Contiene:

- **Los avisos**, si los hay, en recuadros amarillos con el símbolo ⚠. Te advierten de algo que conviene saber aunque haya un resultado; por ejemplo, que la matriz no es diagonalmente dominante. Léelos siempre; el capítulo 10 los explica uno por uno.
- **Los datos de la ejecución.** En Bairstow, por ejemplo, «Raíces encontradas: 3 de 3 · Iteraciones de Bairstow en total: 8 · Tolerancia εs: 0.0001 %». En diferenciación e integración, una línea como «Filas usadas: 13 · Estado: alcanzó la tolerancia (0.000001) · n₀ = 1», que dice cuántas filas tiene la tabla, si se cumplió la tolerancia y con qué datos de partida.
- **La respuesta junto a su valor exacto**, bajo el título «Resumen», en diferenciación e integración. En integración, tres recuadros: «Aproximación» (lo que calculó el método), «Integral exacta» (el valor verdadero, cuando el sistema lo puede calcular) y «Error verdadero» (la diferencia entre ambos). En diferenciación, un recuadro por fórmula y otro con el «Valor exacto» para comparar. En Bairstow, más abajo, el «Resumen de raíces» lista cada raíz con su parte real e imaginaria.

En Jacobi, Gauss-Seidel y Newton, si no hay avisos, el resumen no tiene nada que mostrar y el detalle empieza directamente con la gráfica.

## 7.2 La tabla

**Qué es una iteración.** Un método iterativo no encuentra la respuesta de una vez: parte de un valor inicial, aplica una regla para obtener un valor mejor, vuelve a aplicar la regla a ese valor, y así sucesivamente. Cada aplicación de la regla es una **iteración** (una vuelta). En diferenciación e integración la idea es parecida, pero cada fila repite el cálculo con un paso más pequeño o con más segmentos; a esas filas se les llama **refinamientos**.

**Cómo se lee una fila.** Cada fila es una vuelta, y se lee de izquierda a derecha: primero el número de la vuelta, después los valores calculados en esa vuelta y al final el error. En la Figura 11, la fila 3 dice que en la tercera vuelta el método calculó $x_1 = 0.980364$, $x_2 = 2.007273$ y $x_3 = -1.003636$, y que la respuesta cambió como mucho 0.083636 respecto a la vuelta 2. Leyendo la tabla de arriba abajo ves cómo los valores se acercan a la respuesta y cómo el error se achica.

**Qué significa cada columna en los sistemas.** «Iter.» es el número de la vuelta. «x1», «x2», «x3» (o los nombres de tus variables, como «x» e «y») son los valores de las incógnitas al terminar esa vuelta. «Error» es el cambio más grande entre una vuelta y la anterior; en la primera fila se compara con el vector inicial. La flechita «▸» de la izquierda abre el paso a paso de esa fila (apartado 7.3).

**Qué significa cada columna en diferenciación e integración.** Estas tablas tienen más columnas, y cada encabezado tiene una explicación propia: si pasas el puntero sobre él (o lo tocas en el celular), aparece un globo con su significado. Además, debajo de cada tabla hay un recuadro desplegable, «¿Qué significa cada columna?», que reúne todas las explicaciones juntas. La Figura 22 lo muestra abierto bajo la tabla del método del trapecio. Por ejemplo, ahí se explica que «Error estimado» es «Cuánto cambió T respecto a la fila anterior, |T_k − T_(k−1)|. Decide cuándo parar: cuando ya casi no cambia (es menor que la tolerancia), se considera que se llegó a la precisión pedida.», y que la columna «≤ cota» lleva «✔ si el error verdadero quedó por debajo de la cota, como predice la teoría.». Los encabezados con explicación se reconocen porque están subrayados con una línea punteada.

![Figura 22 — La tabla de refinamiento del trapecio con la leyenda «¿Qué significa cada columna?» abierta](img/usuario/U-12-leyenda-columnas.png)

> **Nota.** Las tablas de Jacobi, Gauss-Seidel, Punto Fijo y Newton no tienen la leyenda «¿Qué significa cada columna?», porque sus columnas son solo las incógnitas y el error, explicadas arriba.

**La paginación.** Las tablas muestran diez filas por página. Debajo están los botones «‹ Anterior» y «Siguiente ›» y, según el método, los números de página o un texto como «Página 1 de 2» o «Mostrando 10 de 12 iteraciones».

## 7.3 El paso a paso

En casi todas las tablas, cada fila empieza con una flechita «▸» («Ver cálculo» al pasar el puntero). Al hacer clic, la fila se despliega y muestra la cuenta completa de esa vuelta; la flechita cambia a «▾», y un segundo clic la cierra. En los sistemas lineales el paso a paso tiene tres bloques, como viste en el capítulo 5: «Fórmula», con la fórmula general; «Sustitución numérica», con los números reemplazados en la fórmula para cada incógnita; y «Error de la iteración», con la cuenta del error. En los demás métodos los bloques cambian (por ejemplo, Newton muestra la matriz Jacobiana evaluada y la regla de Cramer; el trapecio, cada punto evaluado y la suma), pero la idea es la misma: no hay ningún número de la tabla que no puedas rastrear hasta su origen.

**Los colores.** En la sustitución numérica los números llevan color según de dónde vienen, como se ve en la Figura 15:

- **Azul:** el valor viene de la vuelta anterior.
- **Verde:** el valor ya se recalculó en esta misma vuelta.

En Jacobi solo verás azul, porque todas las incógnitas se calculan con los valores de la vuelta anterior. En Gauss-Seidel verás los dos colores, porque cada incógnita usa los valores que ya se recalcularon antes que ella en la misma vuelta. La leyenda que está justo encima de las fórmulas, «■ valores de la iteración anterior · ■ valores ya recalculados en esta misma iteración», te lo recuerda.

Esto ayuda mucho a copiar el ejercicio al cuaderno: cuando hagas la cuenta a mano, los números azules los tomas de la fila de arriba de la tabla y los verdes de la fila que estás calculando. Si tu cuenta no coincide con la del sistema, compara número por número; casi siempre el error está en haber tomado un valor de la fila equivocada.

En Punto Fijo hay además una tabla previa con las ecuaciones despejadas, cada una con su flechita «▸» («Ver el despeje paso a paso»), que muestra cómo se despejó cada variable. En Romberg y en la cuadratura gaussiana el paso a paso está en una sección propia, «Paso a paso de cada fila», con un apartado desplegable por fila.

## 7.4 Los glosarios de símbolos

Debajo de muchas fórmulas del resultado y de la teoría hay un recuadro desplegable titulado «¿Qué significa cada símbolo?». Al abrirlo, lista cada símbolo de la fórmula con una explicación en palabras. La Figura 23 muestra el de la fórmula del error aproximado del trapecio: explica, por ejemplo, que el signo menos aparece porque «si la curva es convexa (f'' > 0), el trapecio queda por encima de la curva, así que el error I − T es negativo».

![Figura 23 — El glosario «¿Qué significa cada símbolo?» abierto bajo una fórmula](img/usuario/U-26-glosario-simbolos.png)

Sirven para que no tengas que adivinar qué es cada letra ni buscarlo en el libro. Algunos se muestran abiertos al aparecer y otros cerrados; haz clic en el título para abrirlos o cerrarlos. Algunos terminan con una línea en cursiva que resume la fórmula en una frase, por ejemplo «En resumen: se suman las áreas de los n trapecios.».

En las gráficas y tablas más elaboradas hay recuadros parecidos con otros títulos, como «¿Cómo leer la gráfica?», «¿Cómo se lee este gráfico?» y «¿Cómo se lee esta tabla?».

## 7.5 La comprobación

Al final de cada resultado hay una sección «Comprobación» (Figura 12). Su objetivo es verificar la respuesta por un camino distinto al del método, como harías tú para estar seguro de un ejercicio.

**Qué verifica, según el método.** En los sistemas, reemplaza la solución en cada ecuación original y comprueba que el lado izquierdo dé el término independiente (lineales) o cero (no lineales). En Bairstow, reemplaza cada raíz en el polinomio y comprueba que dé cero. En integración, calcula la integral exacta por otro camino, con la antiderivada (la función cuya derivada es la del problema), y la compara con la aproximación. En diferenciación, compara las aproximaciones con la derivada exacta.

**La marca de visto ✔ verde** al lado de una ecuación significa que la cuenta cuadra: lo que da la ecuación con la solución reemplazada coincide con lo que debía dar. Si todas las ecuaciones tienen su visto, el ejercicio está bien resuelto.

**El aviso ⚠** aparece en lugar del visto, o encima de la comprobación, cuando la cuenta no cuadra exactamente. No siempre quiere decir que algo esté mal. Si el método convergió, el aviso «⚠ La solución es aproximada; el residuo depende de la tolerancia usada.» te recuerda que la solución tiene un error pequeño del tamaño de la tolerancia, y eso es normal en un método iterativo. Si el método no convergió, el aviso «⚠ El método no convergió; esta comprobación usa la última aproximación calculada.» te dice que estás comprobando una respuesta que no es la final; ahí sí, la comprobación probablemente no cuadre.

El **residuo máximo** que aparece al final es lo más que se aleja una ecuación de lo que debía dar. Cuanto más cerca de cero, mejor.

## 7.6 Las gráficas

**La gráfica de convergencia** (Figura 13), titulada «Convergencia del error», aparece en todos los métodos. El eje horizontal es el número de la iteración o de la fila; el vertical, el error. La línea azul con puntos es el error de cada vuelta («Error por iteración») y la línea verde punteada es la tolerancia que pediste. Si la línea azul baja, el método se acerca a la respuesta; donde cruza la verde, se cumple la tolerancia. Si sube o se queda horizontal, el método no está convergiendo.

El eje vertical está en **escala logarítmica**, como dice su rótulo «Error (escala log)»: cada raya es diez veces más pequeña que la de arriba (1, 0.1, 0.01, 0.001…, escritos como 1×10⁰, 1×10⁻¹, 1×10⁻², …). Se usa esta escala porque el error se hace muy pequeño muy rápido, y en una escala normal todos los puntos después de la tercera vuelta se verían pegados al cero. En esta escala, una línea recta que baja significa que el error se divide por el mismo número en cada vuelta, que es lo que se espera de un buen método.

**La gráfica de trapecios** (parte inferior de la Figura 21), titulada «Gráfico de los trapecios», dibuja la función en naranja y, debajo, los trapecios en azul sombreado. El área azul es lo que calculó el método; la diferencia entre la curva naranja y el borde de los trapecios es el error. Con los botones «Segmentos: n = 1», «n = 2», «n = 4»… cambias la fila que se dibuja y ves cómo, al haber más trapecios, se ajustan mejor a la curva. Solo se pueden ver las filas con hasta 64 segmentos, porque con más ya no se distinguen de la curva. La leyenda de abajo da el valor exacto y el área de los trapecios, por ejemplo «Trapecios (n = 4): área T = 1.4848». En Simpson la gráfica se llama «Gráfico de las parábolas y cúbicas» y dibuja, en vez de rectas, las parábolas (regla 1/3) o las cúbicas (regla 3/8); unos botones «Simpson 1/3» y «Simpson 3/8» eligen cuál ver.

**La gráfica de segmentos de Romberg**, titulada por ejemplo «Gráfico de segmentos: Trapecio (columna 1)», funciona igual que la del trapecio, pero con unos botones adicionales, «Trapecio (columna 1)», «Simpson 1/3 (columna 2)» y «Boole (columna 3)», que dibujan cómo aproxima la curva cada columna de la tabla triangular. La tabla triangular misma (Figura 24) es la pieza central de Romberg: la primera columna son los trapecios con 1, 2, 4, 8… segmentos, y cada columna siguiente combina dos valores de la anterior para eliminar parte del error. Los valores de la diagonal, resaltados en amarillo, son la mejor aproximación de cada fila. Si pasas el puntero sobre una celda, se marcan las dos celdas de las que sale. Debajo hay una gráfica más, «Convergencia de la diagonal», y un botón «Ver tabla de errores».

![Figura 24 — La tabla triangular de Romberg, con la diagonal resaltada](img/usuario/U-25-tabla-romberg.png)

**La gráfica de diferenciación** (Figura 25), titulada «Gráfica de la aproximación», muestra por qué una fórmula de diferencias aproxima la derivada. Tiene tres selectores encima: «Fórmula» (cuál ver, o «Comparar» para verlas juntas), «Fila» (qué refinamiento dibujar, por ejemplo «Fila 1 (h = 0.1)») y «Paso de la gráfica». En el dibujo aparecen:

- **La curva $f(x)$**, en gris oscuro: la función.
- **La recta tangente**, en verde («Tangente (derivada exacta)»): la recta que toca la curva en $x_0$; su inclinación es la derivada que buscamos.
- **La curva interpolante**, en azul discontinuo: la recta o parábola que la fórmula hace pasar por los puntos que usa.
- **La recta aproximada**, en naranja («Aproximación (pendiente …)»): la recta cuya inclinación es el resultado de la fórmula. Mientras más se parezca a la verde, mejor es la aproximación.
- **Los puntos de la fórmula**, en azul, con su nombre ($x_0 - h$, $x_0 + h$…), y **$x_0$**, marcado con un rombo naranja.
- **La zona sombreada**, en azul claro, que muestra cuánto se dobla la parábola respecto a la recta entre los mismos puntos (en las fórmulas de 3 y 5 puntos), o el triángulo que forma la secante (en las diferencias).

Debajo de la gráfica, una línea compara los valores (por ejemplo «D real (fila 1, h = 0.1) = 22.228787 f′(x₀) exacta = 22.167168») y una frase en negrita dice si la fórmula se pasó o se quedó corta.

![Figura 25 — La gráfica de diferenciación con la vista ilustrativa «Ilustrativo ×5»](img/usuario/U-23-grafica-vista-ilustrativa.png)

**La vista ilustrativa.** Con pasos pequeños, como 0.1, las rectas verde y naranja quedan una encima de la otra y no se ve nada. Por eso el selector «Paso de la gráfica» tiene, además de «Real (h de la fila)», las opciones «Ilustrativo ×2», «Ilustrativo ×5» e «Ilustrativo ×10», que dibujan la primera fila con un paso 2, 5 o 10 veces más grande, solo para que se vea la forma. Mientras está activa, un recuadro lo advierte, por ejemplo: «Vista ilustrativa: el paso es h = 0.5 (5 veces el paso real) solo para que se vea la forma de la curva. Los resultados del ejercicio usan h = 0.1.»

> **Aviso.** La vista ilustrativa **no cambia los resultados**: la tabla, la comprobación y el PDF siguen usando el paso real. Es solo un dibujo exagerado para entender la idea. No copies a tu cuaderno los valores de la línea «D con h = … (ilustrativo)».

## 7.7 Cómo se muestran los números

El sistema calcula con toda la precisión del computador (unos 15 o 16 dígitos), pero para que la pantalla sea legible muestra los números con estas reglas:

- **Como máximo seis decimales.** 2.0072727… se muestra 2.007273, redondeado.
- **Sin ceros de relleno.** Se muestra 0.4 y no 0.400000.
- **Los enteros, sin decimales.** Si el valor redondeado a seis decimales es entero, se muestra 1 y no 1.000000. Por eso la solución de la Figura 11 se ve como 1, 2 y −1, aunque el valor interno sea 0.99999998.
- **Los negativos entre paréntesis al sustituir.** En el paso a paso, un número negativo que se reemplaza en una fórmula va entre paréntesis para que no se confunda con una resta: $(-1)(2.054545)$.
- **El símbolo ≈ cuando un valor está redondeado y eso importa.** Por ejemplo, en la columna h de Romberg verás «≈ 3.141593», porque el paso exacto es $\pi$ y lo que ves es solo una aproximación. El valor exacto aparece en el paso a paso o al pasar el puntero.
- **Los números muy pequeños** que con seis decimales se verían como 0 van acompañados de una nota que da su tamaño real, como «Filas 13: Eₜ es menor que 0.0000005 y con 6 decimales se ve 0».
- **Los ángulos, en radianes**, como ya se dijo en el apartado 6.6.

## 7.8 Descargar el PDF

El botón «Descargar PDF», que está en la tarjeta de respuesta y en la franja fija, genera un documento con el ejercicio completo y lo descarga a tu computador (Figura 14). Incluye los datos de entrada, la configuración (tolerancia y máximo), el estado y el número de iteraciones, la solución, la gráfica de convergencia, la tabla completa de iteraciones (todas las filas, no solo las de la página que estabas viendo) y la comprobación. En diferenciación e integración incluye además las fórmulas usadas con sus glosarios y las tablas de comparación. No incluye el paso a paso desplegable de cada fila.

El archivo queda en la carpeta de descargas del navegador (normalmente la carpeta «Descargas» de Windows), con un nombre que combina el método y la fecha, por ejemplo `jacobi-3x3-2026-11-13.pdf` o `trapecio-funcion-2026-11-13.pdf`. Si descargas dos veces el mismo día, el navegador añade un número al segundo, como `(1)`.

El PDF **siempre sale en modo claro**, con fondo blanco, aunque estés usando el modo oscuro: está pensado para imprimirse o leerse en papel.

## 7.9 El botón «Limpiar»

El botón «Limpiar» está en tres sitios: al lado de «Resolver», en la tarjeta de respuesta y en la franja fija. En los tres hace lo mismo: deja el método como cuando lo abriste: **borra** todos los datos que escribiste, devuelve la tolerancia y el máximo a sus valores por defecto, quita la marca del ejemplo cargado, vuelve a abrir la sección «Ejemplos precargados» y elimina el resultado y los mensajes de error. **No cambia** el método ni la categoría en la que estás, ni el modo claro u oscuro, y no afecta a los PDF que ya descargaste.

Si hay datos escritos o un resultado en pantalla, antes de borrar aparece el diálogo de la Figura 16: «¿Borrar el ejercicio actual? Se perderán los datos y el resultado.», con los botones «Cancelar» y «Limpiar». Si no hay nada que perder (por ejemplo, solo hay un mensaje de error), limpia directamente sin preguntar. Si el formulario ya está vacío, el botón aparece apagado y no hace nada. Después de limpiar, la página sube hasta el formulario y deja el cursor en la primera casilla, lista para escribir.

# 8. Las páginas de teoría

Cada método tiene una página de teoría, a la que llegas desde el menú «Teoría ▾». La Figura 26 muestra el comienzo de la de Jacobi.

![Figura 26 — La página de teoría de Jacobi, desde arriba](img/usuario/U-27-pagina-teoria.png)

Arriba de todo está el mismo encabezado que en «Resolver»: la categoría, el nombre del método y una línea que dice en qué consiste. Debajo empieza un texto largo, organizado con títulos, que se lee de arriba abajo como el capítulo de un libro. Los nombres exactos de las secciones varían de un método a otro, pero todas cubren lo mismo:

- **El fundamento**, que explica el problema que resuelve la categoría y las ideas comunes a sus métodos. En Jacobi se llama «Fundamento común: sistemas $A \cdot x = b$».
- **La definición formal** del método, con su fórmula («Definición formal»). La parte propia del método va en su propio recuadro, sin repetir el nombre del método como título, porque ya está en el encabezado.
- **Cuándo se puede usar**: las condiciones que deben cumplir los datos y las precauciones («Restricciones de aplicabilidad», «Restricciones y precauciones»).
- **El algoritmo**, es decir, la receta paso a paso para aplicar el método a mano («Algoritmo de aplicación»).
- **Un ejemplo resuelto**, con las primeras iteraciones hechas en detalle (en Jacobi, «Ejemplo resuelto: tres iteraciones de Jacobi»). En Simpson, Romberg y la cuadratura gaussiana hay un botón «Resolver este ejemplo» que abre el método en «Resolver» con el ejemplo ya cargado y resuelto.
- **La comparación con otros métodos** de la misma categoría («Jacobi frente a Gauss-Seidel», «Integración numérica: comparación de la categoría»).
- **Las referencias**: los libros de donde salen las fórmulas y los ejemplos («Referencias»).

Las fórmulas de la teoría también tienen sus glosarios «¿Qué significa cada símbolo?» (apartado 7.4), y en algunos métodos hay gráficas interactivas con botones para cambiar el número de segmentos.

**Cuándo conviene leerla.** *Antes* de resolver, si no recuerdas bien el método o no sabes si se puede aplicar a tu ejercicio: las restricciones de aplicabilidad te ahorran intentos fallidos. *Después* de resolver, cuando tengas que explicar o sustentar el resultado ante tu profesor: la definición formal, el algoritmo y la comparación te dan los argumentos, y las referencias te dicen qué citar.

# 9. Modo claro y modo oscuro

El sistema tiene dos juegos de colores: el modo claro, con fondo blanco, y el modo oscuro, con fondo azul oscuro, que cansa menos la vista de noche o en salas con poca luz. La Figura 27 muestra el resultado del capítulo 5 en modo oscuro.

![Figura 27 — El resultado de Jacobi en modo oscuro](img/usuario/U-18-modo-oscuro.png)

**Dónde está el botón.** Es el cuadrito del extremo derecho de la barra superior (Figura 4). En modo claro muestra una luna y su texto de ayuda dice «Activar modo oscuro»; en modo oscuro muestra un sol y dice «Activar modo claro». Un clic cambia de uno a otro al instante, sin perder nada de lo que tienes en pantalla.

**Qué recuerda el sistema.** La primera vez, el sistema usa el mismo modo que tenga configurado tu Windows o tu celular. Si eliges uno con el botón, el navegador lo recuerda y la próxima vez que abras el sistema, en ese mismo navegador, aparecerá en el modo que elegiste. Si usas otro navegador u otro computador, o borras los datos de navegación, vuelve a seguir la configuración del equipo.

**Qué no cambia.** El modo solo cambia los colores de la pantalla. Los resultados, los números y las tablas son exactamente los mismos en los dos modos, y el PDF siempre sale en modo claro (apartado 7.8). Los colores con significado se mantienen: en modo oscuro el azul y el verde del paso a paso se ven más claros, pero siguen significando lo mismo.

# 10. Problemas y soluciones

## 10.1 Mensajes que muestra el sistema

Cuando algo no está bien, el sistema te lo dice con un mensaje. Los mensajes aparecen en tres lugares distintos, y saber dónde mirar ayuda:

- **Junto al campo**, en rojo, justo debajo de la casilla que tiene el problema, que también se pone roja. Pasa con los números mal escritos y con las funciones o ecuaciones mal escritas, y aparece mientras escribes, antes de pulsar «Resolver».
- **Encima de los botones**, en un recuadro rojo entre el formulario y los botones «Resolver» y «Limpiar», después de pulsar «Resolver». Pasa cuando los datos no cumplen una condición del método. La página se mueve sola hasta el mensaje para que lo veas. Mientras haya un mensaje aquí, no hay resultado.
- **Dentro del resultado**, en recuadros amarillos con ⚠ en la tarjeta de respuesta y en el resumen, o en un recuadro rojo sobre la tabla. Pasa cuando el método sí corrió, pero algo merece atención, como no haber alcanzado la tolerancia. Aquí sí hay resultado.

Las tablas siguientes recogen los mensajes que puede mostrar el sistema, copiados tal como aparecen. Los números y nombres que contienen (la fila, la ecuación, el grado, la tolerancia) cambian según tus datos; en la tabla aparecen con un valor de ejemplo. Cuando un mensaje se refiere a una ecuación o a la función, el recuadro rojo lo antepone con «Ecuación 1: » o «f(x): », por ejemplo «Ecuación 1: La expresión no está bien formada.».

### Problemas al escribir la función o la ecuación

La Figura 28 muestra cómo se ven estos mensajes: la casilla en rojo con el mensaje debajo, mientras escribes, y el mismo mensaje en el recuadro rojo si pulsas «Resolver».

![Figura 28 — El mensaje de error de una función mal escrita («sen» en vez de «sin»)](img/usuario/U-28-error-expresion.png)

| Lo que dice el sistema | Por qué aparece | Qué hacer |
|---|---|---|
| 'sen' no es una variable declarada ni una función conocida. | Escribiste un nombre que el sistema no conoce: una función en español (`sen`, `tg`, `raiz`), una función que no existe en el sistema (`sec`, `cbrt`), dos letras pegadas (`xy`), una variable que no declaraste (`z`) o un nombre en mayúsculas (`Sin`, `PI`). | Usa los nombres de la tabla del apartado 6.6 en minúsculas; pon `*` entre letras (`x*y`); declara todas las variables que uses. |
| La expresión no está bien formada. | Falta o sobra algo: un paréntesis sin cerrar, un operador al final (`3*`), una función sin paréntesis (`sin x`, `ln x`) o una potencia mal escrita (`sin^2(x)`). | Revisa los paréntesis y los operadores; escribe `sin(x)^2` en lugar de `sin^2(x)`. |
| Usa un único '=' para separar los dos lados. | La ecuación tiene dos o más signos igual, como `x + y = 3 = 2`. | Deja un solo `=`. |
| Símbolo no permitido: '\|'. | Usaste un símbolo que no se acepta, como `\|`, `!`, `#` o `²`. | Usa `abs(x)` para el valor absoluto y `x^2` para el cuadrado. |
| El resultado no es una expresión matemática. | Usaste coma decimal dentro de una función, como `1,5*x`. | Usa punto decimal: `1.5*x`. |
| Número no válido: hay dos números seguidos ('2' y '3'). Revisa ceros a la izquierda o puntos decimales, o sepáralos con un operador. | Escribiste dos números separados solo por un espacio (`2 3`), un número con dos puntos (`1.5.2`) o con ceros a la izquierda (`007`). | Pon el operador que falta (`2*3`) o corrige el número. |
| La expresión contiene una división entre cero. | Escribiste una división cuyo divisor es cero, como `1/0`. | Corrige el divisor. |
| La expresión contiene un exponente demasiado grande (el máximo permitido es 1000). | Usaste una potencia con un exponente mayor que 1000, como `2^5000`. | Usa exponentes más pequeños. |
| La expresión contiene un número demasiado grande (el máximo permitido es 1e+100). | Escribiste un número con más de cien cifras. | Usa números más pequeños o cambia de unidades. |
| La expresión supera el máximo de 300 caracteres. | La función o ecuación es demasiado larga. | Simplifícala antes de escribirla. |
| La expresión tiene demasiados paréntesis anidados. | Hay más de 30 paréntesis uno dentro de otro. | Simplifica la expresión. |
| La expresión está anidada a más de 40 niveles. | La expresión tiene demasiadas operaciones metidas unas dentro de otras. | Simplifica la expresión. |
| La expresión debe escribirse en una sola línea. | Pegaste un texto con saltos de línea. | Borra los saltos de línea. |
| La expresión contiene un carácter no permitido. | Pegaste un carácter invisible o especial desde otro programa. | Borra la expresión y escríbela a mano. |
| La expresión está vacía. | Dejaste la ecuación o el polinomio en blanco. | Escríbela. |
| Ecuación 2: está vacía. | Una de las casillas de ecuación quedó en blanco. | Escribe la ecuación o quítala con la «×». |
| Escribe la función f(x). | Dejaste en blanco la función en diferenciación o integración. | Escribe la función. |
| Escribe sólo la expresión de f(x), sin '=' (o en la forma f(x) = …). | En diferenciación o integración escribiste algo con un igual que no es `f(x) = …`. | Escribe solo la expresión, por ejemplo `ln(x)`. |
| f(x): 'y' no es una variable declarada ni una función conocida. | En diferenciación o integración escribiste `y = …` o usaste otra letra que no es `x`. | Escribe solo la expresión en `x`. |
| Los argumentos de f(x) no coinciden con las variables declaradas (x, y). | En un sistema no lineal empezaste una ecuación con `f(x) =`. | Escribe la ecuación sin nombre de función, por ejemplo `x^2 + y - 1 = 0`. |
| 'x + seno(y) - 3 = 0' no es un nombre de variable válido. | En Punto Fijo escribiste la ecuación en la casilla «Variable», o en Newton escribiste algo que no son nombres en «Variables, en orden». | Escribe en esas casillas solo nombres de variables, como `x` o `x, y`. |
| 'e' está reservado y no puede usarse como variable. | Usaste `e` o `pi` como nombre de variable. | Usa otra letra. |
| La variable 'x' está repetida. | Declaraste dos veces la misma variable. | Usa un nombre distinto para cada incógnita. |
| Los nombres de las variables no pueden estar vacíos. | Dejaste una casilla «Variable» en blanco o pusiste dos comas seguidas. | Escribe el nombre que falta. |
| La ecuación no es válida. | La vista previa no pudo interpretar la ecuación y no recibió una explicación más precisa. | Revisa la ecuación con la tabla del apartado 6.6. |

### Números mal escritos en los campos

| Lo que dice el sistema | Por qué aparece | Qué hacer |
|---|---|---|
| Escribe un número (2.5) o una fracción (6/7). | Escribiste en una casilla numérica algo que no es un número, como una letra. | Escribe un número o una fracción. |
| El denominador de una fracción no puede ser cero. | Escribiste una fracción como `1/0`. | Corrige el denominador. |
| Hay campos del sistema con un valor inválido (marcados en rojo). Corrígelos antes de resolver. | Pulsaste «Resolver» con alguna casilla de la matriz o del vector inicial en rojo (sistemas lineales). | Busca las casillas rojas y corrígelas. |
| El punto inicial x0 tiene un valor inválido (marcado en rojo). Corrígelo antes de resolver. | Igual que el anterior, en los sistemas no lineales. | Corrige la casilla roja del punto inicial. |
| Hay coeficientes o valores iniciales con un valor inválido (marcados en rojo). Corrígelos antes de resolver. | Igual que el anterior, en Bairstow. | Corrige la casilla roja. |
| Hay campos con un valor inválido (marcados en rojo). Corrígelos antes de resolver. | Igual que el anterior, en diferenciación e integración. | Corrige la casilla roja. |
| A valid number is required. | Dejaste vacía la tolerancia, o escribiste algo que no es un número. (Este mensaje sale en inglés: significa «Se requiere un número válido».) | Escribe la tolerancia, por ejemplo `0.000001`. |
| A valid integer is required. | Dejaste vacío el máximo de iteraciones. (En inglés: «Se requiere un número entero válido».) | Escribe un número entero, por ejemplo `100`. |
| Ensure this value is greater than or equal to 0. | Escribiste una tolerancia negativa. (En inglés: «Asegúrate de que el valor sea mayor o igual que 0».) | Escribe una tolerancia positiva. |
| Ensure this value is greater than or equal to 1. | Escribiste 0 o un número negativo como máximo de iteraciones. (En inglés: «… mayor o igual que 1».) | Escribe 1 o más; el sistema hace igualmente al menos 6. |
| La tolerancia del error estimado debe ser mayor que 0. | En diferenciación o integración la tolerancia es 0 o negativa. | Escribe un número positivo, como `0.000001`. |
| La tolerancia εs debe ser mayor que 0 (está en porcentaje). | En Bairstow la tolerancia es 0 o negativa. | Escribe un porcentaje positivo, como `0.0001`. |
| Falta el valor de x₀. | Dejaste vacío el punto donde se deriva. | Escribe x₀. |
| x₀ debe ser un número real finito de magnitud razonable. | El valor de x₀ no es un número utilizable (por ejemplo, es enorme). | Escribe un número normal. |
| El paso inicial h₀ debe ser un número mayor que 0. | Escribiste 0 o un número negativo como paso. | Escribe un paso positivo; si no sabes, `0.1`. |
| Falta el límite inferior a. | Dejaste vacío el límite a (o el b: «Falta el límite superior b.»). | Escribe el límite. |
| El límite inferior a debe ser menor que el límite superior b. | Escribiste a mayor o igual que b. | Intercambia los límites; si necesitas la integral de b a a, cámbiale el signo al resultado. |

### Datos que no cumplen una condición del método

La Figura 29 muestra un ejemplo: en Simpson, con la regla «Ambas», se escribió 3 como «n₀ de Simpson 1/3», que debe ser par.

![Figura 29 — El mensaje de una condición del método que no se cumple (número de segmentos impar en Simpson 1/3)](img/usuario/U-29-error-validacion.png)

| Lo que dice el sistema | Por qué aparece | Qué hacer |
|---|---|---|
| El sistema debe tener al menos 3 variables (n >= 3). | En un sistema lineal pusiste menos de 3 incógnitas. | Usa 3 o más. Un sistema de 2 ecuaciones se resuelve más fácil a mano. |
| La diagonal principal no puede tener ceros (filas problemáticas: [1]); no es posible despejar esa variable. | Hay un cero en la diagonal (en el ejemplo, en la fila 1) y no se puede despejar esa incógnita. | Cambia el orden de las ecuaciones a mano para que la diagonal no tenga ceros. |
| El elemento de la diagonal a[1][1] es cero; no es posible despejar la variable x1. | Lo mismo, detectado en el momento de resolver. | Igual que el anterior. |
| El sistema debe tener entre 2 y 6 ecuaciones (tiene 7). | En un sistema no lineal hay menos de 2 o más de 6 ecuaciones. | Ajusta el número de ecuaciones. |
| Debe haber una variable por ecuación (2 ecuaciones, 3 variables). | El número de variables declaradas no coincide con el de ecuaciones. | Agrega o quita ecuaciones o variables. |
| El punto inicial x0 debe tener exactamente 2 valores. | Aparece junto al anterior: el punto inicial no tiene un valor por variable. | Corrige primero las variables; el punto inicial se ajusta solo. |
| La ecuación 1 admite 2 despejes reales de x (x = -sqrt(11 - y); x = sqrt(11 - y)), así que el despeje automático es ambiguo. Reescribe la ecuación para que x tenga un único despeje, por ejemplo con x sola en el lado izquierdo: x = ... | En Punto Fijo, la variable aparece de forma que tiene dos despejes posibles (por ejemplo, al cuadrado). | Escribe la ecuación ya despejada con el signo que quieres, por ejemplo `x = sqrt(11 - y)`. |
| No fue posible despejar x de la ecuación 1 de forma automática. x aparece con grado 5 y el máximo admitido para el despeje automático es 4. Reescribe la ecuación de otra forma. | En Punto Fijo, la variable aparece con una potencia mayor que 4. | Despeja tú la variable de otra forma, o usa Newton, que no necesita despejar. |
| No fue posible despejar x de la ecuación 1 de forma automática. Reescribe la ecuación de otra forma. | En Punto Fijo, el sistema no encontró cómo despejar la variable. | Escribe la ecuación ya despejada (`x = …`) o usa Newton. |
| La ecuación 1 no contiene ninguna de las variables declaradas: su fila del Jacobiano sería de ceros. | En Newton, una ecuación no tiene ninguna incógnita. | Revisa la ecuación y los nombres de las variables. |
| La variable y no aparece en ninguna ecuación: su columna del Jacobiano sería de ceros y el sistema no tendría solución única. | En Newton declaraste una variable que no usas. | Quita esa variable o revisa las ecuaciones. |
| El polinomio es de grado 2: se resuelve directamente con la fórmula cuadrática. Bairstow es para grado ≥ 3. | En Bairstow el polinomio tiene grado 2 (también hay mensajes para grado 1 y para un polinomio constante). | Resuélvelo con la fórmula cuadrática o despejando. |
| El polinomio es de grado 11; esta aplicación admite hasta grado 10. | El polinomio tiene grado mayor que 10. | Usa un polinomio de grado 3 a 10. |
| La expresión no es un polinomio en x: sólo se admiten sumas de términos c·xᵏ con k entero no negativo (no funciones como sin(x), sqrt(x) o exp(x), ni divisiones entre x, ni exponentes negativos o no enteros). | Escribiste algo que no es un polinomio. | Escribe solo potencias enteras de x con sus coeficientes. |
| El polinomio sólo puede depender de x: 'y' no es una variable declarada ni una función conocida. | Usaste otra letra en el polinomio. | Escríbelo en x. |
| El coeficiente principal (el de la potencia más alta) no puede ser 0. Quita los ceros a la izquierda o baja el grado del polinomio. | En la pestaña «Coeficientes», el primero es 0. | Baja el grado o corrige el primer coeficiente. |
| Faltan los coeficientes del polinomio. | No escribiste los coeficientes. | Escríbelos. |
| La tabla debe tener entre 3 y 20 puntos (tiene 2). | La tabla de diferenciación tiene muy pocos o demasiados puntos para el método. | Agrega o quita puntos. |
| Faltan los puntos (xᵢ, yᵢ) de la tabla. | La tabla está vacía. | Escribe los puntos. |
| Fila 2: falta el valor de y. | Una fila de la tabla tiene una casilla vacía. | Complétala o quita la fila. |
| Fila 2: los valores de x deben ser estrictamente crecientes (x2 = 0 no es mayor que x1 = 0). | Un valor de x es igual o menor que el anterior. | Ordena la tabla de menor a mayor y quita los repetidos. |
| La fórmula de 3 puntos necesita datos igualmente espaciados: entre la fila 2 y la 3 el espaciado es 1.5 y el de la primera pareja es 1. | Los x de la tabla no están a la misma distancia (también sale con «La fórmula de 5 puntos»). | Corrige los datos o usa las diferencias progresiva y regresiva, que aceptan espaciado desigual. |
| f(x) no está definida en x = 0 (punto x₀). | La función no se puede calcular en ese punto, por ejemplo `ln(x)` en 0. Puede venir acompañado de otros puntos vecinos, como «(punto x₀ − h)». | Elige otro x₀, o un h₀ más pequeño si el problema está en un punto vecino. |
| h₀ es demasiado pequeño para la precisión de la computadora: x₀ + h₀ es igual a x₀. | El paso es tan pequeño que el computador no lo distingue de cero. | Usa un paso más grande, como `0.1`. |
| El máximo de refinamientos de h debe estar entre 6 y 30. | El máximo en diferenciación está fuera de rango. | Escribe un número entre 6 y 30. |
| Los segmentos iniciales n₀ deben ser un entero entre 1 y 1000. | En el trapecio, n₀ está fuera de rango o no es entero. | Escribe un entero entre 1 y 1000. |
| Simpson 1/3 necesita un número par de segmentos, porque cada parábola ocupa 2 segmentos (n₀ = 3). | En Simpson 1/3 escribiste un n₀ impar. | Escribe un número par, como 2 o 4. |
| Simpson 3/8 necesita un número de segmentos múltiplo de 3, porque cada cúbica ocupa 3 segmentos (n₀ = 4). | En Simpson 3/8 escribiste un n₀ que no es múltiplo de 3. | Escribe 3, 6, 9… |
| El máximo de refinamientos debe estar entre 6 y 22. | El máximo del trapecio o de Simpson está fuera de rango (en Romberg: «El máximo de filas debe estar entre 6 y 20.»; en Gauss: «El máximo de puntos debe estar entre 6 y 20.»). | Escribe un número dentro del rango que dice el rótulo del campo. |
| Simpson necesita datos igualmente espaciados: entre la fila 2 y la 3 el espaciado es 0.2 y el de la primera pareja es 0.1. Con datos de espaciado desigual puedes usar el método del trapecio. | La tabla de Simpson tiene separaciones distintas (Romberg tiene un mensaje igual). | Corrige los datos o usa el trapecio. |
| Romberg necesita 2ᵐ + 1 puntos igualmente espaciados (3, 5, 9, 17 o 33), porque cada fila duplica el número de segmentos. Tienes 4 puntos: puedes usar el trapecio o Simpson. | La tabla de Romberg no tiene 3, 5, 9, 17 o 33 puntos. | Ajusta la tabla o usa otro método. |
| Simpson 1/3 necesita un número par de segmentos, porque cada parábola ocupa 2 segmentos, y la tabla tiene n = 9. Elige «Ambas» (combina 1/3 y 3/8) o «Simpson 3/8» (n es múltiplo de 3). | En modo tabla elegiste una regla que no encaja con el número de segmentos de la tabla (hay un mensaje equivalente para Simpson 3/8). | Elige la regla que te propone el mensaje. |
| Los subintervalos N deben ser un entero entre 1 y 50. | En la cuadratura gaussiana, N está fuera de rango. | Escribe un entero entre 1 y 50. |
| La cuadratura gaussiana necesita evaluar la función en puntos especiales (las raíces de los polinomios de Legendre), que son números irracionales; por eso no funciona con una tabla de datos. Para datos, usa el trapecio, Simpson o Romberg. | La cuadratura gaussiana no admite tablas. | Usa otro método de integración para tus datos. |
| f(x) no está definida en x = 0 (límite a). | En el trapecio, Simpson o Romberg, la función no se puede calcular en un extremo del intervalo, por ejemplo `1/x` en 0. | Cambia el intervalo o usa la cuadratura gaussiana, que no evalúa los extremos. |

### El método no llega al resultado

Estos mensajes aparecen dentro del resultado: el método corrió, pero no terminó como esperabas. La Figura 30 muestra el caso más común: el método de Jacobi del capítulo 5 con una tolerancia de 0.000000001 y un máximo de 6 iteraciones.

![Figura 30 — El aviso de que el método no alcanzó la tolerancia en el máximo de iteraciones](img/usuario/U-30-aviso-no-convergencia.png)

| Lo que dice el sistema | Por qué aparece | Qué hacer |
|---|---|---|
| ⚠ No alcanzó la tolerancia: se detuvo tras 6 iteraciones. Error final: 0.001299. Los valores mostrados son los últimos calculados, no una solución. | Aparece en la tarjeta de respuesta, en amarillo, siempre que el método se detiene sin alcanzar la tolerancia. Los valores en letra grande son solo lo último que calculó. | Lee el aviso que lo acompaña en el resumen: dice por qué se detuvo. |
| ⚠ El método no alcanzó la tolerancia solicitada (1e-09) dentro de 6 iteraciones. | Se acabaron las iteraciones antes de que el error bajara de la tolerancia. La tolerancia aparece en notación científica: 1e-09 es 0.000000001. | Sube el «Máximo de iteraciones». Si con muchas iteraciones el error no baja, mira la gráfica: el método puede no converger con esos datos. |
| ⚠ El método no convergió. Iteración final: 6 · Error final: 0.001299 · Tolerancia solicitada: 0 | Acompaña al anterior, en rojo sobre la tabla, con la última iteración y su error. Ojo: si la tolerancia tiene más de seis decimales, aquí se ve redondeada a 0. | Igual que el anterior. |
| ⚠ La matriz no es diagonalmente dominante en la(s) fila(s) [1, 2, 3]. Esta es una condición suficiente (no necesaria) de convergencia: el método puede converger o no. | El sistema lineal no cumple la condición que garantiza que el método funcione. | Marca «Reordenar filas automáticamente…»; si no basta, reordena a mano o resuelve con otro método. Si el resultado dice «Convergió», puedes usarlo. |
| ⚠ En la iteración 1, y = g_2(...) no dio un número real finito (resultó complejo, infinito o fuera del dominio de una función). El método se detuvo sin converger; prueba con otro punto inicial o reescribe las ecuaciones. | En Punto Fijo, una cuenta no se pudo hacer: por ejemplo, la raíz de un número negativo o una división entre cero. | Cambia el punto inicial o despeja la ecuación de otra forma. |
| ⚠ El Jacobiano es singular en la iteración 1, no se puede continuar: su determinante en x^(0) es (prácticamente) cero, así que el sistema J·Δx = −F no tiene solución única. Prueba con otro punto inicial. | En Newton, en ese punto las ecuaciones no dan información para avanzar (pasa mucho al empezar en cero). | Cambia el punto inicial, por ejemplo a 1 y 1. |
| ⚠ En la iteración 3, F, el Jacobiano o el paso Δx no dieron números reales finitos (resultó complejo, infinito o fuera del dominio de una función). El método se detuvo sin converger; prueba con otro punto inicial. | En Newton, una cuenta se salió del dominio de una función o creció sin control. | Cambia el punto inicial. |
| ⚠ El factor 1 no alcanzó la tolerancia εs = 0.0001 % en 100 iteraciones. Se muestran las raíces encontradas hasta ese momento. | En Bairstow, un factor no convergió. | Cambia r₀ y s₀ o sube el máximo de iteraciones. |
| ⚠ Factor 1, iteración 2: el determinante D del sistema 2×2 es (prácticamente) cero, no se puede continuar. Prueba con otros r₀ y s₀. Se muestran las raíces encontradas hasta ese momento. | En Bairstow, el método quedó sin poder avanzar desde esos valores iniciales. | Prueba otros r₀ y s₀, como 0.5 y −0.5. |
| ⚠ Factor 1, iteración 4: aparecieron valores no finitos (los valores crecieron sin control). Prueba con otros r₀ y s₀. Se muestran las raíces encontradas hasta ese momento. | En Bairstow, los valores se dispararon. | Prueba otros r₀ y s₀. |
| ⚠ No se alcanzó la tolerancia del error estimado (0.000001) en 6 refinamientos. Aumenta el máximo de refinamientos o la tolerancia. | En diferenciación o integración, se acabaron las filas. (En diferenciación dice «refinamientos de h»; en Romberg, «filas»; en Gauss, «con 12 puntos», y sugiere también aumentar N.) | Sube el máximo o haz la tolerancia menos exigente. |
| ⚠ El error de redondeo ya es comparable con el de truncamiento: reducir más h no mejora la aproximación. | En diferenciación, el paso se hizo tan pequeño que las cuentas empiezan a perder decimales (en integración: «aumentar n no mejora la aproximación»). | No es un error tuyo: la mejor aproximación ya está en la tabla. Usa una tolerancia menos exigente. |
| ⚠ h es demasiado pequeño para la precisión de la computadora (fila 20): x₀ ± h ya es igual a x₀, así que se detuvo el refinamiento. | En diferenciación, el paso llegó al límite de lo que el computador puede representar. | Usa una tolerancia menos exigente o menos refinamientos. |
| ⚠ La diagonal mejora lentamente: f puede no ser suave en [a, b] (por ejemplo, una raíz cuadrada en 0 o un valor absoluto). Romberg funciona mejor con funciones suaves. | En Romberg, la función tiene un punto con una esquina o una pendiente infinita. | El resultado es válido pero cuesta más; para estas funciones considera la cuadratura gaussiana. |
| ⚠ Se alcanzó el máximo de 2097152 segmentos (fila 22): se detuvo el refinamiento. | En el trapecio o Simpson, el número de segmentos llegó al límite. | Usa una tolerancia menos exigente. |
| ⚠ f(x) no está definida en x = 0, dentro de [-1, 1]: la integral puede no existir. | La función se rompe dentro del intervalo de integración. | Revisa el enunciado; la integral puede no tener sentido en ese intervalo. |
| ⚠ No se pudo calcular la integral exacta ni un valor de referencia: no se muestran el error verdadero, el relativo ni la razón. | La integral no tiene una fórmula exacta que el sistema pueda obtener. | No es un error: el resultado del método es válido; solo faltan las columnas de error verdadero. |
| ⚠ La integración simbólica superó el límite de 3 s: se usa un valor de referencia (cálculo numérico de alta precisión). | Encontrar la integral exacta tardaba demasiado, así que el sistema la reemplazó por un cálculo muy preciso. | No hace falta hacer nada. |
| ⚠ f''(x) no es finita en todo [a, b]: no se muestra la cota del error. | La segunda derivada se dispara en el intervalo, así que la cota teórica no se puede calcular. | No hace falta hacer nada; el resto del resultado es válido. |
| ⚠ f no es derivable en x₀: no se muestran el error real ni la razón entre errores. | En diferenciación, la función tiene una esquina en x₀ (como `abs(x)` en 0). | La derivada no existe ahí; revisa el enunciado. |
| ⚠ Punto 3: el dato no coincide con la función (y = 2.5, f(x) = 2.4); puede ser un error de captura. | En modo tabla con «Función para comparar», un dato no coincide con la función. | Revisa ese punto de la tabla. |
| ⚠ Cota no disponible desde m = 6: la cota necesita la derivada de orden 2m de f, que para muchos puntos se vuelve muy larga de calcular; el error verdadero y el error estimado siguen disponibles. | En la cuadratura gaussiana, la cota solo se calcula para pocos puntos. | No hace falta hacer nada. |
| ⚠ El método no convergió; esta comprobación usa la última aproximación calculada. | En la comprobación, porque el método no llegó a la tolerancia. | Resuelve el problema de convergencia primero. |
| ⚠ La solución es aproximada; el residuo depende de la tolerancia usada. | En la comprobación, cuando la solución no es exacta. | Normal; si quieres un residuo más pequeño, usa una tolerancia más pequeña. |

Algunos recuadros amarillos no avisan de ningún problema, sino que informan sobre cómo se hizo el cálculo, por ejemplo «Cada factor obtenido por Bairstow arranca con los mismos valores iniciales r₀ = -1 y s₀ = -1 dados por el usuario.», «Paso previo: se extrajo el factor x^1 (1 raíz/raíces x = 0) y se continúa con el polinomio reducido.» o «El espaciado de los datos no es uniforme: cada fórmula usa su propio h.». Léelos, pero no tienes que hacer nada.

### Problemas de conexión

| Lo que dice el sistema | Por qué aparece | Qué hacer |
|---|---|---|
| No fue posible cargar los métodos desde el servidor. Verifica que el backend esté corriendo. | Al abrir o recargar la página, el servidor de cálculo no respondió. | Espera un minuto y recarga con F5; si sigue, sigue los pasos del apartado 2.3. |
| No fue posible cargar los ejemplos desde el servidor. | Al abrir un método, no llegaron sus ejemplos precargados. | Recarga la página con F5. |
| No fue posible conectar con el servidor. Verifica que el backend esté corriendo. | Al pulsar «Resolver», el navegador no recibió ninguna respuesta. | Comprueba que el sistema siga encendido (apartado 2.3) y vuelve a pulsar «Resolver». |
| Un recuadro rojo muy largo lleno de letras sueltas, una por renglón, que juntas dicen «502 Bad Gateway». | Al pulsar «Resolver», el servidor de cálculo estaba apagado. Unos diez segundos después aparece este recuadro en lugar de un mensaje claro. | Es el mismo caso que el anterior: el servidor no está funcionando. Sigue los pasos del apartado 2.3 y vuelve a resolver. |
| No fue posible verificar la ecuación: sin conexión con el servidor. | La vista previa de la ecuación no pudo consultar al servidor. | Comprueba que el sistema esté encendido; la vista previa vuelve sola al escribir de nuevo. |
| Ocurrió un error al validar los datos. | El servidor rechazó los datos sin dar una explicación. | Revisa los datos, o pulsa «Limpiar», carga un ejemplo y vuelve a intentarlo. |

## 10.2 Cosas que pasan sin mensaje de error

**La página no abre.** Escribes `http://localhost:8080` y el navegador dice que no puede acceder al sitio. Casi siempre es porque el sistema no está encendido: Docker Desktop está cerrado o no ejecutaste `iniciar.bat`. Abre Docker Desktop, espera a que diga «Engine running» y ejecuta `iniciar.bat`. Revisa también que hayas escrito `http://` y no `https://`, y el número 8080 completo.

**Se queda cargando y no pasa nada.** Pulsas «Resolver», el botón muestra un círculo que gira y dice «Resolviendo…», y no aparece nada durante muchos segundos. Algunos cálculos son lentos de verdad: la integración de Romberg con 20 filas y una tolerancia muy pequeña puede tardar casi un minuto. Si pasan más de diez segundos y después aparece un recuadro rojo con letras sueltas, el servidor se apagó (ver la tabla anterior). Si en cambio el botón vuelve a decir «Resolver» y aparece el resultado, solo era un cálculo pesado: la primera integral de una función complicada puede tardar unos segundos mientras el sistema busca su integral exacta, y las repeticiones son más rápidas. Si quieres cancelar la espera, pulsa «Limpiar».

**El resultado tiene muchas más filas de las que esperabas.** Tu libro llega a la respuesta en 8 vueltas y el sistema hace 40. Normalmente es porque la tolerancia es más exigente que la del libro: con 0.000001 el método sigue hasta tener seis decimales correctos, mientras que muchos libros paran con dos o tres. Escribe en «Tolerancia» la misma que usa el libro. También puede ser que el punto de partida sea distinto: revisa el vector inicial.

**El resultado tiene exactamente seis filas aunque la tolerancia sea grande.** Escribes una tolerancia de 0.5, o empiezas justo en la solución, y la tabla igual tiene seis filas. Es intencional: como explica el capítulo 6, ningún método se detiene antes de la sexta iteración, para que siempre haya suficiente información en la tabla. Las filas de más no cambian la respuesta; simplemente confirman que ya no se mueve. Si tu profesor pide solo tres iteraciones, copia las tres primeras filas.

**La tabla de un método de diferenciación muestra «≈» en el paso.** En la columna h aparece algo como «≈ 0.033333». Quiere decir que el paso no tiene una escritura exacta con seis decimales (por ejemplo, 1/30) y que lo que ves está redondeado. El cálculo usa el valor exacto, que puedes ver en el paso a paso de la fila. Una nota debajo de la tabla lo recuerda: «Los valores de h con ≈ están redondeados a 6 decimales; su valor exacto está en el paso a paso.»

**La gráfica se ve casi recta.** En la gráfica de diferenciación, la curva, la tangente y la recta aproximada parecen una sola línea. Es lo esperado: con un paso pequeño las tres casi coinciden, y por eso la aproximación es buena. Para ver la forma, usa la vista ilustrativa (apartado 7.6). En la gráfica de convergencia, una línea recta que baja es lo normal por la escala logarítmica; una línea horizontal significa que el error no está bajando.

**El PDF no se descarga.** Pulsas «Descargar PDF» y no pasa nada visible. Revisa la carpeta de descargas: muchos navegadores descargan sin preguntar y solo muestran un pequeño aviso en una esquina. Si el navegador tiene bloqueadas las descargas automáticas, aparece un icono en la barra de direcciones para permitirlas; permítelas para `localhost`. Si usas un modo de navegación con restricciones, prueba en una ventana normal.

**Aparece «Esta página no existe».** Abriste un favorito o una dirección que el sistema no reconoce: un método escrito con otra palabra, una letra de más o una dirección de una versión anterior. Debajo del mensaje hay dos botones: «Ver los métodos» abre el menú para que elijas el método, e «Ir al inicio» te lleva a Jacobi. Si era un favorito, vuelve a guardarlo desde la página correcta.

**El navegador sigue mostrando el icono o la versión anterior.** Después de que alguien actualiza el sistema, ves el icono viejo en la pestaña o pantallas que ya no deberían existir. El navegador guarda copias de las páginas para cargarlas más rápido. Recarga forzando una copia nueva con Ctrl + F5. Si quien actualizó no reconstruyó el sistema con `reconstruir.bat`, recargar no basta (apartado 2.4).

**El sistema da un resultado distinto al del cuaderno por redondeo.** Tus números coinciden con los del sistema en las primeras vueltas, pero a partir de la cuarta o quinta empiezan a diferir en el último decimal. Es por el redondeo: a mano solemos redondear cada resultado a cuatro o seis decimales y seguir con ese valor redondeado, mientras que el sistema arrastra todos los decimales. Las pequeñas diferencias se acumulan. Si la diferencia es solo en el último decimal, los dos resultados son correctos. Para comparar mejor, haz tus cuentas con más decimales o usa el paso a paso del sistema como guía.

# 11. Preguntas frecuentes

| Pregunta | Respuesta |
|---|---|
| ¿Hace falta internet? | Solo la primera vez que enciendes el sistema, para descargar sus componentes. Después funciona sin conexión. |
| ¿Se guardan mis ejercicios? | No. El sistema no guarda nada: si cierras la pestaña, limpias o cambias de método, el ejercicio se pierde. Para conservarlo, descarga el PDF. |
| ¿Puedo tener dos pestañas abiertas? | Sí. Cada pestaña es independiente, así que puedes resolver el mismo ejercicio con dos métodos a la vez para compararlos, o tener la teoría en una y el ejercicio en otra. |
| ¿Puedo usarlo desde el celular? | Sí, si el celular está en la misma red Wi-Fi que el computador donde está encendido el sistema. Escribe en el navegador del celular `http://` seguido de la dirección IP del computador y `:8080`, por ejemplo `http://192.168.1.20:8080`. La IP del computador se ve escribiendo `ipconfig` en la ventana de comandos de Windows, en la línea «Dirección IPv4». La primera vez, Windows puede pedir permiso para Docker en el firewall: permítelo en redes privadas. La pantalla se adapta al celular (apartado 4.4). |
| ¿Por qué un método converge y otro no con el mismo ejercicio? | Cada método tiene condiciones distintas. Por ejemplo, Gauss-Seidel puede converger donde Jacobi no; Newton suele converger más rápido que Punto Fijo, pero necesita un buen punto de partida. La página de teoría de cada método explica sus condiciones en «Restricciones de aplicabilidad». |
| ¿Qué método me conviene para mi ejercicio? | Usa el Anexo B. Si el enunciado nombra el método, usa ese. |
| ¿Puedo cambiar los ejemplos precargados? | No desde la pantalla. Pero puedes cargar un ejemplo, modificar los datos que quieras y resolver: el ejemplo original no cambia. |
| ¿Cuántos decimales usa por dentro? | Toda la precisión del computador, unos 15 o 16 dígitos. Solo la pantalla y el PDF redondean a seis decimales (apartado 7.7). |
| ¿Puedo imprimir el resultado? | Sí. Descarga el PDF e imprímelo desde tu lector de PDF. El PDF sale en modo claro, pensado para papel. |
| El profesor pide más iteraciones de las que salen, ¿qué hago? | El método se detiene cuando cumple la tolerancia. Para que haga más vueltas, escribe una tolerancia más pequeña (por ejemplo 0.0000000001) y sube el máximo de iteraciones. El sistema hará vueltas hasta cumplirla o llegar al máximo. |
| El profesor pide exactamente cierto número de iteraciones, ¿se puede? | Escribe ese número en «Máximo de iteraciones» y una tolerancia muy pequeña: el método hará exactamente esas vueltas y te avisará de que no alcanzó la tolerancia, lo cual en ese caso es esperable. Recuerda que el mínimo es 6. |
| ¿Los resultados sirven para entregar? | Sirven para verificar tu trabajo y como apoyo, y el PDF muestra el procedimiento completo. Si se pueden entregar tal cual lo decide tu profesor; en general se espera que entiendas y puedas explicar cada paso, para lo cual el paso a paso y la teoría son la mejor ayuda. |
| ¿Puedo escribir fracciones? | Sí, en todas las casillas numéricas: `6/7`, `1/3`. El cálculo usa el valor exacto de la fracción. |
| ¿Por qué Bairstow usa la tolerancia en porcentaje? | Porque el método mide el error relativo, como en el libro de donde viene. El apartado 6.3 lo explica. |
| ¿Qué hago si el sistema no acepta mi función? | Lee el mensaje rojo debajo de la casilla y compáralo con la tabla del apartado 6.6. Los errores más comunes son escribir `sen` en vez de `sin` y olvidar el `*` entre letras. |
| ¿Puedo usar grados en las funciones trigonométricas? | No directamente: el sistema trabaja en radianes. Convierte los grados multiplicando por `pi/180`. |
| ¿Puedo usarlo en otro computador? | Sí, si ese computador tiene Docker Desktop y una copia de la carpeta del proyecto. Sigue el capítulo 2. |

# 12. Glosario

| Término | Significado |
|---|---|
| Acordeón | Fila de un menú que se abre y se cierra al tocarla para mostrar u ocultar su contenido. En pantallas pequeñas, cada categoría del menú es un acordeón. |
| Antiderivada | Función cuya derivada es la función que se quiere integrar. El sistema la usa en la comprobación de la integración para calcular la integral exacta. |
| API | Siglas en inglés de «interfaz de programación de aplicaciones». Es el canal por el que la página que ves le pide los cálculos al servidor. No tienes que usarla directamente. |
| Backend | La parte del sistema que hace los cálculos, sin pantalla propia. Vive en el contenedor llamado `backend`. |
| Cota del error | El error más grande que podría tener una fórmula, según la teoría. Si el error real queda por debajo, la teoría se cumple, y la tabla lo marca con ✔. |
| Contenedor | Una «caja» cerrada que Docker usa para ejecutar un programa con todo lo que necesita. El sistema usa dos: uno para la página y otro para los cálculos. |
| Convergencia | Cuando los resultados de un método iterativo se acercan cada vez más a un valor fijo, que es la respuesta. Si el método se acerca lo suficiente, se dice que «convergió». |
| Derivada | La rapidez con la que cambia una función en un punto; en la gráfica, la inclinación de la recta tangente en ese punto. |
| Diagonal principal | En una matriz, las casillas que van de la esquina superior izquierda a la inferior derecha: fila 1 columna 1, fila 2 columna 2, y así. |
| Diagonalmente dominante | Una matriz en la que, en cada fila, el número de la diagonal es más grande (sin signo) que la suma de los demás números de esa fila (sin signo). Si se cumple, Jacobi y Gauss-Seidel siempre convergen. |
| Docker | Programa que permite ejecutar aplicaciones dentro de contenedores, sin instalar nada más. Docker Desktop es su versión con ventana para Windows y macOS. |
| Error absoluto | La diferencia entre dos valores, sin importar el signo. Es el error que usa la columna «Error» de los sistemas: cuánto cambió la respuesta entre dos vueltas. |
| Error estimado | La diferencia entre dos aproximaciones seguidas. Se puede calcular sin conocer la respuesta exacta, y por eso es el que decide cuándo detenerse. |
| Error porcentual | El error relativo multiplicado por 100 y expresado en porcentaje. Bairstow lo usa para su tolerancia. |
| Error relativo | El error dividido entre el tamaño del valor. Sirve para comparar: un error de 1 es grande si el valor es 2, y pequeño si es un millón. |
| Error verdadero | La diferencia entre el valor exacto y la aproximación. Solo se puede calcular cuando se conoce el valor exacto; en las tablas aparece como Eₜ. |
| Extrapolación | Usar varias aproximaciones para adivinar hacia dónde van y obtener una mejor. Romberg combina dos trapecios para obtener un valor más exacto que ambos. |
| Factor cuadrático | Un polinomio de grado 2, como $x^2 - rx - s$, que divide exactamente a otro polinomio. Bairstow busca factores así para sacar las raíces de dos en dos. |
| Fracción | Un número escrito como división, por ejemplo 6/7. Los campos numéricos del sistema las aceptan. |
| Integral definida | El área bajo la curva de una función entre dos valores, a y b. |
| Iteración | Cada vuelta de un método iterativo: aplicar la regla una vez para obtener una aproximación mejor. Cada fila de la tabla es una iteración. |
| Iterativo (método) | Un método que llega a la respuesta poco a poco, mejorando una aproximación vuelta tras vuelta, en lugar de calcularla de una sola vez. |
| Jacobiano | La tabla de todas las derivadas de las ecuaciones respecto a cada variable. Newton la usa para decidir hacia dónde avanzar. |
| Límites de integración | Los valores a y b entre los que se calcula el área en una integral. |
| Matriz | Una tabla rectangular de números. En los sistemas lineales, la matriz A reúne los coeficientes de las ecuaciones. |
| Navegador | El programa con el que abres páginas web, como Google Chrome, Microsoft Edge o Mozilla Firefox. |
| Nodo | Cada punto donde un método evalúa la función. En la cuadratura gaussiana, los nodos están en posiciones especiales elegidas para dar la mejor precisión. |
| Paso (h) | La distancia entre los puntos que usa una fórmula de diferenciación o el ancho de cada segmento en integración. Un paso más pequeño suele dar una aproximación mejor. |
| PDF | Un formato de archivo de documento que se ve igual en cualquier computador y se puede imprimir. El sistema genera el resultado en este formato. |
| Polinomio | Una expresión formada por potencias enteras de x multiplicadas por números y sumadas, como $2x^3 - x + 5$. Su grado es la potencia más alta. |
| Puerto | El número de «puerta» por la que un programa atiende en un computador. El sistema atiende por el 8080. |
| Punto inicial (valor inicial) | Los valores desde los que un método iterativo empieza a buscar la respuesta. En sistemas lineales se llama vector inicial x0. |
| Radián | La unidad de ángulo que usan las funciones trigonométricas del sistema. Una vuelta completa son 2π radianes, es decir, 360 grados. |
| Raíz | El valor de x que hace que un polinomio valga cero. Puede ser real o compleja. |
| Refinamiento | Cada fila de las tablas de diferenciación e integración: repetir el cálculo con un paso a la mitad o con el doble de segmentos. |
| Residuo | Lo que sobra o falta cuando reemplazas la solución en una ecuación. Si es cero o casi cero, la solución es correcta. |
| Segmento | Cada uno de los pedazos iguales en que se divide el intervalo [a, b] para calcular una integral. |
| Servidor | El programa que recibe los datos y hace los cálculos. En este sistema es el backend. |
| Tolerancia | El cambio más pequeño entre dos vueltas que todavía te importa. Cuando la respuesta cambia menos que la tolerancia, el método se detiene. |
| Valor de referencia | Un valor calculado con muy alta precisión que el sistema usa en lugar de la integral exacta cuando esta no se puede obtener con una fórmula. |
| Vista ilustrativa | Una opción de la gráfica de diferenciación que exagera el paso para que se vea la forma de las rectas. No cambia los resultados. |
| Vista previa | La franja gris debajo de una ecuación o función que muestra cómo la entendió el sistema, escrita como en un libro. |

# Anexo A — Índice de capturas

| Figura | Archivo | Apartado | Tomada por |
|---|---|---|---|
| Figura 1 — La carpeta del proyecto, con los archivos de doble clic | U-01-carpeta-del-proyecto.png | 2.1 | Usuario (marcador) |
| Figura 2 — La ventana de iniciar.bat cuando el sistema ya está listo | U-02-ventana-iniciar.png | 2.1 | Usuario (marcador) |
| Figura 3 — El sistema recién abierto en el navegador | U-03-aplicacion-abierta.png | 2.1 | Claude |
| Figura 4 — La barra superior, con la marca | U-04-barra-superior.png | 3.1 | Claude |
| Figura 5 — El menú «Resolver» desplegado | U-05-menu-resolver.png | 4.1 | Claude |
| Figura 6 — El buscador del menú con la palabra «derivada» | U-06-buscador.png | 4.2 | Claude |
| Figura 7 — El menú en una pantalla angosta | U-07-menu-pantalla-angosta.png | 4.4 | Claude |
| Figura 8 — El formulario de Jacobi vacío | U-08-formulario-jacobi-vacio.png | 5 (paso 2) | Claude |
| Figura 9 — La lista de ejemplos precargados de Jacobi | U-09-ejemplos-precargados.png | 5 (paso 3) | Claude |
| Figura 10 — El formulario de Jacobi con el ejemplo cargado y los ejemplos plegados | U-10-formulario-con-ejemplo.png | 5 (paso 4) | Claude |
| Figura 11 — El resultado de Jacobi: tarjeta de respuesta, gráfica y tabla | U-11-resultado-jacobi.png | 5 (paso 7) | Claude |
| Figura 12 — La sección «Comprobación» | U-14-comprobacion.png | 5 (paso 11) | Claude |
| Figura 13 — La gráfica «Convergencia del error» | U-15-grafica-convergencia.png | 5 (paso 12) | Claude |
| Figura 14 — El PDF del ejercicio abierto | U-16-pdf-descargado.png | 5 (paso 13) | Claude |
| Figura 15 — Una iteración de Gauss-Seidel en azul y verde | U-13-paso-a-paso-colores.png | 5 (paso 14) | Claude |
| Figura 16 — El diálogo de confirmación de «Limpiar» | U-17-dialogo-limpiar.png | 5 (paso 15) | Claude |
| Figura 17 — El formulario de un sistema no lineal | U-19-formulario-no-lineal.png | 6.2 | Claude |
| Figura 18 — El formulario de Bairstow con los coeficientes | U-20-formulario-bairstow.png | 6.3 | Claude |
| Figura 19 — Diferenciación en modo «Función» | U-21-diferenciacion-funcion.png | 6.4 | Claude |
| Figura 20 — Diferenciación en modo «Tabla de datos» | U-22-diferenciacion-tabla.png | 6.4 | Claude |
| Figura 21 — El formulario del trapecio y su gráfica | U-24-trapecio-formulario-y-grafica.png | 6.5 | Claude |
| Figura 22 — La leyenda «¿Qué significa cada columna?» | U-12-leyenda-columnas.png | 7.2 | Claude |
| Figura 23 — El glosario «¿Qué significa cada símbolo?» | U-26-glosario-simbolos.png | 7.4 | Claude |
| Figura 24 — La tabla triangular de Romberg | U-25-tabla-romberg.png | 7.6 | Claude |
| Figura 25 — La gráfica de diferenciación con la vista ilustrativa | U-23-grafica-vista-ilustrativa.png | 7.6 | Claude |
| Figura 26 — La página de teoría de Jacobi | U-27-pagina-teoria.png | 8 | Claude |
| Figura 27 — El resultado de Jacobi en modo oscuro | U-18-modo-oscuro.png | 9 | Claude |
| Figura 28 — El error de una función mal escrita | U-28-error-expresion.png | 10.1 | Claude |
| Figura 29 — Una condición del método que no se cumple | U-29-error-validacion.png | 10.1 | Claude |
| Figura 30 — El aviso de no convergencia | U-30-aviso-no-convergencia.png | 10.1 | Claude |

Para reemplazar los marcadores de las Figuras 1 y 2, guarda la captura real con el mismo nombre de archivo que indica esta tabla.

# Anexo B — Qué método usar

| Si tu ejercicio es… | Usa… | Ten en cuenta… |
|---|---|---|
| Un sistema de 3 o más ecuaciones lineales y te piden Jacobi, o quieres ver el método más simple | Jacobi | Necesita que la diagonal no tenga ceros; converge seguro si la matriz es diagonalmente dominante. Deja marcada la opción de reordenar filas. |
| Un sistema de 3 o más ecuaciones lineales y quieres llegar en menos vueltas | Gauss-Seidel | Mismas condiciones que Jacobi; suele necesitar la mitad de iteraciones. Puedes compararlos sin reescribir los datos. |
| Un sistema de 2 a 6 ecuaciones no lineales que se pueden despejar fácilmente | Punto Fijo (Iterativo Secuencial) | Cada variable debe poder despejarse de su ecuación de forma única y con grado 4 o menos; si no, escribe la ecuación ya despejada. Puede necesitar muchas vueltas o no converger. |
| Un sistema de 2 a 6 ecuaciones no lineales, sobre todo si no se pueden despejar | Newton | Converge muy rápido si el punto inicial está cerca de la solución. Evita empezar en cero si las ecuaciones tienen productos o potencias. |
| Encontrar todas las raíces de un polinomio de grado 3 a 10 | Bairstow | La tolerancia va en porcentaje. Si dice que el sistema 2×2 es singular, cambia r₀ y s₀. |
| La derivada en un punto con la fórmula más simple, o con datos de espaciado desigual | Diferencias progresiva y regresiva | Es la menos precisa (error del orden de h). Acepta tablas desde 2 puntos. |
| La derivada en un punto con buena precisión | Fórmula de 3 puntos | Usa «Punto medio» si tienes puntos a ambos lados y los extremos al borde de una tabla. Las tablas deben estar igualmente espaciadas. |
| La derivada con la mayor precisión, o con datos de 5 o más puntos | Fórmula de 5 puntos | Necesita más puntos (al menos 5 en tabla) igualmente espaciados. |
| Una integral a partir de datos medidos con separaciones desiguales, o la regla más simple | Método del trapecio | Acepta cualquier espaciado y de 2 a 30 puntos. Es el menos preciso con pocos segmentos. |
| Una integral con buena precisión y pocos puntos | Método de Simpson | 1/3 necesita un número par de segmentos y 3/8 un múltiplo de 3; con tablas, puntos igualmente espaciados. |
| Una integral de una función suave con mucha precisión, o una tabla de 3, 5, 9, 17 o 33 puntos | Integración de Romberg | Funciona mejor con funciones suaves; con raíces o valores absolutos mejora lentamente. |
| Una integral con muy pocas evaluaciones, o una función que no está definida en los extremos | Cuadratura gaussiana | Solo con funciones, no con tablas. No evalúa los extremos, así que sirve para funciones como $1/\sqrt{x}$ en [0, 1]. |
