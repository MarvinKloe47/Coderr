from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsCustomerOrReadOnly(BasePermission):
    """Allow review creation only for customer users."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.type == "customer"


class IsReviewerOrReadOnly(BasePermission):
    """Allow review changes only for the user who wrote the review."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.reviewer == request.user
