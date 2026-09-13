from rest_framework.test import APITestCase


class SolveEndpointsTests(APITestCase):
    def _payload(self, **overrides):
        payload = {
            "A": [
                [10, -1, 2],
                [-1, 11, -1],
                [2, -1, 10],
            ],
            "b": [6, 22, -10],
            "tolerance": 0.000001,
            "max_iterations": 100,
        }
        payload.update(overrides)
        return payload

    def test_jacobi_endpoint_returns_iterations_and_solution(self):
        response = self.client.post("/api/solve/jacobi/", self._payload(), format="json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["converged"])
        self.assertTrue(data["is_diagonally_dominant"])
        self.assertGreaterEqual(len(data["iterations"]), 6)
        self.assertAlmostEqual(data["solution"][0], 1.0, places=3)

    def test_gauss_seidel_endpoint_returns_iterations_and_solution(self):
        response = self.client.post(
            "/api/solve/gauss-seidel/", self._payload(), format="json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["converged"])
        self.assertAlmostEqual(data["solution"][1], 2.0, places=3)

    def test_non_square_matrix_returns_400(self):
        payload = self._payload(A=[[1, 2, 3], [4, 5, 6]], b=[1, 2])
        response = self.client.post("/api/solve/jacobi/", payload, format="json")
        self.assertEqual(response.status_code, 400)

    def test_less_than_three_variables_returns_400(self):
        payload = self._payload(A=[[4, 1], [1, 3]], b=[1, 2])
        response = self.client.post("/api/solve/jacobi/", payload, format="json")
        self.assertEqual(response.status_code, 400)

    def test_zero_in_diagonal_returns_400(self):
        payload = self._payload(A=[[0, 1, 1], [1, 5, 1], [1, 1, 5]], b=[1, 2, 3])
        response = self.client.post("/api/solve/jacobi/", payload, format="json")
        self.assertEqual(response.status_code, 400)

    def test_non_dominant_matrix_returns_warning_not_error(self):
        payload = self._payload(
            A=[[1, 2, 3], [4, 5, 6], [7, 8, 10]], b=[6, 15, 25], max_iterations=20
        )
        response = self.client.post("/api/solve/jacobi/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["is_diagonally_dominant"])
        self.assertTrue(any("dominante" in w for w in data["warnings"]))


class AutoReorderEndpointTests(APITestCase):
    REORDERABLE = {
        "A": [[1, 5, 1], [10, 2, 1], [2, 3, 10]],
        "b": [-8, 9, 22],
        "tolerance": 0.000001,
        "max_iterations": 100,
    }
    UNFIXABLE = {
        "A": [[1, 2, 3], [4, 5, 6], [7, 8, 10]],
        "b": [6, 15, 25],
        "tolerance": 0.000001,
        "max_iterations": 100,
    }

    def test_reorders_by_default_and_converges(self):
        response = self.client.post("/api/solve/jacobi/", self.REORDERABLE, format="json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["reordered"])
        self.assertEqual(data["row_order"], [1, 0, 2])
        self.assertTrue(data["converged"])
        self.assertTrue(data["is_diagonally_dominant"])
        self.assertEqual(data["warnings"], [])

    def test_response_returns_the_reordered_system(self):
        response = self.client.post("/api/solve/jacobi/", self.REORDERABLE, format="json")
        data = response.json()
        self.assertEqual(data["A"], [[10, 2, 1], [1, 5, 1], [2, 3, 10]])
        self.assertEqual(data["b"], [9, -8, 22])

    def test_reordered_solution_satisfies_the_original_system(self):
        response = self.client.post(
            "/api/solve/gauss-seidel/", self.REORDERABLE, format="json"
        )
        solution = response.json()["solution"]
        for row, expected in zip(self.REORDERABLE["A"], self.REORDERABLE["b"]):
            left = sum(row[j] * solution[j] for j in range(3))
            self.assertAlmostEqual(left, expected, places=4)

    def test_disabling_auto_reorder_keeps_previous_behaviour(self):
        payload = {**self.REORDERABLE, "auto_reorder": False}
        response = self.client.post("/api/solve/jacobi/", payload, format="json")
        data = response.json()
        self.assertFalse(data["reordered"])
        self.assertIsNone(data["row_order"])
        self.assertFalse(data["is_diagonally_dominant"])
        self.assertTrue(any("dominante" in w for w in data["warnings"]))
        self.assertEqual(data["A"], self.REORDERABLE["A"])

    def test_system_without_valid_ordering_keeps_the_warning(self):
        response = self.client.post("/api/solve/jacobi/", self.UNFIXABLE, format="json")
        data = response.json()
        self.assertFalse(data["reordered"])
        self.assertIsNone(data["row_order"])
        self.assertFalse(data["is_diagonally_dominant"])
        self.assertTrue(any("dominante" in w for w in data["warnings"]))

    def test_already_dominant_system_is_not_reordered(self):
        payload = {
            "A": [[10, -1, 2], [-1, 11, -1], [2, -1, 10]],
            "b": [6, 22, -10],
            "tolerance": 0.000001,
            "max_iterations": 100,
        }
        response = self.client.post("/api/solve/jacobi/", payload, format="json")
        data = response.json()
        self.assertFalse(data["reordered"])
        self.assertEqual(data["A"], payload["A"])


class ExamplesEndpointTests(APITestCase):
    def test_examples_endpoint_returns_at_least_six_examples(self):
        response = self.client.get("/api/examples/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 6)
        for example in data:
            self.assertGreaterEqual(example["n"], 3)
            self.assertEqual(len(example["A"]), example["n"])
            self.assertEqual(len(example["b"]), example["n"])
