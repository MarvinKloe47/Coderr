from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RegistrationApiTests(APITestCase):
    def test_register_customer_returns_token_payload(self):
        response = self.client.post(
            reverse("registration"),
            {
                "username": "andrey",
                "email": "andrey@example.com",
                "password": "asdasd",
                "repeated_password": "asdasd",
                "type": "customer",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "andrey")
        self.assertIn("token", response.data)
        self.assertTrue(
            get_user_model().objects.get(username="andrey").check_password("asdasd")
        )

    def test_register_rejects_password_mismatch(self):
        response = self.client.post(
            reverse("registration"),
            {
                "username": "andrey",
                "email": "andrey@example.com",
                "password": "asdasd",
                "repeated_password": "different",
                "type": "customer",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("repeated_password", response.data)

    def test_register_requires_role(self):
        response = self.client.post(
            reverse("registration"),
            {
                "username": "andrey",
                "email": "andrey@example.com",
                "password": "asdasd",
                "repeated_password": "asdasd",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)


class LoginApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="kevin",
            email="kevin@example.com",
            password="asdasd24",
            type="business",
        )

    def test_login_returns_token_payload(self):
        response = self.client.post(
            reverse("login"),
            {"username": "kevin", "password": "asdasd24"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user_id"], self.user.pk)
        self.assertEqual(response.data["username"], "kevin")
        self.assertIn("token", response.data)

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            reverse("login"),
            {"username": "kevin", "password": "wrong"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_rejects_unknown_user(self):
        response = self.client.post(
            reverse("login"),
            {"username": "missing", "password": "wrong"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
