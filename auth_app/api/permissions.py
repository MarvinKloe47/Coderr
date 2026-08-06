from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsProfileOwnerOrReadOnly(BasePermission):
    """Protect profile updates while allowing authenticated profile reads.

    Object-level writes are limited to the profile owner; authentication is
    enforced by the viewset before this permission runs.
    """

    def has_object_permission(self, request, view, obj):
        """Allow reads for authenticated users and writes for the owner only."""
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user
