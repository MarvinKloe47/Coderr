from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from offers_app.models import Offer, OfferDetail
from orders_app.models import Order


class OrderApiTests(APITestCase):
    def setUp(self):
        users = get_user_model().objects
        self.business = users.create_user("kevin", password="pw", type="business")
        self.customer = users.create_user("andrey", password="pw", type="customer")
        self.other = users.create_user("maria", password="pw", type="customer")
        self.offer = Offer.objects.create(
            user=self.business,
            title="Logo",
            description="Logo design",
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title="Basic Logo",
            revisions=1,
            delivery_time_in_days=3,
            price="99.00",
            features=["Logo"],
            offer_type="basic",
        )

    def create_order(self):
        return Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            offer_detail=self.detail,
            title=self.detail.title,
            revisions=self.detail.revisions,
            delivery_time_in_days=self.detail.delivery_time_in_days,
            price=self.detail.price,
            features=self.detail.features,
        )

    def test_customer_can_create_order_from_offer_detail(self):
        self.client.force_authenticate(self.customer)
        response = self.client.post(
            reverse("order-list"),
            {"offer_detail_id": self.detail.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["business_user"], self.business.pk)
        self.assertEqual(response.data["title"], "Basic Logo")

    def test_business_cannot_create_order(self):
        self.client.force_authenticate(self.business)
        response = self.client.post(
            reverse("order-list"),
            {"offer_detail_id": self.detail.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_snapshot_stays_after_offer_detail_changes(self):
        order = self.create_order()
        self.detail.title = "Changed"
        self.detail.features = ["Changed"]
        self.detail.save()

        order.refresh_from_db()

        self.assertEqual(order.title, "Basic Logo")
        self.assertEqual(order.features, ["Logo"])

    def test_participants_can_list_their_orders(self):
        self.create_order()
        self.client.force_authenticate(self.business)

        response = self.client.get(reverse("order-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_third_party_cannot_retrieve_order(self):
        order = self.create_order()
        self.client.force_authenticate(self.other)

        response = self.client.get(reverse("order-detail", args=[order.pk]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_business_can_update_status(self):
        order = self.create_order()
        self.client.force_authenticate(self.business)

        response = self.client.patch(
            reverse("order-detail", args=[order.pk]),
            {"status": "completed"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")

    def test_customer_cannot_update_status(self):
        order = self.create_order()
        self.client.force_authenticate(self.customer)

        response = self.client.patch(
            reverse("order-detail", args=[order.pk]),
            {"status": "completed"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_order_count_endpoints_return_counts(self):
        self.create_order()
        Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            offer_detail=self.detail,
            title="Done",
            revisions=1,
            delivery_time_in_days=3,
            price="99.00",
            features=["Logo"],
            status=Order.Status.COMPLETED,
        )
        self.client.force_authenticate(self.customer)

        open_response = self.client.get(reverse("order-count", args=[self.business.pk]))
        done_response = self.client.get(
            reverse("completed-order-count",
            args=[self.business.pk])
        )

        self.assertEqual(open_response.data["order_count"], 1)
        self.assertEqual(done_response.data["order_count"], 1)
