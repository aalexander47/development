from django.apps import AppConfig


class VideographerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videographer'

    def ready(self):
        import videographer.signals  # Ensure the signals are imported