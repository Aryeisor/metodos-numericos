"""Parseo seguro de expresiones matemáticas escritas por el usuario.

`sympy.parse_expr` evalúa el texto con `eval()` de Python, incluso con
`evaluate=False` (ese parámetro sólo evita la simplificación algebraica). Con
la configuración por defecto, `__import__("os").getcwd()` se ejecuta. Por eso
hay tres capas de defensa, más límites de recursos:

1. Validación léxica ANTES de llamar a sympy: el texto se tokeniza y sólo se
   aceptan números, operadores aritméticos, paréntesis, comas y nombres de una
   lista blanca (las variables declaradas, funciones y constantes conocidas).
   Cualquier otra cosa —atributos (`.`), cadenas, corchetes, `lambda`,
   nombres desconocidos, saltos de línea— se rechaza sin llegar a evaluarse.
2. `parse_expr` con un `global_dict` que contiene sólo lo imprescindible y
   ningún `__builtins__` (ver `_global_dict`).
3. Validación del árbol ya parseado (`validate_expression_tree`): sólo pueden
   aparecer las variables declaradas, números finitos, pi, e, sumas,
   productos, potencias y las funciones de la lista blanca.

Límites de recursos: longitud del texto, anidamiento de paréntesis,
profundidad del árbol y magnitud de los números. Este último importa porque
una entrada corta como `9**9**9` no cuesta nada al parsear (con
`evaluate=False` no se calcula), pero cuelga el proceso al evaluarla
numéricamente con enteros exactos (por ejemplo, con `lambdify`).
"""

import cmath
import io
import keyword
import math
import re
import tokenize
import unicodedata

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication,
    parse_expr,
    standard_transformations,
)

MAX_LENGTH = 300
MAX_NESTING = 30
MAX_TREE_DEPTH = 40
# Magnitud máxima de cualquier subexpresión puramente numérica.
MAX_MAGNITUDE = 1e100
# Exponente numérico máximo. Con floats `x**(10**50)` desborda al instante,
# pero evaluado con enteros/racionales exactos (subs de un entero + doit)
# cuelga el proceso; lo mismo `(1/2)**(10**50)`, cuyo valor en float es 0.
MAX_EXPONENT = 1000

ALLOWED_FUNCTIONS = {
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "sinh": sp.sinh,
    "cosh": sp.cosh,
    "tanh": sp.tanh,
    "exp": sp.exp,
    "log": sp.log,
    "ln": sp.log,
    "sqrt": sp.sqrt,
    "abs": sp.Abs,
}

ALLOWED_CONSTANTS = {
    "pi": sp.pi,
    "e": sp.E,
}

# Constructores que sympy genera al transformar el texto con evaluate=False
# (números y operaciones). Es el mínimo verificado: sin cualquiera de ellos
# falla el parseo. `Symbol` NO está: si estuviera, la transformación
# `auto_symbol` podría fabricar símbolos con cualquier nombre.
_SYMPY_INTERNALS = {
    "Add": sp.Add,
    "Mul": sp.Mul,
    "Pow": sp.Pow,
    "Integer": sp.Integer,
    "Float": sp.Float,
}

# Clases de función que pueden aparecer en el árbol (sqrt produce un Pow).
_ALLOWED_FUNCTION_CLASSES = frozenset(
    f for f in ALLOWED_FUNCTIONS.values() if isinstance(f, type)
)
_ALLOWED_CONSTANT_VALUES = {sp.pi: math.pi, sp.E: math.e}

_TRANSFORMATIONS = standard_transformations + (implicit_multiplication, convert_xor)

_ALLOWED_OPERATORS = {"+", "-", "*", "/", "**", "^", "(", ")", ","}
_NUMBER = re.compile(r"^(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$", re.ASCII)
_IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_FUNCTION_HEADER = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*\(([^()]*)\)\s*$")


class ExpressionError(ValueError):
    """Expresión inválida o no permitida. El mensaje es apto para el usuario."""


def make_symbols(variables):
    """Valida los nombres de variables y devuelve {nombre: sympy.Symbol}."""
    if not variables:
        raise ExpressionError("Debe declararse al menos una variable.")
    symbols = {}
    for name in variables:
        if not isinstance(name, str) or not _IDENTIFIER.match(name):
            raise ExpressionError(f"'{name}' no es un nombre de variable válido.")
        if name in ALLOWED_FUNCTIONS or name in ALLOWED_CONSTANTS or keyword.iskeyword(name):
            raise ExpressionError(f"'{name}' está reservado y no puede usarse como variable.")
        if name in symbols:
            raise ExpressionError(f"La variable '{name}' está repetida.")
        symbols[name] = sp.Symbol(name, real=True)
    return symbols


def _validate_tokens(text, allowed_names):
    """Primera capa de defensa: lista blanca de tokens."""
    if len(text) > MAX_LENGTH:
        raise ExpressionError(f"La expresión supera el máximo de {MAX_LENGTH} caracteres.")

    # Un salto de línea hacía que sympy descartara en silencio el resto del
    # texto ("x\n+y" se parseaba como "x"); la barra invertida permite
    # continuar líneas. Tampoco se aceptan caracteres de control o invisibles.
    for char in text:
        if char in "\r\n\\":
            raise ExpressionError("La expresión debe escribirse en una sola línea.")
        if char != "\t" and unicodedata.category(char) in ("Cc", "Cf", "Zl", "Zp"):
            raise ExpressionError("La expresión contiene un carácter no permitido.")

    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError) as exc:
        raise ExpressionError("La expresión no está bien formada.") from exc

    depth = 0
    for token in tokens:
        kind, value = token.type, token.string
        if kind in (tokenize.NEWLINE, tokenize.NL, tokenize.ENDMARKER, tokenize.INDENT, tokenize.DEDENT):
            continue
        if kind == tokenize.NUMBER:
            if not _NUMBER.match(value):
                raise ExpressionError(f"Número no válido: '{value}'.")
        elif kind == tokenize.NAME:
            if value not in allowed_names:
                raise ExpressionError(
                    f"'{value}' no es una variable declarada ni una función conocida."
                )
        elif kind == tokenize.OP and value in _ALLOWED_OPERATORS:
            depth += value == "("
            depth -= value == ")"
            if depth > MAX_NESTING:
                raise ExpressionError("La expresión tiene demasiados paréntesis anidados.")
        else:
            raise ExpressionError(f"Símbolo no permitido: '{value}'.")


def _global_dict():
    """Únicos nombres visibles para el `eval` interno de `parse_expr`.

    `__builtins__` vacío impide que Python inyecte los builtins (open, eval,
    __import__...). Las variables declaradas van aparte, en `local_dict`.
    """
    return {
        "__builtins__": {},
        **_SYMPY_INTERNALS,
        **ALLOWED_FUNCTIONS,
        **ALLOWED_CONSTANTS,
    }


def _bounded(value):
    """Verifica que un valor numérico intermedio sea finito y razonable."""
    if not cmath.isfinite(complex(value)) or abs(value) > MAX_MAGNITUDE:
        raise ExpressionError(
            "La expresión contiene un número demasiado grande "
            f"(el máximo permitido es {MAX_MAGNITUDE:.0e})."
        )
    return value


def _inspect(node, symbols, depth):
    """Recorre el árbol validándolo; devuelve el valor numérico aproximado del
    subárbol si es puramente numérico, o None si depende de variables o de
    funciones. Usa floats de Python: nunca evalúa con sympy ni con enteros
    exactos, así que comprobar `9**9**9` es instantáneo (desborda y se rechaza).
    """
    if depth > MAX_TREE_DEPTH:
        raise ExpressionError(
            f"La expresión está anidada a más de {MAX_TREE_DEPTH} niveles."
        )

    if isinstance(node, sp.Symbol):
        if node not in symbols:
            raise ExpressionError(f"'{node}' no es una variable declarada.")
        return None

    if node in _ALLOWED_CONSTANT_VALUES:
        return _ALLOWED_CONSTANT_VALUES[node]

    if node.is_Number:
        # Excluye oo, -oo, zoo y nan, que también son "números" en sympy.
        if not (node.is_Float or node.is_Rational) or node.is_finite is False:
            raise ExpressionError("La expresión contiene un valor no finito.")
        try:
            return _bounded(float(node))
        except OverflowError as exc:
            raise ExpressionError(
                "La expresión contiene un número demasiado grande "
                f"(el máximo permitido es {MAX_MAGNITUDE:.0e})."
            ) from exc

    if isinstance(node, (sp.Add, sp.Mul, sp.Pow)):
        values = [_inspect(arg, symbols, depth + 1) for arg in node.args]

        if isinstance(node, sp.Pow):
            base, exponent = values
            if exponent is not None and abs(exponent) > MAX_EXPONENT:
                raise ExpressionError(
                    f"La expresión contiene un exponente demasiado grande "
                    f"(el máximo permitido es {MAX_EXPONENT})."
                )
            if base == 0 and exponent is not None and exponent.real < 0:
                raise ExpressionError("La expresión contiene una división entre cero.")

        if any(value is None for value in values):
            return None
        try:
            if isinstance(node, sp.Add):
                return _bounded(sum(values))
            if isinstance(node, sp.Mul):
                return _bounded(math.prod(values))
            return _bounded(values[0] ** values[1])
        except OverflowError as exc:
            raise ExpressionError(
                "La expresión contiene un número demasiado grande "
                f"(el máximo permitido es {MAX_MAGNITUDE:.0e})."
            ) from exc
        except ZeroDivisionError as exc:
            raise ExpressionError("La expresión contiene una división entre cero.") from exc

    if isinstance(node, sp.Function) and node.func in _ALLOWED_FUNCTION_CLASSES:
        for arg in node.args:
            _inspect(arg, symbols, depth + 1)
        return None

    raise ExpressionError(
        f"La expresión contiene un elemento no permitido ({type(node).__name__})."
    )


def validate_expression_tree(expr, symbols):
    """Tercera capa de defensa: valida el árbol ya parseado.

    `symbols` es el diccionario de `make_symbols`. Lanza ExpressionError ante
    cualquier variable no declarada, función fuera de la lista blanca, valor
    no finito, división literal entre cero, número desmesurado o anidamiento
    excesivo.
    """
    if not isinstance(expr, sp.Expr):
        raise ExpressionError("El resultado no es una expresión matemática.")
    _inspect(expr, frozenset(symbols.values()), depth=1)


def parse_expression(text, variables):
    """Convierte texto en una expresión sympy sin simplificarla.

    Acepta `^` como potencia y multiplicación implícita (`3x`, `2(x+1)`).
    Lanza ExpressionError si el texto no es válido.
    """
    if not isinstance(text, str) or not text.strip():
        raise ExpressionError("La expresión está vacía.")
    text = text.strip()

    symbols = make_symbols(variables)
    allowed_names = set(symbols) | set(ALLOWED_FUNCTIONS) | set(ALLOWED_CONSTANTS)
    _validate_tokens(text, allowed_names)

    try:
        expr = parse_expr(
            text,
            local_dict=dict(symbols),
            global_dict=_global_dict(),
            transformations=_TRANSFORMATIONS,
            evaluate=False,
        )
    except Exception as exc:  # sympy lanza tipos muy variados ante sintaxis inválida
        raise ExpressionError("La expresión no está bien formada.") from exc

    validate_expression_tree(expr, symbols)
    return expr


def parse_function(text, variables):
    """Parsea una función o ecuación escrita por el usuario.

    Formas aceptadas:
      - "f1(x, y) = x**2 + x*y - 10"  -> ("f1", x**2 + x*y - 10)
      - "x**2 + x*y = 10"             -> (None, x**2 + x*y - 10)
      - "x**2 + x*y - 10"             -> (None, x**2 + x*y - 10)

    En la forma con encabezado, sus argumentos deben coincidir con `variables`.
    """
    if not isinstance(text, str) or not text.strip():
        raise ExpressionError("La expresión está vacía.")
    if "==" in text or text.count("=") > 1:
        raise ExpressionError("Usa un único '=' para separar los dos lados.")

    if "=" not in text:
        return None, parse_expression(text, variables)

    left, right = text.split("=")
    header = _FUNCTION_HEADER.match(left)
    if header:
        name = header.group(1)
        args = [a.strip() for a in header.group(2).split(",") if a.strip()]
        if args != list(variables):
            raise ExpressionError(
                f"Los argumentos de {name}({', '.join(args)}) no coinciden con las "
                f"variables declaradas ({', '.join(variables)})."
            )
        return name, parse_expression(right, variables)

    lhs = parse_expression(left, variables)
    rhs = parse_expression(right, variables)
    return None, sp.Add(lhs, sp.Mul(-1, rhs, evaluate=False), evaluate=False)


def parse_system(texts, variables):
    """Parsea un sistema de funciones; devuelve [(nombre, expresión), ...]."""
    if not texts:
        raise ExpressionError("El sistema no tiene ecuaciones.")
    return [parse_function(text, variables) for text in texts]
