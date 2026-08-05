from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    BusinessProfileListView,
    CustomerProfileListView,
    LoginView,
    ProfileViewSet,
    RegistrationView,
)

router = DefaultRouter()
router.register("profile", ProfileViewSet, basename="profile")

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("login/", LoginView.as_view(), name="login"),
    path("profiles/business/", BusinessProfileListView.as_view(), name="business-profiles"),
    path("profiles/customer/", CustomerProfileListView.as_view(), name="customer-profiles"),
]

urlpatterns += router.urls
