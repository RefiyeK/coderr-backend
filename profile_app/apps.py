from django.apps import AppConfig


class ProfileAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profile_app'

    def ready(self):
        """Importiert Signale, wenn die App geladen wird."""
        import profile_app.signals