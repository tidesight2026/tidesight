from django.apps import AppConfig


class DailyOperationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "daily_operations"
    
    def ready(self):
        import daily_operations.signals  # noqa