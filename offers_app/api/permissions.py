from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsBusinessOrReadOnly(BasePermission):
    """Restrict offer writes to authenticated business users.

    Read operations may proceed to the remaining permission checks, but create
    and update requests require the user's Coderr role to be business.
    """

    def has_permission(self, request, view):
        """Allow safe methods and require the business role for unsafe ones."""
        if request.method in SAFE_METHODS:
            return True
        return request.user.type == "business"


class IsOfferOwnerOrReadOnly(BasePermission):
    """Protect offer modifications at the object level.

    Unsafe requests are accepted only for the offer owner. Authentication and
    role checks are composed separately on the offer viewset.
    """

    def has_object_permission(self, request, view, obj):
        """Allow reads and restrict unsafe object requests to the owner."""
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user
