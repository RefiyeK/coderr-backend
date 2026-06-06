from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Profil eines Benutzers mit zusätzlichen Daten zur User-Tabelle."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='profile'
        )
    file = models.FileField(upload_to='profile_pictures/', null=True, blank=True)
    location = models.CharField(max_length=255,blank=True, default='')
    tel = models.CharField(max_length=20, blank=True, default='')
    working_hours = models.CharField(
    max_length=255, blank=True, default='')
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
