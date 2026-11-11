"""h en tablas y paso a paso: el backend envía la forma exacta (`text`/`latex`)
y el decimal a 6 (`approx`) por separado. La tabla muestra «≈ approx» con
`text` en el title; el paso a paso muestra las dos cosas."""

import math

from django.test import SimpleTestCase

from numeric_methods.serializers.differentiation import (
    DifferentiationSerializer,
    FivePointSerializer,
    ThreePointSerializer,
)
from numeric_methods.serializers.integration import (
    GaussSerializer,
    IntegrationSerializer,
    RombergSerializer,
    SimpsonSerializer,
)
from numeric_methods.solvers.differentiation.display import step_size
from numeric_methods.solvers.differentiation.finite_differences import solve_finite_differences
from numeric_methods.solvers.differentiation.five_point import solve_five_point
from numeric_methods.solvers.differentiation.three_point import solve_three_point
from numeric_methods.solvers.integration.gauss import solve_gauss
from numeric_methods.solvers.integration.romberg import solve_romberg
from numeric_methods.solvers.integration.simpson import solve_simpson
from numeric_methods.solvers.integration.trapezoid import _step, solve_trapezoid


def run(serializer_class, solver, **data):
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    return solver(serializer.validated_data).to_dict()


def table_text(h):
    """Lo mismo que tableValue (frontend/src/utils/iterationSteps.js)."""
    return h["text"] if h["exact"] else f"≈ {h['approx']}"


class HTableFormatTests(SimpleTestCase):
    def test_periodic(self):
        _, h = _step(0, 2, 3)
        self.assertEqual(table_text(h), "≈ 0.666667")
        self.assertEqual(h["text"], "(2 − 0)/3")

    def test_exact(self):
        _, h = _step(0, 1, 2)
        self.assertEqual(table_text(h), "0.5")

    def test_irrational(self):
        _, h = _step(0, math.pi, 1)
        self.assertEqual(table_text(h), "≈ 3.141593")
        # shortcut: a y b llegan como float, así que la forma exacta es (3.141593 − 0)/1, no (π − 0)/1.
        self.assertEqual(h["text"], "(3.141593 − 0)/1")

    def test_differentiation_row_13(self):
        _, h12 = step_size(0.1, 12)
        self.assertEqual(table_text(h12), "0.000048828125")
        _, h13 = step_size(0.1, 13)
        self.assertEqual(table_text(h13), "≈ 0.000024")
        self.assertEqual(h13["text"], "0.1/2^12")

    def test_simpson_38_control_values(self):
        result = run(SimpsonSerializer, solve_simpson, mode="function", function="x^4", a=0, b=2,
                     rule="both", n0_13=2, n0_38=3, tolerance=1e-12, max_iterations=7)
        blocks = {b["rule"]["key"]: b["rows"] for b in result["rules"]}
        rows38 = next(rows for key, rows in blocks.items() if "38" in key)
        expected = ["0.666667", "0.333333", "0.166667", "0.083333", "0.041667", "0.020833", "0.010417"]
        self.assertEqual([table_text(r["h"]) for r in rows38], [f"≈ {v}" for v in expected])
        self.assertEqual([r["h"]["text"] for r in rows38],
                         [f"(2 − 0)/{3 * 2 ** k}" for k in range(7)])
        rows13 = next(rows for key, rows in blocks.items() if "13" in key)
        self.assertTrue(all(r["h"]["exact"] for r in rows13))


class StepShowsExactAndDecimalTests(SimpleTestCase):
    """Fila 1 de cada método: el paso del ancho tiene la forma exacta y el decimal."""

    def assert_both(self, h):
        self.assertTrue(h["text"])
        if not h["exact"]:
            self.assertRegex(h["approx"], r"^-?\d+(\.\d{1,6})?$")

    def test_trapezoid(self):
        result = run(IntegrationSerializer, solve_trapezoid, mode="function", function="x^4", a=0, b=2,
                     n0=3, tolerance=1e-6, max_iterations=8)
        h = result["iterations"][0]["extra"]["h"]
        self.assertFalse(h["exact"])
        self.assert_both(h)

    def test_simpson(self):
        result = run(SimpsonSerializer, solve_simpson, mode="function", function="x^4", a=0, b=2,
                     rule="simpson38", n0_38=3, tolerance=1e-6, max_iterations=8)
        self.assert_both(result["rules"][0]["rows"][0]["h"])

    def test_romberg(self):
        result = run(RombergSerializer, solve_romberg, mode="function", function="sin(x)", a=0, b=1,
                     tolerance=1e-6, max_iterations=8)
        self.assert_both(result["iterations"][0]["extra"]["h"])

    def test_gauss_composite(self):
        result = run(GaussSerializer, solve_gauss, mode="function", function="x^4", a=0, b=2,
                     n0=1, subintervals=3, tolerance=1e-6, max_iterations=8)
        H = result["H_display"]
        self.assertFalse(H["exact"])
        self.assertEqual(H["approx"], "0.666667")

    def test_differentiation_methods(self):
        cases = [
            (DifferentiationSerializer, solve_finite_differences),
            (ThreePointSerializer, solve_three_point),
            (FivePointSerializer, solve_five_point),
        ]
        for serializer_class, solver in cases:
            with self.subTest(solver=solver.__name__):
                result = run(serializer_class, solver, function="ln(x)", x0=1.8, h0=0.1)
                self.assert_both(result["iterations"][0]["extra"]["h"])
