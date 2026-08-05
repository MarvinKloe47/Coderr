from django.db import transaction
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "offer",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
        read_only_fields = ["id", "offer"]

    def validate_features(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError("Provide at least one feature.")
        if not all(isinstance(item, str) and item.strip() for item in value):
            raise serializers.ValidationError("Features must be non-empty strings.")
        return value

    def validate_revisions(self, value):
        if value < -1:
            raise serializers.ValidationError("Use -1 for unlimited revisions.")
        return value


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "description",
            "image",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate_details(self, value):
        types = [item["offer_type"] for item in value]
        expected = list(OfferDetail.Types.values)
        if sorted(types) != sorted(expected):
            raise serializers.ValidationError("Provide basic, standard and premium.")
        return value

    def get_min_price(self, obj):
        value = getattr(obj, "min_price", None)
        if value is not None:
            return value
        prices = [detail.price for detail in obj.details.all()]
        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        value = getattr(obj, "min_delivery_time", None)
        if value is not None:
            return value
        times = [detail.delivery_time_in_days for detail in obj.details.all()]
        return min(times) if times else None

    @transaction.atomic
    def create(self, validated_data):
        details = validated_data.pop("details")
        offer = Offer.objects.create(user=self.context["request"].user, **validated_data)
        self.save_details(offer, details)
        return offer

    @transaction.atomic
    def update(self, instance, validated_data):
        details = validated_data.pop("details", None)
        offer = super().update(instance, validated_data)
        if details is not None:
            offer.details.all().delete()
            self.save_details(offer, details)
        return offer

    def save_details(self, offer, details):
        OfferDetail.objects.bulk_create(
            [OfferDetail(offer=offer, **detail) for detail in details]
        )
