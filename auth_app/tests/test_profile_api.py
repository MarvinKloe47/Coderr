from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ProfileApiTests(APITestCase):
    def setUp(self):
        users = get_user_model().objects
        self.business = users.create_user(
            "test_business",
            email="business@example.com",
            password="test-password",
            type="business",
            first_name="TestBusiness",
            location="Berlin",
        )
        self.customer = users.create_user(
            "test_customer",
            email="customer@example.com",
            password="test-password",
            type="customer",
            first_name="TestCustomer",
        )

    def test_authenticated_user_can_get_profile_detail(self):
        self.client.force_authenticate(self.customer)
        response = self.client.get(reverse("profile-detail", args=[self.business.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.business.pk)
        self.assertEqual(response.data["type"], "business")

    def test_business_profile_list_returns_array(self):
        self.client.force_authenticate(self.customer)
        response = self.client.get(reverse("business-profiles"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(response.data[0]["username"], "test_business")

    def test_customer_profile_list_returns_customers_only(self):
        self.client.force_authenticate(self.business)
        response = self.client.get(reverse("customer-profiles"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["type"], "customer")

    def test_owner_can_patch_profile(self):
        self.client.force_authenticate(self.business)
        response = self.client.patch(
            reverse("profile-detail", args=[self.business.pk]),
            {"first_name": "K", "working_hours": "9-5"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "K")
        self.assertEqual(response.data["working_hours"], "9-5")

    def test_user_cannot_patch_other_profile(self):
        self.client.force_authenticate(self.customer)
        response = self.client.patch(
            reverse("profile-detail", args=[self.business.pk]),
            {"first_name": "Wrong"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_patch_ignores_business_only_fields(self):
        self.client.force_authenticate(self.customer)
        response = self.client.patch(
            reverse("profile-detail", args=[self.customer.pk]),
            {"location": "Berlin", "working_hours": "9-5"},
            format="json",
        )
        self.customer.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.customer.location, "")
        self.assertEqual(self.customer.working_hours, "")
