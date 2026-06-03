from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """Admin-Konfiguration für CustomUser, erweitert um das 'type'-Feld."""

    # Listenansicht: welche Spalten in der User-Liste angezeigt werden
    list_display = ('username', 'email', 'type', 'is_staff', 'date_joined')

    # Filter-Sidebar rechts
    list_filter = UserAdmin.list_filter + ('type',)

    # Detail-/Bearbeitungsansicht eines bestehenden Users
    fieldsets = UserAdmin.fieldsets + (
        ('Coderr', {'fields': ('type',)}),
    )

    # Ansicht beim Anlegen eines neuen Users
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Coderr', {'fields': ('type',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
