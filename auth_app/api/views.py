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
    """Expose public account registration through DRF's create flow.

    Validation and token response shaping live in RegistrationSerializer, so the
    view only opens the endpoint to anonymous users.
    """

    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer


class LoginView(generics.GenericAPIView):
    """Expose token login without creating or modifying model instances.

    The serializer performs authentication and formats the documented payload;
    the view keeps the endpoint publicly accessible.
    """

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
    """Provide authenticated profile detail and owner-only updates.

    Retrieve and PATCH actions use DRF mixins with object permissions, while
    field-level restrictions such as customer-only editable fields remain in the
    profile serializer.
    """

    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]
    serializer_class = ProfileSerializer
    queryset = get_user_model().objects.all().order_by("username")
    lookup_field = "id"


class BusinessProfileListView(generics.ListAPIView):
    """List business profiles without pagination.

    The endpoint returns only users with the business role and uses the reduced
    public business profile schema expected by the frontend.
    """

    serializer_class = BusinessProfileSerializer
    pagination_class = None

    def get_queryset(self):
        return get_user_model().objects.filter(type="business").order_by("username")


class CustomerProfileListView(generics.ListAPIView):
    """List customer profiles without pagination.

    The endpoint returns only users with the customer role and uses the compact
    public customer schema with uploaded_at derived from created_at.
    """

    serializer_class = CustomerProfileSerializer
    pagination_class = None

    def get_queryset(self):
        return get_user_model().objects.filter(type="customer").order_by("username")
