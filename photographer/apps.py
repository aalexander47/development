from django.apps import AppConfig


class PhotographerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'photographer'

    def ready(self):
        import photographer.signals  # Ensure the signals are imported