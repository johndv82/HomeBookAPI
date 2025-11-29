from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

class UsersAuthTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/auth/users/"
        self.login_url = "/auth/jwt/create/"
        self.refresh_url = "/auth/jwt/refresh/"
        self.verify_url = "/auth/jwt/verify/"
        self.me_url = "/auth/users/me/"

        # Usuario de pruebas
        self.user_data = {
            "email": "test@test.com",
            "username": "test",
            "password": "123456aA!",
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email="test@test.com").exists())

    def test_user_login(self):
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.login_url, {
            "email": "test@test.com",
            "password": "123456aA!"
        }, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_token(self):
        User.objects.create_user(**self.user_data)
        login = self.client.post(self.login_url, {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }, format="json")

        response = self.client.post(self.refresh_url, {
            "refresh": login.data["refresh"]
        }, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    # def test_verify_token(self):
    #     User.objects.create_user(**self.user_data)
    #     login = self.client.post(self.login_url, {
    #         "email": self.user_data["email"],
    #         "password": self.user_data["password"]
    #     }, format="json")

    #     response = self.client.post(self.verify_url, {
    #         "token": login.data["access"]
    #     }, format="json")

    #     self.assertEqual(response.status_code, 200)

    def test_get_user_profile(self):
        user = User.objects.create_user(**self.user_data)
        login = self.client.post(self.login_url, {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }, format="json")

        token = login.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], user.email)
