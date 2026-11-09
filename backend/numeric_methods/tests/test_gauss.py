"""Cuadratura gaussiana: valores de referencia verificados con un script
independiente (formas exactas de los nodos y los ejemplos precargados)."""

import json
import math
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from rest_framework.test import APITestCase

from numeric_methods.examples_data import GAUSS_EXAMPLES
from numeric_methods.serializers.integration import GaussSerializer
from numeric_methods.solvers.integration import exact as exact_module
from numeric_methods.solvers.integration import gauss as gauss_module
from numeric_methods.solvers.integration.gauss import moments, nodes_and_weights, solve_gauss


# Respuestas del solver guardadas para la página de teoría (frontend): ejemplos
# 1 (Chapra, con su gráfico), 2 (e^(−x²)), 4 (x⁶), 5 (1/√x, con su gráfico) y
# 7 (Chapra con N = 2).
THEORY_EXAMPLE = (Path(__file__).resolve().parents[3] / "frontend" / "src" / "methods"
                  / "integration" / "theory" / "gaussExample.json")
THEORY_KEYS = {"function": 1, "gauss": 2, "sixth": 4, "root": 5, "composite": 7}
THEORY_CHARTS = {"function", "root"}


def solve(**data):
    serializer = GaussSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return solve_gauss(serializer.validated_data).to_dict()


_CACHE = {}


def example(number):
    if number not in _CACHE:
        _CACHE[number] = solve(**GAUSS_EXAMPLES[number - 1])
    return _CACHE[number]


def rows(result):
    return [step["extra"] for step in result["iterations"]]


def rounded(values, places=6):
    return [round(v, places) for v in values]


_OUTER, _INNER = math.sqrt(3 / 7 + 2 / 7 * math.sqrt(6 / 5)), math.sqrt(3 / 7 - 2 / 7 * math.sqrt(6 / 5))
EXACT = {
    1: ([0.0], [2.0]),
    2: ([-1 / math.sqrt(3), 1 / math.sqrt(3)], [1.0, 1.0]),
    3: ([-math.sqrt(3 / 5), 0.0, math.sqrt(3 / 5)], [5 / 9, 8 / 9, 5 / 9]),
    4: ([-_OUTER, -_INNER, _INNER, _OUTER],
        [(18 - math.sqrt(30)) / 36, (18 + math.sqrt(30)) / 36, (18 + math.sqrt(30)) / 36, (18 - math.sqrt(30)) / 36]),
}


class NodesAndWeightsTests(SimpleTestCase):
    def test_exact_forms(self):
        for m, (nodes, weights) in EXACT.items():
            got_nodes, got_weights = nodes_and_weights(m)
            for got, want in zip(got_nodes + got_weights, nodes + weights):
                with self.subTest(m=m):
                    self.assertLessEqual(abs(got - want), 1e-14)
        self.assertEqual(rounded(nodes_and_weights(4)[0]), [-0.861136, -0.339981, 0.339981, 0.861136])
        self.assertEqual(rounded(nodes_and_weights(4)[1]), [0.347855, 0.652145, 0.652145, 0.347855])

    def test_weights_sum_two_and_nodes_are_symmetric(self):
        for m in range(1, 21):
            nodes, weights = nodes_and_weights(m)
            with self.subTest(m=m):
                self.assertEqual(len(nodes), m)
                self.assertLessEqual(abs(math.fsum(weights) - 2), 1e-13)
                self.assertEqual(list(nodes), [-t for t in reversed(nodes)])
                self.assertTrue(all(-1 < t < 1 for t in nodes))

    def test_exactness_up_to_degree_2m_minus_1(self):
        for m in range(1, 7):
            table = moments(m)
            with self.subTest(m=m):
                self.assertEqual(len(table), 2 * m + 1)
                self.assertTrue(all(row["ok"] and row["difference"] <= 1e-12 for row in table[:-1]))
                self.assertFalse(table[-1]["ok"])
        sixth = moments(3)[6]
        self.assertEqual((round(sixth["value"], 6), round(sixth["exact"], 6)), (0.24, 0.285714))
        self.assertAlmostEqual(moments(3)[0]["value"], 2.0, places=13)


class ChapraExampleTests(SimpleTestCase):
    def setUp(self):
        self.result = example(1)
        self.rows = rows(self.result)

    def test_first_rows(self):
        self.assertEqual(self.result["integral"]["kind"], "exact")
        self.assertAlmostEqual(self.result["integral"]["value"], 3076 / 1875, places=12)
        self.assertEqual(rounded([r["G"] for r in self.rows[:3]]), [1.9648, 1.822578, 1.640533])
        self.assertEqual(rounded([r["true_error"] for r in self.rows[:2]]), [-0.324267, -0.182044])
        self.assertEqual([round(r["relative_error"], 4) for r in self.rows[:2]], [19.7659, 11.0967])
        self.assertEqual(rounded([r["bound"] for r in self.rows[:3]]), [8.533333, 1.6384, 0])
        self.assertEqual(self.rows[2]["bound_info"]["M"]["value"], 0)
        self.assertEqual(self.result["center_display"]["text"], "0.4")
        self.assertEqual(self.result["half_width_display"]["text"], "0.4")

    def test_detail_of_m_2(self):
        step = self.rows[1]["step"]
        points = step["groups"][0]["points"]
        self.assertEqual([p["x_display"] for p in points], ["0.16906", "0.63094"])
        self.assertEqual([p["f_display"] for p in points], ["1.291851", "3.264593"])
        self.assertEqual([n["t_display"] for n in step["nodes"]], ["-0.57735", "0.57735"])
        self.assertEqual(step["nodes"][0]["t_latex"], r"-\frac{1}{\sqrt{3}}")
        self.assertEqual(step["groups"][0]["sum"], "4.556444")
        self.assertEqual(self.result["half_display"]["text"], "0.4")
        self.assertEqual(f"{float(step['total']['text']):.6f}", "1.822578")

    def test_stop(self):
        self.assertTrue(self.result["converged"])
        self.assertEqual(self.result["iterations_used"], 6)
        self.assertIsNone(self.rows[0]["estimated_error"])
        self.assertEqual(self.result["evaluations"], 21)
        self.assertEqual(self.rows[-1]["bound_reason"], "order")

    def test_cost(self):
        cost = self.result["cost"]
        self.assertEqual((cost["first_m"], cost["gauss_evaluations"], cost["romberg_evaluations"],
                          cost["simpson_evaluations"], cost["trapezoid_evaluations"]), (3, 3, 5, 65, 2049))
        self.assertTrue(cost["text"].startswith("Gauss llegó a |Eₜ| ≤ 0.000001 con m = 3 puntos: 3 evaluaciones"))

    def test_moments_use_last_m(self):
        self.assertEqual(self.result["verification"]["moments"]["m"], 6)
        self.assertEqual(len(self.result["verification"]["moments"]["rows"]), 13)


class SixthPowerTests(SimpleTestCase):
    def test_error_equals_bound_at_m_3_and_exact_from_m_4(self):
        row = rows(example(4))[2]
        self.assertEqual(round(row["true_error"], 6), 0.045714)
        self.assertEqual(round(row["bound"], 6), 0.045714)
        self.assertTrue(row["equals_bound"])
        self.assertTrue(row["within_bound"])
        self.assertFalse(row["by_rounding"])
        self.assertEqual(rounded([r["G"] for r in rows(example(4))[:4]]), [0, 0.074074, 0.24, 0.285714])
        for later in rows(example(4))[3:]:
            self.assertLessEqual(abs(later["G"] - 2 / 7), 1e-15)


class StoppingRowTests(SimpleTestCase):
    EXPECTED = {
        2: [0.778801, 0.746595, 0.746815, 0.746824],
        3: [3.141593, 1.93582, 2.001389, 1.999984, 2],
        6: [2, 1.848572, 1.851976, 1.851937],
        7: [1.9008, 1.651911, 1.640533],
        8: [51.428356, 53.586127, 53.598124, 53.59815],
    }

    def test_rows(self):
        for number, values in self.EXPECTED.items():
            with self.subTest(example=number):
                result = example(number)
                self.assertTrue(result["converged"])
                self.assertEqual(result["iterations_used"], 6)
                self.assertEqual(rounded([r["G"] for r in rows(result)[:len(values)]]), values)

    def test_example_2(self):
        result = example(2)
        self.assertEqual(result["integral"]["kind"], "reference")
        self.assertEqual(f"{result['integral']['value']:.6f}", "0.746824")
        errors = [r["true_error"] for r in rows(result)[:4]]
        self.assertEqual([round(errors[0], 3), round(errors[1], 6), round(errors[2], 7), round(errors[3], 9)],
                         [-0.032, 0.000229, 0.0000095, -0.000000335])
        cost = result["cost"]
        self.assertEqual((cost["gauss_evaluations"], cost["romberg_evaluations"], cost["simpson_evaluations"],
                          cost["trapezoid_evaluations"]), (4, 9, 17, 257))

    def test_example_3_bounds_and_cost(self):
        result = example(3)
        self.assertEqual(rounded([r["bound"] for r in rows(result)[:5]]), [1.291928, 0.070838, 0.001498, 0.000017, 0])
        cost = result["cost"]
        self.assertEqual((cost["gauss_evaluations"], cost["romberg_evaluations"], cost["simpson_evaluations"],
                          cost["trapezoid_evaluations"]), (5, 17, 65, 2049))

    def test_example_6_reference_and_note(self):
        result = example(6)
        self.assertEqual(result["integral"]["kind"], "reference")
        self.assertEqual(f"{result['integral']['value']:.6f}", "1.851937")
        self.assertTrue(any("Gauss no evalúa los extremos" in n for n in result["notes"]))

    def test_example_8_exact(self):
        self.assertAlmostEqual(example(8)["integral"]["value"], math.e ** 4 - 1, places=12)


class SingularEndpointTests(APITestCase):
    def test_example_5(self):
        response = self.client.post("/api/solve/gauss/", GAUSS_EXAMPLES[4], format="json")
        self.assertEqual(response.status_code, 200)
        result = example(5)
        self.assertTrue(any(n.startswith("f(x) no está definida en x = 0 (límite a). Gauss no evalúa los extremos")
                            for n in result["notes"]))
        self.assertFalse(result["converged"])
        self.assertEqual(result["iterations_used"], 12)
        self.assertEqual(rounded([r["G"] for r in rows(result)[:6]]), [1.414214, 1.65068, 1.750863, 1.806343, 1.8416,
                                                                        1.865992])
        self.assertEqual(round(rows(result)[-1]["G"], 6), 1.930337)
        self.assertTrue(any("No se alcanzó la tolerancia" in w for w in result["warnings"]))
        self.assertTrue(all(r["bound"] is None for r in rows(result)))
        self.assertEqual(rows(result)[0]["bound_reason"], "not_finite")
        cost = result["cost"]
        self.assertFalse(cost["applicable"])
        self.assertIsNone(cost["trapezoid_evaluations"])
        self.assertIn("no son aplicables", cost["text"])


class CompositeTests(SimpleTestCase):
    def test_example_7_nodes(self):
        result = example(7)
        self.assertEqual([c["text"] for c in result["centers"]], ["0.2", "0.6"])
        self.assertEqual(result["H_display"]["text"], "0.4")
        step = rows(result)[1]["step"]
        points = [p for g in step["groups"] for p in g["points"]]
        self.assertEqual([p["x_display"] for p in points], ["0.08453", "0.31547", "0.48453", "0.71547"])
        self.assertEqual([p["f_display"] for p in points], ["1.247658", "1.710564", "3.219806", "2.081528"])
        self.assertEqual(rounded([r["true_error"] for r in rows(result)[:2]]), [-0.260267, -0.011378])
        self.assertEqual(round(rows(result)[1]["bound"], 6), 0.1024)
        self.assertEqual(rows(result)[-1]["evaluations"], 12)

    def test_one_subinterval_is_the_simple_rule(self):
        f = lambda x: math.exp(-x * x)  # noqa: E731
        result = solve(function="exp(-x^2)", a=0, b=1, subintervals=1)
        for row in rows(result):
            nodes, weights = nodes_and_weights(row["m"])
            simple = 0.5 * sum(w * f(0.5 + 0.5 * t) for t, w in zip(nodes, weights))
            self.assertAlmostEqual(row["G"], simple, places=14)

    def test_rectangles(self):
        for number in (1, 4, 7, 8):
            result = example(number)
            for chart, row in zip(result["chart_rows"], rows(result)):
                G = row["G"]
                area = math.fsum((r["right"] - r["left"]) * r["height"] for r in chart["rects"])
                widths = math.fsum(r["right"] - r["left"] for r in chart["rects"])
                with self.subTest(example=number, m=chart["m"]):
                    self.assertLessEqual(abs(area - G), 1e-12 * max(1.0, abs(G)))
                    self.assertLessEqual(abs(widths - (result["b"] - result["a"])), 1e-12)
                    self.assertEqual(len(chart["rects"]), row["evaluations"])
        self.assertEqual(example(7)["chart_rows"][0]["edges"], [0, 0.4, 0.8])


class BoundCriterionTests(SimpleTestCase):
    def test_true_error_within_bound_plus_rounding(self):
        for number in range(1, 9):
            for row in rows(example(number)):
                if row["bound"] is not None and row["true_error"] is not None:
                    with self.subTest(example=number, m=row["m"]):
                        self.assertTrue(row["within_bound"])
                        self.assertLessEqual(abs(row["true_error"]), row["bound"] + row["rounding"])


class DerivativeTimeoutTests(SimpleTestCase):
    def test_exhausted_limit_hides_the_bound(self):
        with mock.patch.object(gauss_module, "_derivatives", return_value=([], True)):
            result = solve(function="cos(x)", a=0, b=1)
        self.assertTrue(all(r["bound"] is None for r in rows(result)))
        self.assertEqual(rows(result)[0]["bound_reason"], "timeout")
        self.assertTrue(any("límite de 3 s" in n and "muy larga de calcular" in n for n in result["notes"]))
        self.assertIsNotNone(rows(result)[-1]["true_error"])

    def test_child_process_keeps_what_it_finished(self):
        import sympy as sp

        x = sp.Symbol("x")
        found, timed_out = exact_module._derive_with_timeout(sp.exp(-x ** 2), x, 10, timeout=0)
        self.assertTrue(timed_out)
        self.assertLess(len(found), 10)
        found, timed_out = exact_module._derive_with_timeout(x ** 3, x, 4, timeout=30)
        self.assertFalse(timed_out)
        self.assertEqual(found, [3 * x ** 2, 6 * x, 6, 0])


class ValidationTests(APITestCase):
    URL = "/api/solve/gauss/"

    def assert_error(self, payload, fragment):
        response = self.client.post(self.URL, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn(fragment, str(response.json()))

    def test_errors(self):
        self.assert_error({"function": "x", "a": 1, "b": 1}, "debe ser menor")
        self.assert_error({"function": "x", "a": 2, "b": 1}, "debe ser menor")
        self.assert_error({"function": "x + y", "a": 0, "b": 1}, "f(x)")
        self.assert_error({"function": "x", "a": 0, "b": 1, "subintervals": 0}, "entre 1 y 50")
        self.assert_error({"function": "x", "a": 0, "b": 1, "subintervals": 51}, "entre 1 y 50")
        self.assert_error({"function": "x", "a": 0, "b": 1, "max_iterations": 5},
                          "El máximo de puntos debe estar entre 6 y 20.")
        self.assert_error({"function": "x", "a": 0, "b": 1, "max_iterations": 21},
                          "El máximo de puntos debe estar entre 6 y 20.")
        self.assert_error({"mode": "table", "points": [[0, 1], [1, 2]]}, "no funciona con una tabla de datos")

    def test_node_of_row_1(self):
        response = self.client.post(self.URL, {"function": "1/(x - 0.4)", "a": 0, "b": 0.8}, format="json")
        self.assertEqual(response.status_code, 400)
        message = str(response.json())
        self.assertIn("nodo", message)
        self.assertIn("x = 0.4", message)

    def test_undefined_endpoint_is_not_an_error(self):
        response = self.client.post(self.URL, {"function": "ln(x)", "a": 0, "b": 1}, format="json")
        self.assertEqual(response.status_code, 200)


class EndpointTests(APITestCase):
    def test_solve(self):
        response = self.client.post("/api/solve/gauss/", {"function": "x^2", "a": 0, "b": 2}, format="json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["category"], "integration")
        self.assertEqual((data["max_iterations"], data["subintervals"]), (12, 1))

    def test_catalog_and_examples(self):
        catalog = self.client.get("/api/methods/").json()
        slugs = [m["slug"] for m in catalog]
        self.assertEqual(slugs.index("gauss"), slugs.index("romberg") + 1)
        method = catalog[slugs.index("gauss")]
        self.assertEqual(method["name"], "Cuadratura gaussiana")
        self.assertEqual(method["category_label"], "Integración numérica")
        examples = self.client.get("/api/examples/?method=gauss").json()
        self.assertEqual(len(examples), 8)
        self.assertTrue(all(e["max_iterations"] == 12 and e["mode"] == "function" for e in examples))
        self.assertEqual([e["subintervals"] for e in examples], [1, 1, 1, 1, 1, 1, 2, 4])


class TheoryExampleTests(SimpleTestCase):
    """La página de teoría usa respuestas guardadas del solver: deben ser las
    que el solver devuelve hoy y mostrar los valores de Chapra."""

    def setUp(self):
        self.saved = json.loads(THEORY_EXAMPLE.read_text(encoding="utf-8"))

    def test_two_and_three_points_of_example_one(self):
        saved = rows(self.saved["function"])
        two, three = saved[1], saved[2]
        self.assertEqual([p["x_display"] for p in two["step"]["groups"][0]["points"]], ["0.16906", "0.63094"])
        self.assertEqual([p["f_display"] for p in two["step"]["groups"][0]["points"]], ["1.291851", "3.264593"])
        self.assertEqual((f"{two['G']:.6f}", f"{two['true_error']:.6f}", f"{two['relative_error']:.4f}"),
                         ("1.822578", "-0.182044", "11.0967"))
        self.assertAlmostEqual(two["bound"], 1.6384, places=12)
        self.assertEqual(f"{three['G']:.6f}", "1.640533")
        self.assertLess(abs(three["true_error"]), 1e-12)
        self.assertEqual(self.saved["function"]["cost"]["gauss_evaluations"], 3)

    def test_saved_responses_match_solver(self):
        for key, number in THEORY_KEYS.items():
            with self.subTest(example=number):
                result = json.loads(json.dumps(example(number)))
                result.pop("request", None)
                if key not in THEORY_CHARTS:
                    result.pop("chart_rows")
                    result.pop("curve")
                stored = {k: v for k, v in self.saved[key].items() if k != "request"}
                self.assertEqual(result, stored)
