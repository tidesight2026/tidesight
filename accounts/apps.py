from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'إدارة الحسابات'
    
    def ready(self):
        """تحميل Signals عند تحميل التطبيق"""
        import accounts.signals  # noqa

