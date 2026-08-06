from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsBusinessOrReadOnly(BasePermission):
    """Allow offer creation and writes only for business users."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.type == "business"


class IsOfferOwnerOrReadOnly(BasePermission):
    """Allow offer changes only for the user who owns the offer."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user
