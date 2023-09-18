# django imports
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.IntegerChoices):
        NON_STAFF = 0, _("Driver")
        OPERATIONS_MANAGER = 1, _("Operations Manager")
        FLEET_MANAGER = 2, _("Fleet Manager")
        SERVICE_MANAGER = 3, _("Service Manager")
        OPERATIONS_EXECUTIVE = 4, _("Operations Executive")

    full_name = models.CharField(max_length=50, null=True)
    role = models.PositiveSmallIntegerField(choices=Role.choices, default=2)
    employee_id = models.IntegerField(null=True, blank=True, unique=True)
    is_staff = models.BooleanField(default=False)
    phone_no = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.username}"

    def save(self, *args, **kwargs):
        if any(
            [
                self.role
                in {
                    User.Role.OPERATIONS_EXECUTIVE,
                    User.Role.FLEET_MANAGER,
                    User.Role.SERVICE_MANAGER,
                    User.Role.OPERATIONS_MANAGER,
                },
                self.is_superuser,
            ]
        ):
            self.is_staff = True
        else:
            self.is_staff = False

        super().save(*args, **kwargs)
