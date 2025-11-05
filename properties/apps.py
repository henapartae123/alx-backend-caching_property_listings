from django.apps import AppConfig


class PropertiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'properties'

    def ready(self):
        """
        Import signal handlers when the app is ready.
        This ensures signals are registered before any operations.
        """
        import properties.signals
