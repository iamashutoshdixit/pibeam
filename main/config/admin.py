# django imports
from django.contrib import admin

# app level imports
from .models import Config


class ConfigAdmin(admin.ModelAdmin):
    """
    Admin View for the configuration module
    """

    list_display = (
        "key",
        "value",
    )


admin.site.register(Config, ConfigAdmin)
