from django.db import models
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-id']

    @classmethod
    def get_fields(cls):
        return [field.name for field in cls._meta.get_fields()]



class CITY(models.IntegerChoices):
    CHENNAI = 0, _("Chennai")
    BENGALURU = 1, _("Bengaluru")