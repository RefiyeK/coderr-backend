from rest_framework import permissions


class IsCustomerUserOrReadOnly(permissions.BasePermission):
    """Erlaubt POST nur für Customer-User; GET ist für alle authentifizierten User offen."""

    def has_permission(self, request, view):
        """Prüft, ob der User authentifiziert ist und für POST den type 'customer' hat."""
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.type == 'customer'


class IsBusinessOwnerForUpdate(permissions.BasePermission):
    """Erlaubt PATCH nur, wenn der request.user der business_user der Order ist."""

    def has_object_permission(self, request, view, obj):
        """Prüft, ob der anfragende User der business_user der Order ist."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.business_user == request.user
