from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsCustomerOrReadOnly(BasePermission):
    """Restrict review writes to users with the customer role.

    Safe reads remain available to authenticated users, while create and update
    requests require the Coderr customer role.
    """

    def has_permission(self, request, view):
        """Allow safe methods and require the customer role for writes."""
        if request.method in SAFE_METHODS:
            return True
        return request.user.type == "customer"


class IsReviewerOrReadOnly(BasePermission):
    """Protect review modifications at the object level.

    Unsafe requests are allowed only for the reviewer stored on the review;
    customer-role validation is handled by a separate permission.
    """

    def has_object_permission(self, request, view, obj):
        """Allow reads and restrict unsafe object requests to the reviewer."""
        if request.method in SAFE_METHODS:
            return True
        return obj.reviewer == request.user
