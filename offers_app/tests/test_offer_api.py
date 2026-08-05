from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail


def offer_payload(title="Logo Design"):
    return {
        "title": title,
        "description": "A polished visual identity package.",
        "details": [
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
        ],
    }


class OfferApiTests(APITestCase):
    def setUp(self):
        users = get_user_model().objects
        self.business = users.create_user("kevin", password="pw", type="business")
        self.other = users.create_user("sara", password="pw", type="business")
        self.customer = users.create_user("andrey", password="pw", type="customer")

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
        self.assertEqual(response.data["user"], self.business.pk)
        self.assertEqual(len(response.data["details"]), 3)
        self.assertEqual(response.data["min_delivery_time"], 3)

    def test_customer_cannot_create_offer(self):
        self.client.force_authenticate(self.customer)
        response = self.client.post(
            reverse("offer-list"), offer_payload(), format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_filters_by_creator_and_search(self):
        self.create_offer(title="Logo Design")
        self.create_offer(owner=self.other, title="Backend API")
        self.client.force_authenticate(self.customer)

        response = self.client.get(
            reverse("offer-list"),
            {"creator_id": self.business.pk, "search": "Logo"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Logo Design")

    def test_offer_detail_endpoint_returns_detail(self):
        offer = self.create_offer()
        detail = offer.details.get(offer_type="premium")
        self.client.force_authenticate(self.customer)

        response = self.client.get(reverse("offerdetail-detail", args=[detail.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["offer_type"], "premium")

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

    def test_owner_can_delete_offer(self):
        offer = self.create_offer()
        self.client.force_authenticate(self.business)

        response = self.client.delete(reverse("offer-detail", args=[offer.pk]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(pk=offer.pk).exists())
