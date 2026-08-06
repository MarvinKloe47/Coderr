from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import User
from orders_app.models import Order

from .permissions import CanCreateOrUpdateOrder, IsOrderParticipant
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """Expose order CRUD with participant-scoped access.

    Customers create orders from offer details, involved customers and business
    users can read them, business users update status, and staff users may
    delete orders.
    """

    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    permission_classes = [IsAuthenticated, IsOrderParticipant, CanCreateOrUpdateOrder]
    serializer_class = OrderSerializer
    pagination_class = None

    def get_queryset(self):
        """Return only orders involving the authenticated user."""
        user = self.request.user
        queryset = Order.objects.select_related(
            "customer_user",
            "business_user",
            "offer_detail",
        )
        if user.is_staff:
            return queryset.order_by("-created_at", "id")
        return (
            queryset.filter(customer_user=user) | queryset.filter(business_user=user)
        ).order_by("-created_at", "id")


class OrderCountView(APIView):
    """Return the number of in-progress orders for a business profile.

    The endpoint accepts only business user IDs and returns the key documented
    for the frontend order counter.
    """

    status_filter = Order.Status.IN_PROGRESS

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id, type=User.Types.BUSINESS)
        count = user.business_orders.filter(status=self.status_filter).count()
        return Response({"order_count": count})


class CompletedOrderCountView(OrderCountView):
    """Return the number of completed orders for a business profile.

    It reuses the same business-user lookup as OrderCountView but exposes the
    completed_order_count response key required by the API contract.
    """

    status_filter = Order.Status.COMPLETED

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id, type=User.Types.BUSINESS)
        count = user.business_orders.filter(status=self.status_filter).count()
        return Response({"completed_order_count": count})
