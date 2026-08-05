from rest_framework import viewsets

from reviews_app.models import Review

from .permissions import IsCustomerOrReadOnly, IsReviewerOrReadOnly
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsCustomerOrReadOnly, IsReviewerOrReadOnly]
    serializer_class = ReviewSerializer
    filterset_fields = ["business_user_id", "reviewer_id"]
    ordering_fields = ["updated_at", "rating"]
    ordering = ["-updated_at", "id"]

    def get_queryset(self):
        return Review.objects.select_related(
            "reviewer",
            "business_user",
        ).order_by("-updated_at", "id")
