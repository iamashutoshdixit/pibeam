# python imports
from datetime import timedelta

# django imports
from django.db import models


class Config(models.Model):
    """
    Model to store the configurations
    """

    key = models.CharField(max_length=50, unique=True)
    value = models.JSONField()

    @classmethod
    def get_value(cls, key):
        qs = Config.objects.filter(key=key).first()
        if qs is not None:
            return qs.value
        return None

    @classmethod
    def get_timedelta(cls):
        """
        Get the timedelta difference between two roster's creation
        """
        qs = Config.objects.filter(key="roster_timedelta").first()
        td = qs.value if qs else 0
        return timedelta(hours=td)

    class Meta:
        verbose_name = "Config"
        verbose_name_plural = "Configs"
