from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Erweitert Django's Standard-User um ein 'type'-Feld"""

    TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    def __str__(self):
        """Gibt Benutzername mit Typ zurück."""
        return f"{self.username} ({self.type})"
