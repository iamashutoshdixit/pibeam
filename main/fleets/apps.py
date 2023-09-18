from django.apps import AppConfig


class FleetsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "fleets"
    verbose_name = "Fleet Management"

    def ready(self):
        from . import signals
