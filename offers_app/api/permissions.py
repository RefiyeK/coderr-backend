from rest_framework import permissions


class IsBusinessUserOrReadOnly(permissions.BasePermission):
    """Allows read access for everyone, write access only for authenticated business users."""

    def has_permission(self, request, view):
        """Allows only business users to create or modify offers."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.type == 'business'


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allows only the owner of an offer to edit or delete it.
    Read access is granted to all authenticated users.
    """

    def has_object_permission(self, request, view, obj):
        """Checks whether the requesting user is the owner of the offer."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user