from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


def registration_payload(**overrides):
    payload = {
        "username": "test_customer",
        "email": "customer@example.com",
        "password": "test-password",
        "repeated_password": "test-password",
        "type": "customer",
    }
    payload.update(overrides)
    return payload


class RegistrationApiTests(APITestCase):
    def test_register_customer_returns_token_payload(self):
        response = self.client.post(
            reverse("registration"),
            registration_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "test_customer")
        self.assertIn("token", response.data)
        user = get_user_model().objects.get(username="test_customer")
        self.assertTrue(user.check_password("test-password"))

    def test_register_rejects_password_mismatch(self):
        response = self.client.post(
            reverse("registration"),
            registration_payload(repeated_password="different"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("repeated_password", response.data)

    def test_register_requires_role(self):
        payload = registration_payload()
        payload.pop("type")

        response = self.client.post(
            reverse("registration"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)


class LoginApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test_business",
            email="business@example.com",
            password="test-password",
            type="business",
        )

    def test_login_returns_token_payload(self):
        response = self.client.post(
            reverse("login"),
            {"username": "test_business", "password": "test-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user_id"], self.user.pk)
        self.assertEqual(response.data["username"], "test_business")
        self.assertIn("token", response.data)

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            reverse("login"),
            {"username": "test_business", "password": "wrong-test-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_rejects_unknown_user(self):
        response = self.client.post(
            reverse("login"),
            {"username": "missing", "password": "wrong-test-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
