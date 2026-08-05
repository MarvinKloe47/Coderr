from django.contrib.auth import get_user_model
from django.test import TestCase


class UserManagerTests(TestCase):
    def test_create_user_hashes_password_and_sets_role(self):
        user = get_user_model().objects.create_user(
            username="andrey",
            email="USER@Example.COM",
            password="asdasd",
            type="customer",
        )

        self.assertEqual(user.email, "USER@example.com")
        self.assertEqual(user.type, "customer")
        self.assertTrue(user.check_password("asdasd"))
        self.assertNotEqual(user.password, "asdasd")

    def test_create_user_requires_username(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", password="secret")

    def test_create_superuser_sets_business_role(self):
        user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="secret",
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.type, "business")

    def test_create_superuser_rejects_missing_flags(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(
                username="admin",
                password="secret",
                is_staff=False,
            )


class UserModelTests(TestCase):
    def test_string_representation_is_username(self):
        user = get_user_model().objects.create_user(
            username="kevin",
            password="asdasd24",
            type="business",
        )

        self.assertEqual(str(user), "kevin")
