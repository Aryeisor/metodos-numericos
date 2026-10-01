from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from numeric_methods.examples_data import EXAMPLES, all_examples
from numeric_methods.registry import CATEGORIES, METHODS, public_catalog
from numeric_methods.solvers.base import IterationStep, SolverResult


class RegistryConsistencyTests(SimpleTestCase):
    def test_every_method_is_well_formed(self):
        for slug, spec in METHODS.items():
            with self.subTest(method=slug):
                self.assertEqual(spec.slug, slug)
                self.assertIn(spec.category, CATEGORIES)
                self.assertTrue(callable(spec.solver))
                self.assertTrue(hasattr(spec.serializer, "is_valid"))

    def test_every_method_has_a_solve_url(self):
        for slug in METHODS:
            with self.subTest(method=slug):
                self.assertEqual(reverse(f"solve-{slug}"), f"/api/solve/{slug}/")

    def test_every_method_has_examples(self):
        for slug in METHODS:
            with self.subTest(method=slug):
                self.assertTrue(EXAMPLES.get(slug))

    def test_examples_belong_to_registered_methods(self):
        self.assertLessEqual(set(EXAMPLES), set(METHODS))


class SolverResultTests(SimpleTestCase):
    def test_meta_is_merged_at_top_level(self):
        result = SolverResult(
            method="m", category="c", converged=True,
            iterations=[IterationStep(1, [1.0], 0.5)], solution=[1.0], variables=["x1"],
            meta={"reordered": False},
        )
        data = result.to_dict()
        self.assertEqual(data["iterations"], [{"iteration": 1, "x": [1.0], "error": 0.5}])
        self.assertEqual(data["iterations_used"], 1)
        self.assertFalse(data["reordered"])

    def test_meta_cannot_overwrite_common_fields(self):
        result = SolverResult(
            method="m", category="c", converged=True, iterations=[], solution=[],
            variables=[], meta={"solution": "pisado"},
        )
        with self.assertRaises(ValueError):
            result.to_dict()

    def test_iteration_extra_is_serialized_only_when_present(self):
        self.assertNotIn("extra", IterationStep(1, [0.0], None).to_dict())
        self.assertEqual(IterationStep(1, [0.0], None, {"J": [[1]]}).to_dict()["extra"], {"J": [[1]]})


class MethodsEndpointTests(APITestCase):
    def test_lists_registered_methods_with_category_labels(self):
        response = self.client.get("/api/methods/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), public_catalog())
        self.assertEqual(
            [(m["slug"], m["category_label"]) for m in response.json()],
            [("jacobi", "Sistemas lineales"), ("gauss-seidel", "Sistemas lineales")],
        )

    def test_catalog_does_not_expose_internals(self):
        for method in self.client.get("/api/methods/").json():
            self.assertEqual(set(method), {"slug", "name", "category", "category_label"})


class ExamplesByMethodTests(APITestCase):
    def test_filters_by_method(self):
        for slug in ("jacobi", "gauss-seidel"):
            with self.subTest(method=slug):
                response = self.client.get(f"/api/examples/?method={slug}")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.json()), 6)

    def test_unknown_method_returns_404(self):
        response = self.client.get("/api/examples/?method=newton")
        self.assertEqual(response.status_code, 404)

    def test_without_method_returns_each_example_once(self):
        ids = [e["id"] for e in self.client.get("/api/examples/").json()]
        self.assertEqual(ids, [e["id"] for e in all_examples()])
        self.assertEqual(len(ids), len(set(ids)))

    def test_solve_response_includes_generic_fields(self):
        example = EXAMPLES["jacobi"][1]
        payload = {k: example[k] for k in ("A", "b", "x0", "tolerance", "max_iterations")}
        data = self.client.post("/api/solve/jacobi/", payload, format="json").json()
        self.assertEqual(data["category"], "linear_system")
        self.assertEqual(data["variables"], ["x1", "x2", "x3"])
