"""Gráfica de la aproximación de los 3 métodos de diferenciación (chart.py)."""

import json
import math

from django.test import SimpleTestCase

from numeric_methods.solvers.differentiation.chart import CHART_ROWS, lagrange_slope
from numeric_methods.tests import test_differentiation, test_five_point, test_three_point

FUNCTION_EXAMPLES = (
    (test_differentiation, "dif-burden-ln"),
    (test_three_point, "tp-burden-xexp"),
    (test_five_point, "cp-burden-xexp"),
)
TABLE_EXAMPLES = (
    (test_differentiation, "dif-carro"),
    (test_differentiation, "dif-tabla"),
    (test_three_point, "tp-tabla-burden"),
    (test_three_point, "tp-tabla-cubos"),
    (test_five_point, "cp-tabla-burden"),
    (test_five_point, "cp-tabla-cuartas"),
)


def pieces(chart):
    """Cada bloque de fórmula de la gráfica, con su fila."""
    for row in chart["rows"]:
        for piece in row["formulas"].values():
            yield row, piece


def slope(line):
    (a, ya), (b, yb) = line
    return (yb - ya) / (b - a)


def close(a, b, relative=1e-9):
    return abs(a - b) <= relative * max(1.0, abs(b))


class ChartTests(SimpleTestCase):
    def charts(self, examples):
        for module, example_id in examples:
            with self.subTest(example=example_id):
                yield example_id, module.example(example_id)["chart"]

    def test_interpolant_slope_at_x0_is_D(self):
        for _, chart in self.charts(FUNCTION_EXAMPLES + TABLE_EXAMPLES):
            for _, piece in pieces(chart):
                xs = [p["x"] for p in piece["points"]]
                ys = [p["y"] for p in piece["points"]]
                x0 = next(p["x"] for p in piece["points"] if p["base"])
                self.assertTrue(close(lagrange_slope(xs, ys, x0), piece["D"]), piece["key"])

    def test_interpolant_passes_through_points(self):
        for _, chart in self.charts(FUNCTION_EXAMPLES + TABLE_EXAMPLES):
            for _, piece in pieces(chart):
                curve = piece["interpolant"]
                for point in piece["points"]:
                    i = min(range(len(curve["x"])), key=lambda j: abs(curve["x"][j] - point["x"]))
                    self.assertTrue(close(curve["x"][i], point["x"], 1e-12))
                    self.assertLessEqual(abs(curve["y"][i] - point["y"]), 1e-9)

    def test_line_slopes(self):
        for _, chart in self.charts(FUNCTION_EXAMPLES + TABLE_EXAMPLES):
            for row, piece in pieces(chart):
                self.assertTrue(close(slope(piece["approx"]), piece["D"]))
                exact = chart["exact"] if chart["mode"] == "function" else None
                if piece["tangent"] is not None:
                    tangent = slope(piece["tangent"])
                    if exact is not None:
                        self.assertTrue(close(tangent, exact))
                    # En la tabla, f'(xᵢ) de cada punto: |D − pendiente| es el error real.
                    self.assertLessEqual(abs(abs(piece["D"] - tangent) - piece["error"]), 1e-9)
                if chart["mode"] == "function":
                    for line in row["compare"]["lines"]:
                        self.assertTrue(close(slope(line["line"]), line["D"]))
                    self.assertTrue(close(slope(row["compare"]["tangent"]), exact))

    def test_verified_slopes(self):
        expected = {
            "dif-burden-ln": {"forward": 0.540672, "backward": 0.571584},
            "tp-burden-xexp": {"punto_medio": 22.228787, "extremo_adelante": 22.032305, "extremo_atras": 22.054521},
            "cp-burden-xexp": {"punto_medio_5": 22.166996, "extremo_adelante_5": 22.165915,
                               "extremo_atras_5": 22.166312},
        }
        exact = {"dif-burden-ln": 0.555556, "tp-burden-xexp": 22.167168, "cp-burden-xexp": 22.167168}
        for example_id, chart in self.charts(FUNCTION_EXAMPLES):
            row = chart["rows"][0]
            for key, value in expected[example_id].items():
                self.assertAlmostEqual(row["formulas"][key]["D"], value, places=6)
            self.assertAlmostEqual(chart["exact"], exact[example_id], places=6)

    def test_windows_of_row_one(self):
        expected = {
            "dif-burden-ln": {"forward": (1.7, 2.0), "backward": (1.6, 1.9)},
            "tp-burden-xexp": {"punto_medio": (1.8, 2.2), "extremo_adelante": (1.9, 2.3),
                               "extremo_atras": (1.7, 2.1)},
            "cp-burden-xexp": {"punto_medio_5": (1.7, 2.3), "extremo_adelante_5": (1.9, 2.5),
                               "extremo_atras_5": (1.5, 2.1)},
        }
        for example_id, chart in self.charts(FUNCTION_EXAMPLES):
            for key, (a, b) in expected[example_id].items():
                window = chart["rows"][0]["formulas"][key]["window"]
                self.assertAlmostEqual(window[0], a, places=12)
                self.assertAlmostEqual(window[1], b, places=12)

    def test_window_zooms_with_h(self):
        chart = test_five_point.example("cp-burden-xexp")["chart"]
        widths = [row["formulas"]["punto_medio_5"]["window"] for row in chart["rows"]]
        for k, (a, b) in enumerate(widths):
            self.assertAlmostEqual(b - a, 0.6 / 2 ** k, places=12)

    def test_reading_phrases(self):
        chart = test_differentiation.example("dif-burden-ln")["chart"]
        row = chart["rows"][0]
        self.assertEqual(row["formulas"]["forward"]["side"], "under")
        self.assertIn("subestima", row["formulas"]["forward"]["phrase"])
        self.assertEqual(row["formulas"]["backward"]["side"], "over")
        self.assertIn("sobreestima", row["formulas"]["backward"]["phrase"])
        self.assertIn("una a cada lado de la tangente", row["compare"]["phrase"])
        self.assertIn("promedio (la fórmula de 3 puntos)", row["compare"]["phrase"])

        five = test_five_point.example("cp-burden-xexp")["chart"]["rows"][0]
        self.assertEqual(five["formulas"]["punto_medio_5"]["side"], "under")
        self.assertIn("subestima", five["formulas"]["punto_medio_5"]["phrase"])

    def test_five_point_compare_includes_three_point_reference(self):
        row = test_five_point.example("cp-burden-xexp")["chart"]["rows"][0]
        reference = next(line for line in row["compare"]["lines"] if line["key"] == "reference")
        self.assertEqual(reference["name"], "Punto medio de 3 puntos")
        self.assertAlmostEqual(reference["D"], 22.228787, places=6)
        self.assertIn("el punto medio de 3 puntos tiene más pendiente", row["compare"]["phrase"])

    def test_function_undefined_in_part_of_window(self):
        result = test_differentiation.solve(function="ln(x)", x0=0.15, h0=0.1, formula="backward")
        self.assertEqual(len(result["iterations"][0]["x"]), 1)
        text = json.dumps(result["chart"], allow_nan=False)  # sin NaN ni infinitos
        row = json.loads(text)["rows"][0]
        a, b = row["formulas"]["backward"]["window"]
        self.assertAlmostEqual(a, -0.05, places=12)
        self.assertAlmostEqual(b, 0.25, places=12)
        curve = row["curve"]
        for x, y in zip(curve["x"], curve["y"]):
            if x <= 0:
                self.assertIsNone(y)
            else:
                self.assertTrue(math.isfinite(y))

    def test_only_rows_one_to_four(self):
        for _, chart in self.charts(FUNCTION_EXAMPLES):
            self.assertEqual([row["k"] for row in chart["rows"]], list(range(1, CHART_ROWS + 1)))

    def test_table_defaults(self):
        expected = {
            "dif-carro": (4, {1: "forward", 4: "forward", 6: "backward"}),
            "tp-tabla-burden": (3, {1: "extremo_adelante", 3: "punto_medio", 5: "extremo_atras"}),
            "cp-tabla-burden": (5, {1: "extremo_adelante_5", 5: "punto_medio_5", 9: "extremo_atras_5"}),
        }
        for example_id, chart in self.charts(TABLE_EXAMPLES):
            if example_id not in expected:
                continue
            point, defaults = expected[example_id]
            self.assertEqual(chart["default_point"], point)
            for i, key in defaults.items():
                self.assertEqual(chart["rows"][i - 1]["default"], key)
            self.assertIsNotNone(chart["curve"])

    def test_table_without_function_has_no_curve_nor_tangent(self):
        chart = test_differentiation.example("dif-tabla")["chart"]
        self.assertIsNone(chart["curve"])
        for _, piece in pieces(chart):
            self.assertIsNone(piece["tangent"])
            self.assertIsNone(piece["phrase"])
