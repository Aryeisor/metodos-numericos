"""Integración de Romberg: valores de referencia verificados con un script
independiente (fracciones exactas y los ejemplos precargados)."""

from fractions import Fraction

from django.test import SimpleTestCase
from rest_framework.test import APITestCase

from numeric_methods.examples_data import ROMBERG_EXAMPLES
from numeric_methods.serializers.integration import RombergSerializer
from numeric_methods.solvers.integration import romberg as romberg_module
from numeric_methods.solvers.integration.rules import SIMPSON_13, TRAPEZOID, apply
from numeric_methods.solvers.integration.romberg import NOT_SMOOTH, solve_romberg


def chapra_exact(x):
    return Fraction(1, 5) + 25 * x - 200 * x ** 2 + 675 * x ** 3 - 900 * x ** 4 + 400 * x ** 5


def exact_romberg(f, a, b, rows):
    """La tabla triangular en aritmética exacta (trapecio directo + Richardson)."""
    table = []
    for i in range(1, rows + 1):
        n = 2 ** (i - 1)
        h = (b - a) / n
        row = [TRAPEZOID.factor * h * sum(w * f(a + j * h) for j, w in enumerate(TRAPEZOID.weights(n)))]
        for k in range(2, i + 1):
            factor = 4 ** (k - 1)
            row.append((factor * row[-1] - table[-1][k - 2]) / (factor - 1))
        table.append(row)
    return table


def solve(**data):
    serializer = RombergSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return solve_romberg(serializer.validated_data).to_dict()


_CACHE = {}


def example(number):
    if number not in _CACHE:
        _CACHE[number] = solve(**ROMBERG_EXAMPLES[number - 1])
    return _CACHE[number]


def rows(result):
    return [step["extra"] for step in result["iterations"]]


def diagonal(result):
    return [row["best"] for row in rows(result)]


class ExactFractionTests(SimpleTestCase):
    def test_chapra(self):
        table = exact_romberg(chapra_exact, Fraction(0), Fraction(4, 5), 3)
        expected = [[Fraction(108, 625)], [Fraction(668, 625), Fraction(2564, 1875)],
                    [Fraction(928, 625), Fraction(3044, 1875), Fraction(3076, 1875)]]
        self.assertEqual(table, expected)
        for row, values in zip(rows(example(1)), expected):
            for got, want in zip(row["values"], values):
                self.assertAlmostEqual(got, float(want), places=12)

    def test_fifth_power(self):
        table = exact_romberg(lambda x: x ** 5, Fraction(0), Fraction(2), 4)
        expected = [[32], [17, 12], [Fraction(197, 16), Fraction(43, 4), Fraction(32, 3)],
                    [Fraction(2837, 256), Fraction(683, 64), Fraction(32, 3), Fraction(32, 3)]]
        self.assertEqual(table, expected)
        for row, values in zip(rows(example(4)), expected):
            for got, want in zip(row["values"], values):
                self.assertAlmostEqual(got, float(want), places=12)


class ChapraExampleTests(SimpleTestCase):
    def setUp(self):
        self.result = example(1)
        self.rows = rows(self.result)

    def test_first_rows(self):
        expected = [[0.1728], [1.0688, 1.367467], [1.4848, 1.623467, 1.640533]]
        for row, values in zip(self.rows, expected):
            self.assertEqual([round(v, 6) for v in row["values"]], values)
        self.assertEqual(self.result["integral"]["kind"], "exact")
        self.assertAlmostEqual(self.result["integral"]["value"], 3076 / 1875, places=12)

    def test_coherent_decimals_of_R33(self):
        R32, R33 = self.rows[2]["extrapolations"]
        self.assertEqual(R32["decimals"], 6)
        self.assertEqual((R32["same"], R32["previous"], R32["numerator"], R32["quotient"]),
                         ("1.4848", "1.0688", "4.8704", "1.623467"))
        # Con 6 decimales (16(1.623467) − 1.367467)/15 = 1.640534 ≠ 1.640533: se usan 8.
        self.assertEqual(R33["decimals"], 8)
        self.assertEqual(
            (R33["factor"], R33["divisor"], R33["same"], R33["previous"], R33["product"], R33["numerator"],
             R33["quotient"]),
            (16, 15, "1.62346667", "1.36746667", "25.97546672", "24.60800005", "1.64053334"),
        )
        self.assertTrue(R33["coherent"])

    def test_stop_and_evaluations(self):
        self.assertTrue(self.result["converged"])
        self.assertEqual(self.result["iterations_used"], 6)
        self.assertEqual(self.result["evaluations"], 33)
        self.assertEqual(self.rows[-1]["evaluations"], 33)
        self.assertEqual([c["name"] for c in self.result["columns"][:4]],
                         ["Trapecio", "Simpson 1/3", "Boole", "Nivel 4"])
        self.assertEqual(self.result["columns"][2]["order_text"], "O(h⁶)")

    def test_errors_of_row_3(self):
        row = self.rows[2]
        self.assertEqual(f"{row['estimated_error']:.6f}", "0.273067")
        self.assertEqual(f"{row['approx_error']:.6f}", "16.644993")
        self.assertIsNone(self.rows[0]["estimated_error"])
        self.assertIsNone(self.rows[0]["approx_error"])
        self.assertAlmostEqual(row["true_error"], 0, places=12)

    def test_cost(self):
        cost = self.result["cost"]
        self.assertEqual((cost["first_row"], cost["first_evaluations"], cost["trapezoid_evaluations"],
                          cost["simpson_evaluations"], cost["romberg_evaluations"]), (3, 5, 2049, 65, 33))
        self.assertEqual(
            cost["text"],
            "Romberg llegó a |Eₜ| ≤ 0.000001 en la fila 3, con 5 evaluaciones; el trapecio habría necesitado 2049 "
            "y Simpson 65. Por el mínimo de 6 filas, el sistema usó 33.",
        )

    def test_error_table(self):
        errors = self.rows[1]["errors"]
        self.assertAlmostEqual(errors[0], 3076 / 1875 - 1.0688, places=12)
        self.assertAlmostEqual(errors[1], 3076 / 1875 - 2564 / 1875, places=12)


class IdentityTests(SimpleTestCase):
    def test_columns_1_and_2(self):
        for number in (1, 2, 6):
            # Tolerancia inalcanzable para llegar a 8 filas; la comparación de costo no se revisa aquí.
            data = dict(ROMBERG_EXAMPLES[number - 1], max_iterations=8, tolerance=1e-30)
            original, romberg_module.COST_LIMIT = romberg_module.COST_LIMIT, 2 ** 8
            try:
                result = solve(**data)
            finally:
                romberg_module.COST_LIMIT = original
            identities = result["verification"]["identities"]
            self.assertEqual(len(identities), 8)
            for identity, row in zip(identities, rows(result)):
                with self.subTest(example=number, row=row["i"]):
                    self.assertTrue(identity["trapezoid"]["ok"])
                    self.assertEqual(identity["trapezoid"]["value"], row["values"][0])
                    if row["i"] == 1:
                        self.assertIsNone(identity["simpson"])
                    else:
                        self.assertTrue(identity["simpson"]["ok"])
                        self.assertEqual(identity["simpson"]["value"], row["values"][1])

    def test_identity_values_match_the_rule_engines(self):
        identity = example(1)["verification"]["identities"][2]
        values = [float(chapra_exact(Fraction(j, 5))) for j in range(5)]
        self.assertAlmostEqual(identity["trapezoid"]["other"], apply(TRAPEZOID, values, 0.2), places=12)
        self.assertAlmostEqual(identity["simpson"]["other"], apply(SIMPSON_13, values, 0.2), places=12)


class StoppingRowTests(SimpleTestCase):
    EXPECTED = {
        2: (6, [0.68394, 0.74718, 0.746834, 0.746824]),
        3: (6, [0, 2.094395, 1.998571, 2.000006, 2]),
        4: (6, [32, 12, 10.666667]),
        5: (13, [0.5, 0.638071, 0.657757, 0.663608, 0.665593, 0.666288]),
        6: (6, [0.75, 0.694444, 0.693175, 0.693147]),
    }

    def test_rows_and_diagonals(self):
        for number, (stop, values) in self.EXPECTED.items():
            with self.subTest(example=number):
                result = example(number)
                self.assertTrue(result["converged"])
                self.assertEqual(result["iterations_used"], stop)
                self.assertEqual([round(v, 6) for v in diagonal(result)[:len(values)]], values)

    def test_example_2_row_3_and_reference(self):
        result = example(2)
        self.assertEqual(result["integral"]["kind"], "reference")
        self.assertEqual(f"{result['integral']['value']:.6f}", "0.746824")
        self.assertEqual([round(v, 6) for v in rows(result)[2]["values"]], [0.742984, 0.746855, 0.746834])

    def test_example_4_R33_is_exact(self):
        self.assertAlmostEqual(rows(example(4))[2]["values"][2], 32 / 3, places=12)
        self.assertEqual([round(v, 6) for v in rows(example(4))[2]["values"]], [12.3125, 10.75, 10.666667])

    def test_example_5_evaluations(self):
        self.assertEqual(example(5)["evaluations"], 4097)


class SmoothnessWarningTests(SimpleTestCase):
    def test_only_example_5(self):
        self.assertIn(NOT_SMOOTH, example(5)["warnings"])
        for number in (1, 2, 3, 4, 6, 7, 8):
            with self.subTest(example=number):
                self.assertNotIn(NOT_SMOOTH, example(number)["warnings"])

    def test_example_1_ratios_are_rounding_noise(self):
        # Las razones de las filas 4 a 6 son de errores ≈ 10⁻¹⁵: no cuentan.
        tail = rows(example(1))[3:]
        self.assertTrue(all(row["estimated_error"] < 1e-13 for row in tail))
        self.assertEqual(example(1)["warnings"], [])


class CostTests(SimpleTestCase):
    EXPECTED = {
        2: (4, 9, 257, 17),
        3: (5, 17, 2049, 65),
        4: (3, 5, 8193, 129),
        5: (12, 2049, 4097, 2049),
        6: (4, 9, 257, 17),
    }

    def test_examples(self):
        for number, expected in self.EXPECTED.items():
            with self.subTest(example=number):
                cost = example(number)["cost"]
                self.assertEqual((cost["first_row"], cost["first_evaluations"], cost["trapezoid_evaluations"],
                                  cost["simpson_evaluations"]), expected)
        self.assertIn("necesitó llegar a la fila 13: el sistema usó 4097", example(5)["cost"]["text"])

    def test_limit_text(self):
        original = romberg_module.COST_LIMIT
        romberg_module.COST_LIMIT = 2 ** 8
        try:
            cost = solve(function="sqrt(x)", a=0, b=1, tolerance=1e-9)["cost"]
        finally:
            romberg_module.COST_LIMIT = original
        self.assertIsNone(cost["trapezoid_evaluations"])
        self.assertIn("más de 257", cost["text"])


class TableModeTests(APITestCase):
    def test_example_7(self):
        result = example(7)
        expected = [[0.1728], [1.0688, 1.367467], [1.4848, 1.623467, 1.640533],
                    [1.6008, 1.639467, 1.640533, 1.640533]]
        self.assertEqual([[round(v, 6) for v in row["values"]] for row in rows(result)], expected)
        self.assertEqual(f"{rows(result)[-1]['true_error']:.6f}", "0.000000")
        self.assertEqual([row["data_points"] for row in rows(result)][:3], [[0, 8], [0, 4, 8], [0, 2, 4, 6, 8]])
        self.assertEqual(rows(result)[1]["new_points"], [4])
        self.assertTrue(all(c["ok"] for c in result["verification"]["data"]))
        self.assertIn("Con 9 puntos sólo se pueden armar 4 filas", result["notes"][0])
        self.assertIsNone(result["cost"])

    def test_example_8(self):
        result = example(8)
        expected = [[0.68394], [0.73137, 0.74718], [0.742984, 0.746855, 0.746834]]
        self.assertEqual([[round(v, 6) for v in row["values"]] for row in rows(result)], expected)
        self.assertEqual(f"{result['solution'][0]:.6f}", "0.746834")
        self.assertIsNone(result["integral"])
        self.assertTrue(all(i["trapezoid"]["ok"] for i in result["verification"]["identities"]))

    def test_three_points(self):
        result = solve(mode="table", points=[[0, 0], [1, 1], [2, 4]])
        self.assertEqual(result["iterations_used"], 2)
        self.assertEqual([round(v, 6) for v in rows(result)[1]["values"]], [3, 2.666667])

    def test_seven_points_is_rejected(self):
        response = self.client.post("/api/solve/romberg/", {
            "mode": "table", "points": [[i, i] for i in range(7)],
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["points"], [
            "Romberg necesita 2ᵐ + 1 puntos igualmente espaciados (3, 5, 9, 17 o 33), porque cada fila duplica el "
            "número de segmentos. Tienes 7 puntos: puedes usar el trapecio o Simpson."
        ])

    def test_uneven_spacing_is_rejected(self):
        response = self.client.post("/api/solve/romberg/", {
            "mode": "table", "points": [[0, 1], [0.25, 1], [0.5, 1], [1, 1], [1.5, 1]],
        }, format="json")
        self.assertEqual(response.status_code, 400)
        message = response.json()["points"][0]
        self.assertTrue(message.startswith("Romberg necesita datos igualmente espaciados"))
        self.assertIn("puedes usar el método del trapecio", message)

    def test_thirty_three_points(self):
        points = [[j / 32, (j / 32) ** 2] for j in range(33)]
        result = solve(mode="table", points=points, compare_function="x^2")
        self.assertEqual(result["iterations_used"], 6)
        self.assertAlmostEqual(result["solution"][0], 1 / 3, places=12)

    def test_altered_data_point_is_flagged(self):
        data = dict(ROMBERG_EXAMPLES[6])
        data["points"] = [list(p) for p in data["points"]]
        data["points"][3][1] = 1.7
        result = solve(**data)
        self.assertFalse(result["verification"]["data"][3]["ok"])
        self.assertTrue(any("Punto 3" in w for w in result["warnings"]))


class ValidationTests(APITestCase):
    URL = "/api/solve/romberg/"

    def assert_error(self, payload, fragment):
        response = self.client.post(self.URL, payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn(fragment, str(response.json()))

    def test_errors(self):
        self.assert_error({"function": "x", "a": 1, "b": 1}, "debe ser menor")
        self.assert_error({"function": "x", "a": 2, "b": 1}, "debe ser menor")
        self.assert_error({"function": "1/x", "a": 0, "b": 1}, "límite a")
        self.assert_error({"function": "x + y", "a": 0, "b": 1}, "f(x)")
        self.assert_error({"function": "x", "a": 0, "b": 1, "max_iterations": 5},
                          "El máximo de filas debe estar entre 6 y 20.")
        self.assert_error({"function": "x", "a": 0, "b": 1, "max_iterations": 21},
                          "El máximo de filas debe estar entre 6 y 20.")

    def test_interior_singularity_stops(self):
        result = solve(function="1/(x - 1)", a=0, b=2)
        self.assertFalse(result["converged"])
        # La fila 2 necesita f(1): se detiene antes de completarla.
        self.assertEqual(result["iterations_used"], 1)
        self.assertTrue(any("no está definida en x = 1" in w for w in result["warnings"]))
        self.assertIsNone(result["integral"]["value"])


class EndpointTests(APITestCase):
    def test_solve(self):
        response = self.client.post("/api/solve/romberg/", {"function": "x^2", "a": 0, "b": 2}, format="json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["category"], "integration")
        self.assertEqual(data["max_iterations"], 15)

    def test_catalog_and_examples(self):
        catalog = self.client.get("/api/methods/").json()
        slugs = [m["slug"] for m in catalog]
        self.assertEqual(slugs.index("romberg"), slugs.index("simpson") + 1)
        method = catalog[slugs.index("romberg")]
        self.assertEqual(method["name"], "Integración de Romberg")
        self.assertEqual(method["category_label"], "Integración numérica")
        examples = self.client.get("/api/examples/?method=romberg").json()
        self.assertEqual(len(examples), 8)
        self.assertTrue(all(e["max_iterations"] == 15 and e["n0"] == 1 for e in examples))
