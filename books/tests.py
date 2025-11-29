from django.test import TestCase
from rest_framework.test import APIClient

class BookTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_list_books(self):
        url = "/api/books/books/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertIsInstance(response.data["results"], list)

        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_get_book_detail(self):
        # obtenemos cualquier ID real
        list_resp = self.client.get("/api/books/books/")
        self.assertEqual(list_resp.status_code, 200)

        first = list_resp.data["results"][0]
        book_id = first["id"]

        url = f"/api/books/books/{book_id}/"
        detail = self.client.get(url)

        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["id"], book_id)

    def test_search_books(self):
        url = "/api/books/books/?search=a"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)

        # Debe haber al menos 1 coincidencia
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_ordering_price_asc(self):
        url = "/api/books/books/?ordering=price&page_size=9999"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        books = response.data["results"]
        prices = [float(b["price"]) for b in books if b["price"]]

        if len(prices) > 1:
            self.assertEqual(prices, sorted(prices))