from django.contrib.auth import get_user_model
from django.test import TestCase


class UserManagerTests(TestCase):
    def test_create_user_hashes_password_and_sets_role(self):
        user = get_user_model().objects.create_user(
            username="test_customer",
            email="USER@Example.COM",
            password="test-password",
            type="customer",
        )

        self.assertEqual(user.email, "USER@example.com")
        self.assertEqual(user.type, "customer")
        self.assertTrue(user.check_password("test-password"))
        self.assertNotEqual(user.password, "test-password")

    def test_create_user_requires_username(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", password="test-password")

    def test_create_superuser_sets_business_role(self):
        user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="test-password",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.type, "business")

    def test_create_superuser_rejects_missing_flags(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(
                username="admin",
                password="test-password",
                is_staff=False,
            )


class UserModelTests(TestCase):
    def test_string_representation_is_username(self):
        user = get_user_model().objects.create_user(
            username="test_business",
            password="test-password",
            type="business",
        )

        self.assertEqual(str(user), "test_business")
