from rest_framework import permissions


class IsBusinessUserOrReadOnly(permissions.BasePermission):
    """Erlaubt Lesezugriff für alle, Schreibzugriff nur für authentifizierte Business-User."""

    def has_permission(self, request, view):
        """Erlaubt nur Business-Usern, Offers zu erstellen oder zu bearbeiten."""
        # Alle Benutzer können GET-Anfragen durchführen
        if request.method in permissions.SAFE_METHODS:
            return True
        # Nur authentifizierte Business-User können POST, PUT, DELETE durchführen
        return request.user.is_authenticated and request.user.type == 'business'


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Erlaubt nur dem Eigentümer eines Offers, es zu bearbeiten oder zu löschen.
    Lesezugriff ist für alle authentifizierten Benutzer erlaubt.
    """

    def has_object_permission(self, request, view, obj):
        """Prüft, ob der anfragende User der Eigentümer des Offers ist."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
