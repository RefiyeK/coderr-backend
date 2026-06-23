from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser, extended with the 'type' field."""
    # List view: which columns are shown in the user list
    list_display = ('username', 'email', 'type', 'is_staff', 'date_joined')
    # Filter sidebar on the right
    list_filter = UserAdmin.list_filter + ('type',)
    # Detail / edit view of an existing user
    fieldsets = UserAdmin.fieldsets + (
        ('Coderr', {'fields': ('type',)}),
    )
    # View when creating a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Coderr', {'fields': ('type',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)