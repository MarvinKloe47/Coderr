from django.contrib.auth import get_user_model
from rest_framework import generics, mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .permissions import IsProfileOwnerOrReadOnly
from .serializers import (
    BusinessProfileSerializer,
    CustomerProfileSerializer,
    LoginSerializer,
    ProfileSerializer,
    RegistrationSerializer,
)


class RegistrationView(generics.CreateAPIView):
    """Create a user account and return the documented token payload."""

    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer


class LoginView(generics.GenericAPIView):
    """Authenticate credentials and return a DRF token payload."""

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Provide profile detail and owner-only partial updates."""

    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]
    serializer_class = ProfileSerializer
    queryset = get_user_model().objects.all().order_by("username")
    lookup_field = "id"

    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class BusinessProfileListView(generics.ListAPIView):
    """List profiles for users with the business role."""

    serializer_class = BusinessProfileSerializer
    pagination_class = None

    def get_queryset(self):
        return get_user_model().objects.filter(type="business").order_by("username")


class CustomerProfileListView(generics.ListAPIView):
    """List profiles for users with the customer role."""

    serializer_class = CustomerProfileSerializer
    pagination_class = None

    def get_queryset(self):
        return get_user_model().objects.filter(type="customer").order_by("username")
