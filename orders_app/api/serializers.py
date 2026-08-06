from rest_framework import serializers
from rest_framework.exceptions import NotFound

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.IntegerField(write_only=True, required=False)
    offer_type = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "offer_detail_id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "created_at",
            "updated_at",
        ]

    def validate_status(self, value):
        """Accept only status values defined by the Order model."""
        if value not in Order.Status.values:
            raise serializers.ValidationError("Invalid order status.")
        return value

    def validate_offer_detail_id(self, value):
        """Reject orders for offer details that do not exist."""
        if not OfferDetail.objects.filter(pk=value).exists():
            raise NotFound("Offer detail not found.")
        return value

    def validate(self, attrs):
        """Allow status-only PATCH requests for documented order updates."""
        request = self.context.get("request")
        if self.instance and request and request.method == "PATCH":
            invalid_fields = set(request.data) - {"status"}
            if invalid_fields:
                raise serializers.ValidationError(
                    "Only the status field can be updated."
                )
        return attrs

    def get_offer_type(self, obj):
        if obj.offer_detail_id:
            return obj.offer_detail.offer_type
        return ""

    def create(self, validated_data):
        """Create an order with immutable values from the chosen offer detail."""
        detail_id = validated_data.pop("offer_detail_id")
        detail = OfferDetail.objects.select_related("offer", "offer__user").get(
            pk=detail_id
        )
        snapshot = self.snapshot_from_detail(detail)
        return Order.objects.create(
            customer_user=self.context["request"].user,
            business_user=detail.offer.user,
            offer_detail=detail,
            **snapshot,
        )

    def snapshot_from_detail(self, detail):
        """Copy offer values so later offer changes do not affect the order."""
        return {
            "title": detail.title,
            "revisions": detail.revisions,
            "delivery_time_in_days": detail.delivery_time_in_days,
            "price": detail.price,
            "features": detail.features,
        }
