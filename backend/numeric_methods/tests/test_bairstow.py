import json
import math

from django.test import SimpleTestCase
from rest_framework.test import APITestCase

from numeric_methods.examples_data import EXAMPLES
from numeric_methods.solvers.polynomial.bairstow import quadratic_roots, solve_bairstow
from numeric_methods.solvers.polynomial.synthetic import b_table, c_table
from numeric_methods.solvers.polynomial.validation import (
    PolynomialValidationError,
    coefficients_from_text,
    validate_coefficients,
)
from numeric_methods.solvers.validation import MIN_ITERATIONS

CHAPRA = "x^5 - 3.5x^4 + 2.75x^3 + 2.125x^2 - 3.875x + 1.25"
CHAPRA_COEFFICIENTS = [1, -3.5, 2.75, 2.125, -3.875, 1.25]

# Raíces esperadas de cada ejemplo precargado (re, im).
EXPECTED_ROOTS = {
    "bairstow-cubica-enteras": [(1, 0), (-2, 0), (3, 0)],
    "bairstow-chapra": [(-1, 0), (0.5, 0), (2, 0), (1, 0.5), (1, -0.5)],
    "bairstow-cubica-reales": [(1, 0), (2, 0), (3, 0)],
    "bairstow-cubica-compleja": [(1, 0), (0, 1), (0, -1)],
    "bairstow-terminos-faltantes": [(1, 0), (-1, 0), (2, 0), (-2, 0)],
    "bairstow-dos-pares": [(0, 1), (0, -1), (1, 2), (1, -2)],
    "bairstow-principal-2": [(0.5, 0), (-0.5, math.sqrt(3) / 2), (-0.5, -math.sqrt(3) / 2)],
    "bairstow-grado-6": [(-1, 1), (-1, -1), (1, 0), (2, 0), (0, 2), (0, -2)],
    "bairstow-raiz-nula": [(0, 0), (1, 0), (-1, 0), (3, 0), (-2, 0)],
}


def solve(coefficients=None, text=None, r0=-1, s0=-1, tolerance=0.0001, max_iterations=100):
    if text is not None:
        coefficients = coefficients_from_text(text)
    return solve_bairstow({
        "coefficients": coefficients, "polynomial": text, "r0": r0, "s0": s0,
        "tolerance": tolerance, "max_iterations": max_iterations,
    }).to_dict()


def root_set(roots):
    return sorted((round(r["re"], 5), round(r["im"], 5)) for r in roots)


def assert_roots(test, roots, expected, places=5):
    got = root_set(roots)
    want = sorted((round(re, 5), round(im, 5)) for re, im in expected)
    test.assertEqual(len(got), len(want))
    for (gr, gi), (wr, wi) in zip(got, want):
        test.assertAlmostEqual(gr, wr, places=places - 1)
        test.assertAlmostEqual(gi, wi, places=places - 1)


class SyntheticDivisionTests(SimpleTestCase):
    def test_b_table_has_the_four_rows(self):
        table = b_table([1, -3.5, 2.75, 2.125, -3.875, 1.25], -1, -1)
        self.assertEqual(table["coefficients"], [1, -3.5, 2.75, 2.125, -3.875, 1.25])
        self.assertEqual(table["r_terms"], [None, -1.0, 4.5, -6.25, -0.375, 10.5])
        self.assertEqual(table["s_terms"], [None, None, -1.0, 4.5, -6.25, -0.375])
        self.assertEqual(table["result"], [1, -4.5, 6.25, 0.375, -10.5, 11.375])

    def test_c_table_does_not_compute_c0(self):
        table = c_table([1, -4.5, 6.25, 0.375, -10.5, 11.375], -1, -1)
        self.assertEqual(table["result"], [1, -5.5, 10.75, -4.875, -16.375, None])
        self.assertIsNone(table["r_terms"][-1])
        self.assertIsNone(table["s_terms"][-1])


class ChapraFirstIterationTests(SimpleTestCase):
    """Primera iteración del ejemplo de Chapra (r₀ = s₀ = −1), calculada a mano."""

    def setUp(self):
        self.result = solve(text=CHAPRA, tolerance=1)
        self.extra = self.result["iterations"][0]["extra"]

    def test_b_and_c(self):
        self.assertEqual(self.extra["b_table"]["result"], [1, -4.5, 6.25, 0.375, -10.5, 11.375])
        self.assertEqual(self.extra["c_table"]["result"][:5], [1, -5.5, 10.75, -4.875, -16.375])
        self.assertEqual((self.extra["b1"], self.extra["b0"]), (-10.5, 11.375))
        self.assertEqual((self.extra["c1"], self.extra["c2"], self.extra["c3"]), (-16.375, -4.875, 10.75))

    def test_cramer(self):
        self.assertAlmostEqual(self.extra["D"], 199.796875, places=9)
        self.assertAlmostEqual(self.extra["D_r"], 71.09375, places=9)
        self.assertAlmostEqual(self.extra["D_s"], 227.390625, places=9)
        self.assertEqual(self.extra["matrix"], [[-4.875, 10.75], [-16.375, -4.875]])
        self.assertEqual(self.extra["rhs"], [10.5, -11.375])

    def test_update_and_errors(self):
        self.assertAlmostEqual(self.extra["delta_r"], 0.355830, places=6)
        self.assertAlmostEqual(self.extra["delta_s"], 1.138109, places=6)
        self.assertAlmostEqual(self.extra["r_new"], -0.644170, places=6)
        self.assertAlmostEqual(self.extra["s_new"], 0.138109, places=6)
        self.assertAlmostEqual(self.extra["eps_r"], 55.24, places=2)
        self.assertAlmostEqual(self.extra["eps_s"], 824.07, places=2)
        self.assertEqual(self.result["iterations"][0]["error"], self.extra["eps_s"])
        self.assertEqual(self.extra["absolute"], {"r": False, "s": False})
        self.assertEqual(self.extra["factor"], 0)


class ChapraFinalResultTests(SimpleTestCase):
    def setUp(self):
        self.result = solve(text=CHAPRA, tolerance=1)

    def test_first_factor_and_quotient(self):
        first = self.result["factors"][0]
        self.assertEqual(first["method"], "bairstow")
        self.assertAlmostEqual(first["r"], -0.5, places=6)
        self.assertAlmostEqual(first["s"], 0.5, places=6)
        assert_roots(self, first["roots"], [(0.5, 0), (-1, 0)])
        for got, expected in zip(first["quotient"]["coefficients"], [1, -4, 5.25, -2.5]):
            self.assertAlmostEqual(got, expected, places=6)
        self.assertEqual(first["quotient"]["latex"], "x^{3} - 4 x^{2} + 5.25 x - 2.5")
        self.assertAlmostEqual(first["residue"]["b1"], 0, places=6)
        self.assertAlmostEqual(first["residue"]["b0"], 0, places=6)

    def test_all_roots_and_structure(self):
        self.assertTrue(self.result["converged"])
        assert_roots(self, self.result["roots"], EXPECTED_ROOTS["bairstow-chapra"])
        self.assertEqual([f["method"] for f in self.result["factors"]],
                         ["bairstow", "bairstow", "lineal_directa"])
        self.assertEqual(self.result["variables"], ["r", "s"])
        self.assertEqual(self.result["polynomial"]["coefficients"], CHAPRA_COEFFICIENTS)
        self.assertIn(r"\left(x - 2\right)", self.result["factorization"])
        self.assertTrue(all(r["check"] < 1e-5 for r in self.result["roots"]))
        json.dumps(self.result, allow_nan=False)


class ExamplesTests(SimpleTestCase):
    def test_every_example_converges_to_the_expected_roots(self):
        examples = EXAMPLES["bairstow"]
        self.assertEqual(len(examples), 9)
        self.assertEqual(set(EXPECTED_ROOTS), {e["id"] for e in examples})
        self.assertEqual({e["mode"] for e in examples}, {"text", "coefficients"})
        for example in examples:
            with self.subTest(example=example["id"]):
                result = solve(example["coefficients"], example["polynomial"],
                               example["r0"], example["s0"], example["tolerance"], example["max_iterations"])
                self.assertTrue(result["converged"], result["warnings"])
                assert_roots(self, result["roots"], EXPECTED_ROOTS[example["id"]], places=4)


class SpecialCasesTests(SimpleTestCase):
    def test_minimum_six_iterations_per_factor(self):
        # (x − 1)(x − 2) = x² − 3x + 2 ⇒ r = 3, s = −2: ya es el factor exacto.
        result = solve([1, -6, 11, -6], r0=3, s0=-2)
        self.assertEqual(result["factors"][0]["iterations_used"], MIN_ITERATIONS)
        for example in EXAMPLES["bairstow"]:
            result = solve(example["coefficients"], example["polynomial"], example["r0"], example["s0"],
                           example["tolerance"])
            for factor in result["factors"]:
                if factor["method"] == "bairstow":
                    self.assertGreaterEqual(factor["iterations_used"], MIN_ITERATIONS)

    def test_missing_terms_have_explicit_zeros(self):
        self.assertEqual(coefficients_from_text("x^4 + 4 - 5x^2"), [1, 0, -5, 0, 4])
        self.assertEqual(coefficients_from_text("x^4 - 1"), [1, 0, 0, 0, -1])
        result = solve(text="x^4 - 5x^2 + 4")
        self.assertEqual(result["polynomial"]["coefficients"], [1, 0, -5, 0, 4])

    def test_zero_roots_are_extracted_first(self):
        result = solve(text="x^5 - x^4 - 7x^3 + x^2 + 6x")
        self.assertEqual(result["zero_roots"], 1)
        self.assertEqual(result["factors"][0]["dividend"]["coefficients"], [1, -1, -7, 1, 6])
        self.assertEqual(sum(1 for r in result["roots"] if r.get("source") == "paso_previo"), 1)
        self.assertTrue(any("Paso previo" in note for note in result["notes"]))
        self.assertTrue(result["factorization"].startswith("x \\left("))

    def test_reduced_degree_below_three_is_solved_directly(self):
        # x⁴ − 2x³ = x³ (x − 2): queda grado 1, sin iteraciones.
        result = solve(text="x^4 - 2x^3")
        self.assertEqual(result["zero_roots"], 3)
        self.assertEqual(result["iterations"], [])
        self.assertEqual([f["method"] for f in result["factors"]], ["lineal_directa"])
        assert_roots(self, result["roots"], [(0, 0), (0, 0), (0, 0), (2, 0)])
        self.assertTrue(any("se resuelve directamente" in note for note in result["notes"]))
        self.assertTrue(result["converged"])

    def test_quadratic_and_linear_closures(self):
        quadratic = solve(text="x^4 - 5x^2 + 4")
        self.assertEqual([f["method"] for f in quadratic["factors"]], ["bairstow", "cuadratica_directa"])
        closure = quadratic["factors"][1]
        self.assertNotIn("iteration_indices", closure)
        self.assertIn("discriminant", closure)
        linear = solve(text=CHAPRA, tolerance=1)
        self.assertEqual(linear["factors"][-1]["method"], "lineal_directa")
        self.assertEqual(linear["factors"][-1]["factor_latex"], "x - 2")

    def test_negligible_discriminant_is_a_double_root(self):
        discriminant, roots, double = quadratic_roots(2, -1 + 1e-16)
        self.assertTrue(double)
        self.assertEqual(discriminant, 0.0)
        self.assertEqual(roots, [{"re": 1.0, "im": 0.0}, {"re": 1.0, "im": 0.0}])
        # x³ (x − 1)²: el paso previo deja x² − 2x + 1, raíz doble.
        result = solve(text="x^5 - 2x^4 + x^3")
        self.assertTrue(result["factors"][0]["double_root"])
        self.assertTrue(any("raíz doble" in note for note in result["notes"]))

    def test_complex_roots_are_computed_without_complex_arithmetic(self):
        discriminant, roots, double = quadratic_roots(2, -1.25)
        self.assertEqual(discriminant, -1.0)
        self.assertEqual(roots, [{"re": 1.0, "im": 0.5}, {"re": 1.0, "im": -0.5}])
        self.assertFalse(double)

    def test_absolute_error_is_used_when_r_is_zero(self):
        # x³ − x² + x − 1 = (x − 1)(x² + 1): el factor real tiene r = 0.
        result = solve(text="x^3 - x^2 + x - 1", r0=0.5, s0=-0.5)
        flags = [it["extra"]["absolute"]["r"] for it in result["iterations"]]
        self.assertTrue(any(flags))
        self.assertTrue(any("error absoluto" in w for w in result["warnings"]))


class TextParsingTests(SimpleTestCase):
    def test_accepted_forms(self):
        self.assertEqual(coefficients_from_text("x^3 - 6x^2 + 11x - 6 = 0"), [1, -6, 11, -6])
        self.assertEqual(coefficients_from_text("x^3 = 6x^2 - 11x + 6"), [1, -6, 11, -6])
        self.assertEqual(coefficients_from_text("(x - 1)(x - 2)(x - 3)"), [1, -6, 11, -6])
        coefficients = coefficients_from_text("x^3 + pi*x - sqrt(2)")
        self.assertAlmostEqual(coefficients[2], math.pi)
        self.assertAlmostEqual(coefficients[3], -math.sqrt(2))

    def test_rejected_forms(self):
        cases = {
            "x^2 - 1": "fórmula cuadrática",
            "2x + 1": "despejando x",
            "x^11 + 1": "hasta grado 10",
            "sin(x) + x^3": "no es un polinomio en x",
            "1/x + x^3": "no es un polinomio en x",
            "sqrt(x) + x^3": "no es un polinomio en x",
            "x^3 + y": "sólo puede depender de x",
            "x^3 - x^3 + 5": "constante",
            "((x^1000)^1000)": "grado demasiado alto",
        }
        for text, fragment in cases.items():
            with self.subTest(text=text):
                with self.assertRaises(PolynomialValidationError) as ctx:
                    coefficients_from_text(text)
                self.assertIn(fragment, " ".join(ctx.exception.errors))

    def test_coefficients_mode(self):
        self.assertEqual(validate_coefficients([2, 1, 1, -1]), [2.0, 1.0, 1.0, -1.0])
        for coefficients, fragment in (([0, 1, 2, 3, 4], "coeficiente principal"),
                                       ([1, 2, 3], "fórmula cuadrática"),
                                       ([1] * 12, "hasta grado 10"),
                                       ([1, 2, 1e101, 3], "demasiado grande")):
            with self.subTest(coefficients=coefficients):
                with self.assertRaises(PolynomialValidationError) as ctx:
                    validate_coefficients(coefficients)
                self.assertIn(fragment, " ".join(ctx.exception.errors))


class FailureTests(SimpleTestCase):
    def test_singular_determinant(self):
        # Desde (−1, −1) la primera iteración cae en r = s = 0 y D = 0.
        result = solve(text="x^3 - x^2 + x - 1")
        self.assertFalse(result["converged"])
        self.assertEqual(result["failure"], {"factor": 0, "iteration": 2, "reason": "singular"})
        self.assertTrue(any("determinante D" in w for w in result["warnings"]))
        self.assertEqual(result["iterations"][-1]["extra"]["D"], 0.0)
        self.assertIsNone(result["factorization"])
        json.dumps(result, allow_nan=False)

    def test_max_iterations_reports_partial_roots(self):
        # Desde (0.5, −0.5) el primer factor converge en 6 iteraciones y el
        # segundo necesita 26: con máximo 10 se detiene en el segundo.
        result = solve(text=CHAPRA, r0=0.5, s0=-0.5, tolerance=1, max_iterations=10)
        self.assertFalse(result["converged"])
        self.assertEqual(result["failure"], {"factor": 1, "iteration": 10, "reason": "max_iterations"})
        self.assertEqual(len(result["roots"]), 2)
        self.assertTrue(result["factors"][0]["converged"])
        self.assertFalse(result["factors"][1]["converged"])
        self.assertTrue(any("no alcanzó la tolerancia" in w for w in result["warnings"]))


class BairstowEndpointTests(APITestCase):
    URL = "/api/solve/bairstow/"

    def _post(self, **payload):
        return self.client.post(self.URL, payload, format="json")

    def _flat_errors(self, response, field):
        self.assertEqual(response.status_code, 400, response.content)
        messages = response.json()[field]
        self.assertTrue(all(isinstance(m, str) for m in messages))
        return " ".join(messages)

    def test_text_and_coefficients_modes(self):
        for payload in ({"polynomial": "x^3 - 6x^2 + 11x - 6"}, {"coefficients": [1, -6, 11, -6]}):
            with self.subTest(payload=payload):
                response = self._post(**payload)
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data["method"], "bairstow")
                self.assertEqual(data["category"], "polynomial")
                self.assertTrue(data["converged"])
                self.assertEqual(data["variables"], ["r", "s"])
                for key in ("polynomial", "zero_roots", "factors", "roots", "factorization", "failure"):
                    self.assertIn(key, data)
                self.assertEqual(data["r0"], -1.0)
                self.assertEqual(data["tolerance_percent"], 0.0001)
                self.assertIn("b_table", data["iterations"][0]["extra"])

    def test_examples_by_method(self):
        response = self.client.get("/api/examples/?method=bairstow")
        self.assertEqual(response.status_code, 200)
        examples = response.json()
        self.assertGreaterEqual(len(examples), 6)
        for example in examples:
            payload = {k: example[k] for k in ("r0", "s0", "tolerance", "max_iterations")}
            if example["mode"] == "text":
                payload["polynomial"] = example["polynomial"]
            else:
                payload["coefficients"] = example["coefficients"]
            self.assertTrue(self._post(**payload).json()["converged"])

    def test_rejections(self):
        self.assertIn("fórmula cuadrática", self._flat_errors(self._post(polynomial="x^2 + 1"), "polynomial"))
        self.assertIn("hasta grado 10", self._flat_errors(self._post(polynomial="x^11 - 1"), "polynomial"))
        for text in ("sin(x) + x^3", "1/x + x^3", "sqrt(x) + x^3", "x^3 + y"):
            self._flat_errors(self._post(polynomial=text), "polynomial")
        self.assertIn("coeficiente principal",
                      self._flat_errors(self._post(coefficients=[0, 1, 2, 3, 4]), "coefficients"))
        self.assertIn("exactamente uno",
                      self._flat_errors(self._post(polynomial="x^3 - 1", coefficients=[1, 0, 0, -1]), "polynomial"))
        self.assertIn("exactamente uno", self._flat_errors(self._post(), "polynomial"))
        for tolerance in (0, -1):
            self.assertIn("mayor que 0",
                          self._flat_errors(self._post(polynomial="x^3 - 1", tolerance=tolerance), "tolerance"))

    def test_failure_is_200_with_warning(self):
        response = self._post(polynomial="x^3 - x^2 + x - 1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["converged"])
        self.assertEqual(data["failure"]["reason"], "singular")


class VerificationTests(SimpleTestCase):
    """Apartado «Comprobación»: sustitución de cada raíz en el polinomio original."""

    def by_root(self, result):
        return {(round(r["re"], 6), round(r["im"], 6)): r["verification"] for r in result["roots"]}

    def test_integer_roots_term_by_term(self):
        result = solve(text="x^3 - 2x^2 - 5x + 6", r0=-1, s0=-1, tolerance=1)
        self.assertTrue(result["converged"])
        checks = self.by_root(result)
        expected = {1: [1, -2, -5, 6], -2: [-8, -8, 10, 6], 3: [27, -18, -15, 6]}
        self.assertEqual(sorted(checks), sorted((float(x), 0.0) for x in expected))
        for root, values in expected.items():
            with self.subTest(root=root):
                check = checks[(float(root), 0.0)]
                self.assertEqual([t["value"]["re"] for t in check["terms"]], values)
                self.assertEqual([t["power"] for t in check["terms"]], [3, 2, 1, 0])
                self.assertEqual([t["coefficient"] for t in check["terms"]], [1, -2, -5, 6])
                self.assertTrue(all(t["value"]["im"] == 0 for t in check["terms"]))
                self.assertEqual(check["value"], {"re": 0.0, "im": 0.0})
                self.assertEqual(check["abs"], 0.0)
                self.assertTrue(check["is_zero"])
        json.dumps(result, allow_nan=False)

    def test_missing_powers_are_omitted(self):
        result = solve(coefficients=[1, 0, -5, 0, 4])
        for root in result["roots"]:
            with self.subTest(root=root["re"]):
                self.assertEqual([t["power"] for t in root["verification"]["terms"]], [4, 2, 0])
                self.assertTrue(root["verification"]["is_zero"])

    def test_complex_pair_is_approximately_zero(self):
        result = solve(text="x^3 - x^2 + x - 1", r0=0.5, s0=-0.5)
        self.assertTrue(result["converged"])
        complex_roots = [r for r in result["roots"] if r["im"] != 0]
        self.assertEqual(len(complex_roots), 2)
        for root in complex_roots:
            check = root["verification"]
            self.assertTrue(check["is_zero"])
            self.assertAlmostEqual(check["value"]["re"], 0, places=6)
            self.assertAlmostEqual(check["value"]["im"], 0, places=6)
            self.assertAlmostEqual(check["abs"], root["check"])
            # (±i)³ = ∓i: el término x³ es imaginario puro.
            cube = check["terms"][0]
            self.assertEqual(cube["power"], 3)
            self.assertAlmostEqual(cube["x_power"]["re"], 0, places=6)
            self.assertAlmostEqual(cube["x_power"]["im"], -round(root["im"]), places=6)

    def test_zero_root_is_checked(self):
        result = solve(text="x^5 - x^4 - 7x^3 + x^2 + 6x")
        zero = [r for r in result["roots"] if r.get("source") == "paso_previo"]
        self.assertEqual(len(zero), 1)
        check = zero[0]["verification"]
        # a₀ = 0 no aparece; los demás términos valen 0 en x = 0.
        self.assertEqual([t["power"] for t in check["terms"]], [5, 4, 3, 2, 1])
        self.assertTrue(all(t["value"]["re"] == 0 for t in check["terms"]))
        self.assertEqual(check["value"], {"re": 0.0, "im": 0.0})
        self.assertTrue(check["is_zero"])

    def test_large_tolerance_leaves_a_visible_residue(self):
        # Con εs = 1 % el residuo de Chapra sigue siendo ≈ 0 relativo a la
        # escala; con εs = 10 % el factor se cierra antes y el residuo se nota.
        chapra = solve(text=CHAPRA, tolerance=1)
        self.assertTrue(all(r["verification"]["is_zero"] for r in chapra["roots"]))
        loose = solve(text=CHAPRA, tolerance=10)
        self.assertTrue(loose["converged"])
        self.assertTrue(any(not r["verification"]["is_zero"] for r in loose["roots"]))
