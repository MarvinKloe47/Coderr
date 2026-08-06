from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from reviews_app.models import Review

from .permissions import IsCustomerOrReadOnly, IsReviewerOrReadOnly
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Expose review CRUD with customer-only writes and owner-only edits.

    Authenticated users may read reviews with documented filters and ordering,
    while creation is restricted to customers and updates stay with the
    original reviewer.
    """

    permission_classes = [IsAuthenticated, IsCustomerOrReadOnly, IsReviewerOrReadOnly]
    serializer_class = ReviewSerializer
    pagination_class = None
    filterset_fields = ["business_user_id", "reviewer_id"]
    ordering_fields = ["updated_at", "rating"]
    ordering = ["-updated_at", "id"]

    def get_queryset(self):
        """Load reviewer and business user to avoid extra queries."""
        return Review.objects.select_related(
            "reviewer",
            "business_user",
        ).order_by("-updated_at", "id")
