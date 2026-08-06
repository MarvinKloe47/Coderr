from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Validate customer reviews for business profiles.

    The serializer assigns the authenticated reviewer on create, limits review
    targets to business users, and enforces one review per customer/business
    pair.
    """

    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "description",
            "rating",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "reviewer", "created_at", "updated_at"]

    def validate_business_user(self, value):
        """Ensure reviews target another user with the business role."""
        if value.type != get_user_model().Types.BUSINESS:
            raise serializers.ValidationError("Reviews target business users only.")
        if value == self.context["request"].user:
            raise serializers.ValidationError("You cannot review yourself.")
        return value

    def validate_rating(self, value):
        """Keep ratings within the documented one-to-five range."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate(self, attrs):
        """Enforce the documented PATCH field set and duplicate-review rule.

        DRF would accept any writable field on PATCH. The review API allows only
        rating and description updates, and creation/update must still preserve
        one review per customer/business pair.
        """
        request = self.context.get("request")
        if self.instance and request and request.method == "PATCH":
            invalid_fields = set(request.data) - {"description", "rating"}
            if invalid_fields:
                raise serializers.ValidationError(
                    "Only rating and description can be updated."
                )
        business_user = attrs.get(
            "business_user", getattr(self.instance, "business_user", None)
        )
        if self.duplicate_review_exists(business_user):
            raise serializers.ValidationError("You already reviewed this user.")
        return attrs

    def duplicate_review_exists(self, business_user):
        """Check duplicates while allowing the current review to be updated."""
        duplicate = Review.objects.filter(
            reviewer=self.context["request"].user,
            business_user=business_user,
        )
        if self.instance:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        return duplicate.exists()

    def create(self, validated_data):
        """Store the authenticated user as reviewer during DRF creation."""
        return Review.objects.create(
            reviewer=self.context["request"].user,
            **validated_data,
        )
