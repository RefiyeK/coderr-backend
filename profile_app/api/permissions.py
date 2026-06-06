from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Erlaubt nur dem Eigentümer eines Profile, es zu bearbeiten.
    Lesezugriff ist für alle authentifizierten Benutzer erlaubt.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user