from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


def registration_payload():
    return {
        "username": "security_customer",
        "email": "security-customer@example.com",
        "password": "test-password",
        "repeated_password": "test-password",
        "type": "customer",
    }


def create_user(username, role):
    return get_user_model().objects.create_user(
        username=username,
        password="test-password",
        type=role,
    )


class SecurityRegressionTests(APITestCase):
    def test_registration_response_excludes_password_fields(self):
        response = self.client.post(
            reverse("registration"),
            registration_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)
        self.assertNotIn("repeated_password", response.data)

    def test_failed_login_response_excludes_token(self):
        create_user("security_business", "business")

        response = self.client.post(
            reverse("login"),
            {
                "username": "security_business",
                "password": "wrong-test-password",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)

    def test_profile_response_excludes_password_hash_and_admin_flags(self):
        user = create_user("profile_customer", "customer")
        self.client.force_authenticate(user)

        response = self.client.get(reverse("profile-detail", args=[user.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("password", response.data)
        self.assertNotIn("is_staff", response.data)
        self.assertNotIn("is_superuser", response.data)

    def test_profile_requires_authentication(self):
        user = create_user("private_customer", "customer")

        response = self.client.get(reverse("profile-detail", args=[user.pk]))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_test_settings_use_safe_security_defaults(self):
        self.assertFalse(settings.DEBUG)
        self.assertFalse(settings.SECRET_KEY.startswith("django-insecure-"))
