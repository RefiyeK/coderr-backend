from rest_framework import permissions


class IsCustomerUserOrReadOnly(permissions.BasePermission):
    """Allows POST only for customer users; GET is open to all authenticated users."""

    def has_permission(self, request, view):
        """Checks whether the user is authenticated and (for POST) is of type 'customer'."""
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.type == 'customer'


class IsReviewerOrReadOnly(permissions.BasePermission):
    """Allows PATCH/DELETE only to the creator of the review."""

    def has_object_permission(self, request, view, obj):
        """Checks whether the requesting user is the reviewer of the review."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.reviewer == request.user