from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from reviews_app.models import Review


class ReviewApiTests(APITestCase):
    def setUp(self):
        users = get_user_model().objects
        self.business = users.create_user("kevin", password="pw", type="business")
        self.customer = users.create_user("andrey", password="pw", type="customer")
        self.other = users.create_user("maria", password="pw", type="customer")

    def test_customer_can_create_review(self):
        self.client.force_authenticate(self.customer)
        response = self.client.post(
            reverse("review-list"),
            {
                "business_user": self.business.pk,
                "description": "Great work.",
                "rating": 5,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["reviewer"], self.customer.pk)

    def test_business_cannot_create_review(self):
        self.client.force_authenticate(self.business)
        response = self.client.post(
            reverse("review-list"),
            {
                "business_user": self.business.pk,
                "description": "Nope.",
                "rating": 5,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_review_same_business_twice(self):
        Review.objects.create(
            reviewer=self.customer,
            business_user=self.business,
            description="Great",
            rating=5,
        )
        self.client.force_authenticate(self.customer)

        response = self.client.post(
            reverse("review-list"),
            {
                "business_user": self.business.pk,
                "description": "Again",
                "rating": 4,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rating_must_be_between_one_and_five(self):
        self.client.force_authenticate(self.customer)
        response = self.client.post(
            reverse("review-list"),
            {
                "business_user": self.business.pk,
                "description": "Too much",
                "rating": 6,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filters_reviews_by_business_user(self):
        Review.objects.create(
            reviewer=self.customer,
            business_user=self.business,
            description="Great",
            rating=5,
        )
        self.client.force_authenticate(self.other)

        response = self.client.get(
            reverse("review-list"),
            {"business_user_id": self.business.pk, "ordering": "-rating"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_reviewer_can_update_review(self):
        review = Review.objects.create(
            reviewer=self.customer,
            business_user=self.business,
            description="Great",
            rating=5,
        )
        self.client.force_authenticate(self.customer)

        response = self.client.patch(
            reverse("review-detail", args=[review.pk]),
            {"description": "Still great", "rating": 4},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 4)

    def test_other_customer_cannot_delete_review(self):
        review = Review.objects.create(
            reviewer=self.customer,
            business_user=self.business,
            description="Great",
            rating=5,
        )
        self.client.force_authenticate(self.other)

        response = self.client.delete(reverse("review-detail", args=[review.pk]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
