# Django imports
from django.db.models.signals import post_save
from django.dispatch import receiver

# User imports
from .models import User
from .helpers import get_perms


@receiver(post_save, sender=User)
def user_post_save_handler(sender, instance, created, **kwargs):
    if created:
        if instance.role > 0:
            instance.is_staff = True
            instance.save()

    if instance.role == User.Role.OPERATIONS_MANAGER:
        instance.user_permissions.set(
            get_perms(
                "onboarding",
                "trip",
                "roster",
                "drivers",
                "drivercontract",
                "drivercontractlog",
                "vendor",
                "station",
                "vehicle",
                "vehiclestationlogs",
                "vehiclestatuslogs",
                "config",
                "user",
                "client",
                "clientstore",
                "group",
                "gpstracker",
                "battery"
            )
        )

    elif instance.role == User.Role.FLEET_MANAGER:
        instance.user_permissions.set(
            [
                *get_perms(
                    "onboarding",
                    "trip",
                    "roster",
                    "driver",
                    "station",
                    "vehicle",
                    "client",
                    "clientstore",
                    scope="view"
                ),
            ]
        )

    elif instance.role == User.Role.SERVICE_MANAGER:
        instance.user_permissions.set(
            get_perms(
                "vehicle",
                "station",
                scope="view",
            )
        )

    elif instance.role == User.Role.OPERATIONS_EXECUTIVE:
        instance.user_permissions.set(
            [
                *get_perms("roster", "vehicle", "station"),
                *get_perms(
                    "driver",
                    "onboarding",
                    "client",
                    "clientstore"
                    "trip",
                    "user",
                    scope="view",
                )
            ]
        )
