from rest_framework import serializers

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "offer_detail_id",
            "created_at",
            "status",
            "title",
            "delivery_time_in_days",
            "revisions",
            "price",
            "features",
        ]
        read_only_fields = [
            "id",
            "customer_user",
            "business_user",
            "created_at",
            "title",
            "delivery_time_in_days",
            "revisions",
            "price",
            "features",
        ]

    def validate_status(self, value):
        if value not in Order.Status.values:
            raise serializers.ValidationError("Invalid order status.")
        return value

    def validate_offer_detail_id(self, value):
        if not OfferDetail.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Offer detail not found.")
        return value

    def create(self, validated_data):
        detail_id = validated_data.pop("offer_detail_id")
        detail = OfferDetail.objects.select_related("offer", "offer__user").get(pk=detail_id)
        return Order.objects.create(
            customer_user=self.context["request"].user,
            business_user=detail.offer.user,
            offer_detail=detail,
            title=detail.title,
            revisions=detail.revisions,
            delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price,
            features=detail.features,
        )
