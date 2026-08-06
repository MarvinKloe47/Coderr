from django.db.models import Min
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from offers_app.models import Offer, OfferDetail

from .filters import OfferFilter
from .permissions import IsBusinessOrReadOnly, IsOfferOwnerOrReadOnly
from .serializers import (
    OfferDetailSerializer,
    OfferListSerializer,
    OfferSerializer,
    OfferWriteSerializer,
)


class OfferViewSet(viewsets.ModelViewSet):
    """Manage offers and expose documented filtering, search and ordering."""

    serializer_class = OfferSerializer
    filterset_class = OfferFilter
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["-updated_at", "id"]

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [AllowAny]
        else:
            permission_classes = [
                IsAuthenticated,
                IsBusinessOrReadOnly,
                IsOfferOwnerOrReadOnly,
            ]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "list":
            return OfferListSerializer
        if self.action in {"create", "update", "partial_update"}:
            return OfferWriteSerializer
        return OfferSerializer

    def get_queryset(self):
        """Load offers with owner, details and aggregate values efficiently."""
        return (
            Offer.objects.select_related("user")
            .prefetch_related("details")
            .annotate(
                min_price=Min("details__price"),
                min_delivery_time=Min("details__delivery_time_in_days"),
            )
            .order_by("-updated_at", "id")
        )


class OfferDetailViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Expose a read-only endpoint for a single offer package."""

    permission_classes = [IsAuthenticated]
    serializer_class = OfferDetailSerializer
    queryset = OfferDetail.objects.select_related("offer", "offer__user")
