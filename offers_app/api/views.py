from django.db.models import Min
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from offers_app.models import Offer, OfferDetail

from .filters import OfferFilter
from .permissions import IsBusinessOrReadOnly, IsOfferOwnerOrReadOnly
from .serializers import OfferDetailSerializer, OfferSerializer


class OfferViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsBusinessOrReadOnly, IsOfferOwnerOrReadOnly]
    serializer_class = OfferSerializer
    filterset_class = OfferFilter
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price", "min_delivery_time"]
    ordering = ["-updated_at", "id"]

    def get_queryset(self):
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
    serializer_class = OfferDetailSerializer
    queryset = OfferDetail.objects.select_related("offer", "offer__user")
