from django.db import transaction
from rest_framework import serializers
from rest_framework.reverse import reverse

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
        read_only_fields = ["id"]

    def validate_features(self, value):
        """Require at least one non-empty feature per offer package."""
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError("Provide at least one feature.")
        if not all(isinstance(item, str) and item.strip() for item in value):
            raise serializers.ValidationError("Features must be non-empty strings.")
        return value

    def validate_revisions(self, value):
        """Use -1 as the documented value for unlimited revisions."""
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
        """Require exactly the basic, standard and premium packages."""
        types = [item["offer_type"] for item in value]
        if self.partial and self.instance:
            return value
        expected = list(OfferDetail.Types.values)
        if sorted(types) != sorted(expected):
            raise serializers.ValidationError("Provide basic, standard and premium.")
        return value

    def get_min_price(self, obj):
        """Return the annotated minimum price or calculate it from details."""
        value = getattr(obj, "min_price", None)
        if value is not None:
            return value
        prices = [detail.price for detail in obj.details.all()]
        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        """Return the annotated fastest delivery time or calculate it."""
        value = getattr(obj, "min_delivery_time", None)
        if value is not None:
            return value
        times = [detail.delivery_time_in_days for detail in obj.details.all()]
        return min(times) if times else None

    @transaction.atomic
    def create(self, validated_data):
        """Create an offer and its three nested package details."""
        details = validated_data.pop("details")
        offer = Offer.objects.create(
            user=self.context["request"].user, **validated_data
        )
        self.save_details(offer, details)
        return offer

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update nested details by offer_type without replacing their rows."""
        details = validated_data.pop("details", None)
        offer = super().update(instance, validated_data)
        if details is not None:
            self.update_details(offer, details)
        return offer

    def save_details(self, offer, details):
        OfferDetail.objects.bulk_create(
            [OfferDetail(offer=offer, **detail) for detail in details]
        )

    def update_details(self, offer, details):
        existing_details = {
            detail.offer_type: detail for detail in offer.details.all()
        }

        for detail_data in details:
            offer_type = detail_data["offer_type"]
            detail = existing_details[offer_type]
            for field, value in detail_data.items():
                setattr(detail, field, value)
            detail.save()


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        request = self.context.get("request")
        return reverse("offerdetail-detail", args=[obj.pk], request=request)


class OfferUserDetailsSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()


class OfferListSerializer(OfferSerializer):
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    user_details = OfferUserDetailsSerializer(source="user", read_only=True)

    class Meta(OfferSerializer.Meta):
        fields = [
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
        ]


class OfferWriteSerializer(OfferSerializer):
    class Meta(OfferSerializer.Meta):
        fields = [
            "id",
            "title",
            "image",
            "description",
            "details",
        ]
        read_only_fields = ["id"]
