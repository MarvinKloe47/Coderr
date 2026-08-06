from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token


def build_auth_payload(user):
    """Return the documented token payload for registration and login."""
    token, _ = Token.objects.get_or_create(user=user)
    return {
        "token": token.key,
        "username": user.username,
        "email": user.email,
        "user_id": user.pk,
    }


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "email",
            "password",
            "repeated_password",
            "type",
        ]

    def validate_type(self, value):
        """Accept only the two roles supported by the frontend."""
        choices = get_user_model().Types.values
        if value not in choices:
            raise serializers.ValidationError("Choose customer or business.")
        return value

    def validate(self, attrs):
        """Ensure the repeated password matches before creating the user."""
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": ["Passwords do not match."]}
            )
        return attrs

    def create(self, validated_data):
        """Create the user through the manager so the password is hashed."""
        validated_data.pop("repeated_password")
        password = validated_data.pop("password")
        return get_user_model().objects.create_user(
            password=password,
            **validated_data,
        )

    def to_representation(self, instance):
        return build_auth_payload(instance)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate credentials without revealing which field was wrong."""
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["username"],
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError("Invalid username or password.")
        attrs["user"] = user
        return attrs

    def to_representation(self, instance):
        return build_auth_payload(instance["user"])


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = get_user_model()
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "email",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "created_at",
        ]
        read_only_fields = ["user", "username", "type", "created_at"]

    def update(self, instance, validated_data):
        """Ignore business-only fields when a customer profile is updated."""
        if instance.type == instance.Types.CUSTOMER:
            for field in ["location", "tel", "description", "working_hours"]:
                validated_data.pop(field, None)
        return super().update(instance, validated_data)


class BusinessProfileSerializer(ProfileSerializer):
    class Meta(ProfileSerializer.Meta):
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]


class CustomerProfileSerializer(ProfileSerializer):
    uploaded_at = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta(ProfileSerializer.Meta):
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "uploaded_at",
            "type",
        ]
