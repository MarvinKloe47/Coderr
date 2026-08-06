from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer
from reviews_app.models import Review


def create_base_info_data():
    users = get_user_model().objects
    business = users.create_user(
        "test_business", password="test-password", type="business"
    )
    customer = users.create_user(
        "test_customer", password="test-password", type="customer"
    )
    Offer.objects.create(user=business, title="Logo", description="Logo design")
    Review.objects.create(reviewer=customer, business_user=business, rating=5)


class BaseInfoApiTests(APITestCase):
    def test_base_info_returns_frontend_counts(self):
        create_base_info_data()

        response = self.client.get(reverse("base-info"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["offer_count"], 1)
        self.assertEqual(response.data["review_count"], 1)
        self.assertEqual(response.data["business_profile_count"], 1)
        self.assertEqual(response.data["average_rating"], 5.0)
