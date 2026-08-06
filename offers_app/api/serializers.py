from django.db import transaction
from rest_framework import serializers
from rest_framework.reverse import reverse

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """Validate and render a single offer package.

    The serializer is used both for nested offer writes and for the read-only
    offer detail endpoint. Package type, features, revisions, delivery time and
    price form the documented offer tier contract.
    """

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
    """Represent offers with nested package details and aggregate fields.

    It handles the full offer detail schema for create, retrieve and nested
    updates. Minimum price and delivery time are read from queryset annotations
    when available to keep list responses efficient.
    """

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
        """Validate package types before nested offer detail persistence.

        Full writes must include exactly the three documented package types.
        PATCH requests may send a subset, but each item still needs one unique
        offer_type so the existing detail row can be resolved safely.
        """
        types = []
        for item in value:
            offer_type = item.get("offer_type")
            if not offer_type:
                raise serializers.ValidationError(
                    "Each detail must include offer_type."
                )
            types.append(offer_type)

        if len(types) != len(set(types)):
            raise serializers.ValidationError("Each offer_type may only be used once.")

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
        """Create an offer and its package rows in one transaction.

        DRF's default ModelSerializer create cannot persist writable nested
        details, so the serializer creates the parent offer for the request user
        and then stores the three validated package tiers.
        """
        details = validated_data.pop("details")
        offer = Offer.objects.create(
            user=self.context["request"].user, **validated_data
        )
        self.save_details(offer, details)
        return offer

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update an offer and supplied package details atomically.

        DRF's default ModelSerializer update cannot update nested OfferDetail
        rows. Supplied packages are resolved by offer_type and updated without
        replacing their database identities.
        """
        details = validated_data.pop("details", None)
        offer = super().update(instance, validated_data)
        if details is not None:
            self.update_details(offer, details)
        return offer

    def save_details(self, offer, details):
        """Persist validated package details for a newly created offer."""
        OfferDetail.objects.bulk_create(
            [OfferDetail(offer=offer, **detail) for detail in details]
        )

    def update_details(self, offer, details):
        """Apply partial package changes to existing rows by offer_type."""
        existing_details = {detail.offer_type: detail for detail in offer.details.all()}

        for detail_data in details:
            offer_type = detail_data["offer_type"]
            detail = existing_details[offer_type]
            for field, value in detail_data.items():
                setattr(detail, field, value)
            detail.save()


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Represent offer packages as links in the paginated offer list.

    List responses expose lightweight detail references instead of embedding
    every package, matching the documented list schema.
    """

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        request = self.context.get("request")
        return reverse("offerdetail-detail", args=[obj.pk], request=request)


class OfferUserDetailsSerializer(serializers.Serializer):
    """Embed creator identity fields in offer list responses."""

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()


class OfferListSerializer(OfferSerializer):
    """Format offer list entries with linked details and creator data.

    The serializer reuses offer aggregate fields while replacing nested package
    payloads with offer detail links for the paginated public list endpoint.
    """

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
    """Limit offer write responses to the documented mutable offer fields."""

    class Meta(OfferSerializer.Meta):
        fields = [
            "id",
            "title",
            "image",
            "description",
            "details",
        ]
        read_only_fields = ["id"]
