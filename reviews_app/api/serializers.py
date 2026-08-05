from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
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
        if value.type != get_user_model().Types.BUSINESS:
            raise serializers.ValidationError("Reviews target business users only.")
        if value == self.context["request"].user:
            raise serializers.ValidationError("You cannot review yourself.")
        return value

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate(self, attrs):
        request = self.context["request"]
        business_user = attrs.get("business_user", getattr(self.instance, "business_user", None))
        duplicate = Review.objects.filter(
            reviewer=request.user,
            business_user=business_user,
        )
        if self.instance:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise serializers.ValidationError("You already reviewed this user.")
        return attrs

    def create(self, validated_data):
        return Review.objects.create(
            reviewer=self.context["request"].user,
            **validated_data,
        )
