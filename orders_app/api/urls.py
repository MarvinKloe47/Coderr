from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CompletedOrderCountView, OrderCountView, OrderViewSet

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [
    path("order-count/<int:user_id>/", OrderCountView.as_view(), name="order-count"),
    path(
        "completed-order-count/<int:user_id>/",
        CompletedOrderCountView.as_view(),
        name="completed-order-count",
    ),
]

urlpatterns += router.urls
