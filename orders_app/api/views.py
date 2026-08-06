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
    """Manage orders visible only to the customer or business participant."""

    http_method_names = ["get", "post", "patch", "head", "options"]
    permission_classes = [IsAuthenticated, IsOrderParticipant, CanCreateOrUpdateOrder]
    serializer_class = OrderSerializer
    pagination_class = None

    def get_queryset(self):
        """Return only orders involving the authenticated user."""
        user = self.request.user
        queryset = Order.objects.select_related("customer_user", "business_user")
        return (
            queryset.filter(customer_user=user) | queryset.filter(business_user=user)
        ).order_by("-created_at", "id")


class OrderCountView(APIView):
    """Count in-progress orders for a business user."""

    status_filter = Order.Status.IN_PROGRESS

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id, type=User.Types.BUSINESS)
        count = user.business_orders.filter(status=self.status_filter).count()
        return Response({"order_count": count})


class CompletedOrderCountView(OrderCountView):
    """Count completed orders for a business user."""

    status_filter = Order.Status.COMPLETED
