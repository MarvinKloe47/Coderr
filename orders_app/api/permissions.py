from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOrderParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in {obj.customer_user, obj.business_user}


class CanCreateOrUpdateOrder(BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return request.user.type == "customer"
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user == obj.business_user
