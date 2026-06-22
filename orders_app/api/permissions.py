from rest_framework import permissions


class IsCustomerUserOrReadOnly(permissions.BasePermission):
    """Allows POST only for customer users; GET is open to all authenticated users."""

    def has_permission(self, request, view):
        """Checks whether the user is authenticated and (for POST) is of type 'customer'."""
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.type == 'customer'


class IsBusinessOwnerForUpdate(permissions.BasePermission):
    """Allows PATCH only if the request user is the business_user of the order."""

    def has_object_permission(self, request, view, obj):
        """Checks whether the requesting user is the business_user of the order."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.business_user == request.user