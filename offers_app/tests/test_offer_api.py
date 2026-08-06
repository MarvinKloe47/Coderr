from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail

OFFER_DETAILS = [
    {
        "title": "Basic Logo",
        "revisions": 1,
        "delivery_time_in_days": 3,
        "price": "99.00",
        "features": ["Logo"],
        "offer_type": "basic",
    },
    {
        "title": "Standard Logo",
        "revisions": 3,
        "delivery_time_in_days": 5,
        "price": "199.00",
        "features": ["Logo", "Colors"],
        "offer_type": "standard",
    },
    {
        "title": "Premium Logo",
        "revisions": -1,
        "delivery_time_in_days": 7,
        "price": "299.00",
        "features": ["Logo", "Colors", "Brand guide"],
        "offer_type": "premium",
    },
]


def offer_payload(title="Logo Design"):
    return {
        "title": title,
        "description": "A polished visual identity package.",
        "details": [detail.copy() for detail in OFFER_DETAILS],
    }


class OfferApiTests(APITestCase):
    def setUp(self):
        users = get_user_model().objects
        self.business = users.create_user(
            "test_business", password="test-password", type="business"
        )
        self.other = users.create_user(
            "other_business", password="test-password", type="business"
        )
        self.customer = users.create_user(
            "test_customer", password="test-password", type="customer"
        )

    def create_offer(self, owner=None, title="Logo Design"):
        owner = owner or self.business
        offer = Offer.objects.create(
            user=owner,
            title=title,
            description="A polished visual identity package.",
        )
        for detail in offer_payload()["details"]:
            OfferDetail.objects.create(offer=offer, **detail)
        return offer

    def test_business_can_create_offer_with_details(self):
        self.client.force_authenticate(self.business)
        response = self.client.post(
            reverse("offer-list"), offer_payload(), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            set(response.data.keys()),
            {"id", "title", "image", "description", "details"},
        )
        self.assertEqual(len(response.data["details"]), 3)
        self.assertEqual(
            set(response.data["details"][0].keys()),
            {
                "id",
                "title",
                "revisions",
                "delivery_time_in_days",
                "price",
                "features",
                "offer_type",
            },
        )
        self.assertNotIn("offer", response.data["details"][0])

    def test_customer_cannot_create_offer(self):
        self.client.force_authenticate(self.customer)
        response = self.client.post(
            reverse("offer-list"), offer_payload(), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rejects_incomplete_offer_details(self):
        payload = offer_payload()
        payload["details"] = payload["details"][:2]
        self.client.force_authenticate(self.business)

        response = self.client.post(reverse("offer-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejects_invalid_offer_detail_values(self):
        payload = offer_payload()
        payload["details"][0]["features"] = []
        payload["details"][1]["features"] = [" "]
        payload["details"][2]["revisions"] = -2
        self.client.force_authenticate(self.business)

        response = self.client.post(reverse("offer-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_filters_by_creator_and_search(self):
        self.create_offer(title="Logo Design")
        self.create_offer(owner=self.other, title="Backend API")

        response = self.client.get(
            reverse("offer-list"),
            {"creator_id": self.business.pk, "search": "Logo"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            set(response.data["results"][0].keys()),
            {
                "id",
                "user",
                "title",
                "image",
                "description",
                "created_at",
                "updated_at",
                "details",
                "min_price",
                "min_delivery_time",
                "user_details",
            },
        )
        self.assertEqual(
            set(response.data["results"][0]["details"][0].keys()),
            {"id", "url"},
        )
        self.assertEqual(
            set(response.data["results"][0]["user_details"].keys()),
            {"first_name", "last_name", "username"},
        )
        self.assertEqual(response.data["results"][0]["title"], "Logo Design")

    def test_public_offer_list_supports_filters_ordering_and_page_size(self):
        self.create_offer(title="Logo Design")
        self.create_offer(owner=self.other, title="Backend API")

        response = self.client.get(
            reverse("offer-list"),
            {
                "creator_id": self.business.pk,
                "min_price": "99.00",
                "max_delivery_time": 3,
                "search": "Logo",
                "ordering": "min_price",
                "page_size": 1,
                "page": 1,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_offer_detail_endpoint_returns_detail(self):
        offer = self.create_offer()
        detail = offer.details.get(offer_type="premium")
        self.client.force_authenticate(self.customer)

        response = self.client.get(reverse("offerdetail-detail", args=[detail.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {
                "id",
                "title",
                "revisions",
                "delivery_time_in_days",
                "price",
                "features",
                "offer_type",
            },
        )
        self.assertEqual(response.data["offer_type"], "premium")

    def test_offer_detail_endpoint_requires_authentication(self):
        offer = self.create_offer()
        detail = offer.details.get(offer_type="premium")

        response = self.client.get(reverse("offerdetail-detail", args=[detail.pk]))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_offer_retrieve_requires_authentication(self):
        offer = self.create_offer()

        response = self.client.get(reverse("offer-detail", args=[offer.pk]))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_owner_can_update_offer(self):
        offer = self.create_offer()
        payload = offer_payload(title="Updated")
        self.client.force_authenticate(self.other)

        response = self.client.patch(
            reverse("offer-detail", args=[offer.pk]),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_update_offer_details(self):
        offer = self.create_offer()
        payload = offer_payload(title="Updated")
        payload["details"][0]["price"] = "149.00"
        self.client.force_authenticate(self.business)

        url = reverse("offer-detail", args=[offer.pk])
        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated")
        self.assertEqual(offer.details.get(offer_type="basic").price, 149)

    def test_owner_can_patch_single_offer_detail_by_offer_type(self):
        offer = self.create_offer()
        detail = offer.details.get(offer_type="basic")
        self.client.force_authenticate(self.business)

        response = self.client.patch(
            reverse("offer-detail", args=[offer.pk]),
            {
                "details": [
                    {
                        "offer_type": "basic",
                        "price": "149.00",
                        "delivery_time_in_days": 2,
                    }
                ]
            },
            format="json",
        )

        detail.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.pk, offer.details.get(offer_type="basic").pk)
        self.assertEqual(detail.price, 149)
        self.assertEqual(detail.delivery_time_in_days, 2)
        self.assertEqual(offer.details.count(), 3)

    def test_patch_offer_detail_requires_offer_type(self):
        offer = self.create_offer()
        self.client.force_authenticate(self.business)

        response = self.client.patch(
            reverse("offer-detail", args=[offer.pk]),
            {"details": [{"price": "149.00"}]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_offer_detail_rejects_empty_offer_type(self):
        offer = self.create_offer()
        self.client.force_authenticate(self.business)

        response = self.client.patch(
            reverse("offer-detail", args=[offer.pk]),
            {"details": [{"offer_type": "", "price": "149.00"}]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_offer_detail_rejects_unknown_offer_type(self):
        offer = self.create_offer()
        self.client.force_authenticate(self.business)

        response = self.client.patch(
            reverse("offer-detail", args=[offer.pk]),
            {"details": [{"offer_type": "enterprise", "price": "149.00"}]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_offer_detail_rejects_duplicate_offer_type(self):
        offer = self.create_offer()
        self.client.force_authenticate(self.business)

        response = self.client.patch(
            reverse("offer-detail", args=[offer.pk]),
            {
                "details": [
                    {"offer_type": "basic", "price": "149.00"},
                    {"offer_type": "basic", "price": "159.00"},
                ]
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_can_delete_offer(self):
        offer = self.create_offer()
        self.client.force_authenticate(self.business)

        response = self.client.delete(reverse("offer-detail", args=[offer.pk]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(pk=offer.pk).exists())
