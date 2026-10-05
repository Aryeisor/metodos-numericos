"""División sintética entre el factor cuadrático x² − r·x − s, como en el
tablero.

Los coeficientes van en orden **descendente** (posición 0 = potencia más alta,
última posición = término independiente). Para un polinomio de grado n, la
posición p corresponde a la potencia i = n − p.

Primera división (coeficientes b, sobre los a):
    bₙ = aₙ
    bₙ₋₁ = aₙ₋₁ + r·bₙ
    bᵢ = aᵢ + r·bᵢ₊₁ + s·bᵢ₊₂          i = n−2, …, 0

Segunda división (coeficientes c, sobre los b), igual pero sin c₀, que
Bairstow no usa:
    cᵢ = bᵢ + r·cᵢ₊₁ + s·cᵢ₊₂          i = n−2, …, 1

Cada tabla conserva las cuatro filas que se escriben a mano: los
coeficientes de entrada, los productos r·(anterior), los productos
s·(dos atrás) y el resultado. Una casilla que no existe (por ejemplo r·bₙ₊₁)
o que no se calcula (c₀) vale None.

No depende de Django: puede usarse y testearse de forma aislada.
"""


def synthetic_division(coefficients, r, s, skip_last=False):
    """Divide entre x² − r·x − s. Devuelve la tabla de cuatro filas:

    {"coefficients", "r_terms", "s_terms", "result"}, todas de la misma
    longitud que `coefficients`. Con `skip_last=True` no calcula la última
    posición (c₀ en la segunda división): su casilla queda en None.
    """
    n = len(coefficients)
    result = [None] * n
    r_terms = [None] * n
    s_terms = [None] * n
    last = n - 1 if skip_last else n
    for p in range(last):
        value = coefficients[p]
        if p >= 1:
            r_terms[p] = r * result[p - 1]
            value += r_terms[p]
        if p >= 2:
            s_terms[p] = s * result[p - 2]
            value += s_terms[p]
        result[p] = value
    return {
        "coefficients": list(coefficients),
        "r_terms": r_terms,
        "s_terms": s_terms,
        "result": result,
    }


def b_table(coefficients, r, s):
    """Primera división: los b a partir de los a."""
    return synthetic_division(coefficients, r, s)


def c_table(b, r, s):
    """Segunda división: los c a partir de los b (sin c₀)."""
    return synthetic_division(b, r, s, skip_last=True)


def at_power(values, power):
    """Valor de la casilla de la potencia `power` en una lista descendente."""
    return values[len(values) - 1 - power]
