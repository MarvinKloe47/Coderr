from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class AuthResponseMixin:
    def auth_payload(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        return {
            "token": token.key,
            "user_id": user.pk,
            "username": user.username,
        }


class RegistrationSerializer(AuthResponseMixin, serializers.ModelSerializer):
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
        choices = get_user_model().Types.values
        if value not in choices:
            raise serializers.ValidationError("Choose customer or business.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": ["Passwords do not match."]}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("repeated_password")
        password = validated_data.pop("password")
        return get_user_model().objects.create_user(
            password=password,
            **validated_data,
        )

    def to_representation(self, instance):
        return self.auth_payload(instance)


class LoginSerializer(AuthResponseMixin, serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
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
        return self.auth_payload(instance["user"])
