from django.contrib.auth import get_user_model
from rest_framework import generics, mixins, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .permissions import IsProfileOwnerOrReadOnly
from .serializers import LoginSerializer, ProfileSerializer, RegistrationSerializer


class RegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer


class LoginView(generics.GenericAPIView):
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
    permission_classes = [IsProfileOwnerOrReadOnly]
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
    serializer_class = ProfileSerializer
    pagination_class = None

    def get_queryset(self):
        return get_user_model().objects.filter(type="business").order_by("username")


class CustomerProfileListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    pagination_class = None

    def get_queryset(self):
        return get_user_model().objects.filter(type="customer").order_by("username")
