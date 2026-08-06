from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOrderParticipant(BasePermission):
    """Restrict order object access to participants and staff users.

    Customers and business users may access only orders in which they are
    stored as participants. Staff bypasses this object restriction for admin
    deletion support.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return request.user in {obj.customer_user, obj.business_user}


class CanCreateOrUpdateOrder(BasePermission):
    """Apply role-specific order write rules.

    Customers may create orders, business participants may update order status,
    and delete requests are reserved for staff users.
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            return request.user.type == "customer"
        if request.method == "DELETE":
            return request.user.is_staff
        return True

    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return request.user.is_staff
        if request.method in SAFE_METHODS:
            return True
        return request.user == obj.business_user
