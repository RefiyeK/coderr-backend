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