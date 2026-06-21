from rest_framework import permissions


class IsCustomerUserOrReadOnly(permissions.BasePermission):
    """Erlaubt POST nur für Customer-User; GET ist für alle authentifizierten User offen."""

    def has_permission(self, request, view):
        """Prüft, ob der User authentifiziert ist und für POST den type 'customer' hat."""
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.type == 'customer'
    
class IsReviewerOrReadOnly(permissions.BasePermission):
    """Erlaubt PATCH/DELETE nur dem Ersteller der Review."""

    def has_object_permission(self, request, view, obj):
        """Prüft, ob der anfragende User der reviewer der Review ist."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.reviewer == request.user