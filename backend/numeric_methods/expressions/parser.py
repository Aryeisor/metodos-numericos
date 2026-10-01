"""Parseo seguro de expresiones matemáticas escritas por el usuario.

`sympy.parse_expr` evalúa el texto con `eval()` de Python, incluso con
`evaluate=False` (ese parámetro sólo evita la simplificación algebraica). Con
la configuración por defecto, `__import__("os").getcwd()` se ejecuta. Por eso
hay dos capas de defensa:

1. Validación léxica ANTES de llamar a sympy: el texto se tokeniza y sólo se
   aceptan números, operadores aritméticos, paréntesis, comas y nombres de una
   lista blanca (las variables declaradas, funciones y constantes conocidas).
   Cualquier otra cosa —atributos (`.`), cadenas, corchetes, `lambda`,
   nombres desconocidos— se rechaza sin llegar a evaluarse.
2. `parse_expr` con un `global_dict` mínimo y sin `__builtins__`.
"""

import io
import keyword
import re
import tokenize

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication,
    parse_expr,
    standard_transformations,
)

MAX_LENGTH = 300
MAX_NESTING = 30

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

# Constructores que sympy usa internamente al transformar el texto.
_SYMPY_INTERNALS = {
    "Add": sp.Add,
    "Mul": sp.Mul,
    "Pow": sp.Pow,
    "Integer": sp.Integer,
    "Float": sp.Float,
    "Rational": sp.Rational,
    "Symbol": sp.Symbol,
}

_TRANSFORMATIONS = standard_transformations + (implicit_multiplication, convert_xor)

_ALLOWED_OPERATORS = {"+", "-", "*", "/", "**", "^", "(", ")", ","}
_NUMBER = re.compile(r"^(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$")
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


def parse_expression(text, variables):
    """Convierte texto en una expresión sympy sin simplificarla.

    Acepta `^` como potencia y multiplicación implícita (`3x`, `2(x+1)`).
    Lanza ExpressionError si el texto no es válido.
    """
    if not isinstance(text, str) or not text.strip():
        raise ExpressionError("La expresión está vacía.")

    symbols = make_symbols(variables)
    allowed_names = set(symbols) | set(ALLOWED_FUNCTIONS) | set(ALLOWED_CONSTANTS)
    _validate_tokens(text, allowed_names)

    global_dict = {"__builtins__": {}, **_SYMPY_INTERNALS, **ALLOWED_FUNCTIONS, **ALLOWED_CONSTANTS}
    try:
        expr = parse_expr(
            text,
            local_dict=dict(symbols),
            global_dict=global_dict,
            transformations=_TRANSFORMATIONS,
            evaluate=False,
        )
    except Exception as exc:  # sympy lanza tipos muy variados ante sintaxis inválida
        raise ExpressionError("La expresión no está bien formada.") from exc

    if not isinstance(expr, sp.Expr):
        raise ExpressionError("El resultado no es una expresión matemática.")
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
