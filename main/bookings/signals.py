# python imports
import logging
# django imports
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
# project imports
from fleets.models import Vehicle
from clients.models import Pricing
from drivers.models import Driver
# app imports
from .models import (
    Roster,
    RosterVehicleLog,
    RosterDriverLog,
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Roster)
def update_vehicle_status(
    sender,
    instance,
    created,
    **kwargs,
):
    # update the vehicle status based on rosters
    if created is True:
        if instance.vehicle is not None:
            instance.vehicle.status = Vehicle.STATUS.ON_GROUND
            instance.vehicle.save()
    else:
        if instance.is_active is False:
            if (
                instance.vehicle is not None and 
                instance.vehicle.roster_set.filter(is_active=True).count() == 0
            ):
                instance.vehicle.status = Vehicle.STATUS.FOR_DEPLOYMENT
                instance.vehicle.save()
        else:
            if instance.vehicle is not None:
                current_vehicle = instance.vehicle
                current_vehicle.status = Vehicle.STATUS.ON_GROUND
                current_vehicle.save()
            # if the vehicle has been changed in the roster
            if instance.tracker.has_changed('vehicle_id'):
                previous_vehicle_id = instance.tracker.previous('vehicle_id')
                try:
                    previous_vehicle = Vehicle.objects.get(id=previous_vehicle_id)
                except Vehicle.DoesNotExist:
                    previous_vehicle = None
                # check if the previous vehicle has another active roster assigned to it
                if previous_vehicle is not None and previous_vehicle.roster_set.filter(is_active=True).count() == 0:
                    previous_vehicle.status = Vehicle.STATUS.FOR_DEPLOYMENT
                    previous_vehicle.save()
                
                # create the roster-vehicle-logs
                RosterVehicleLog.objects.create(
                    roster=instance,
                    old_vehicle=previous_vehicle,
                    new_vehicle=instance.vehicle,
                    status=instance.status,
                    created_by=instance.created_by,
                )

        # create the roster-driver-logs
        if instance.tracker.has_changed('driver_id'):
            previous_driver_id = instance.tracker.previous('driver_id')
            current_driver = instance.driver
            try:
                previous_driver= Driver.objects.get(id=previous_driver_id)
            except Driver.DoesNotExist:
                previous_driver = None
            RosterDriverLog.objects.create(
                roster=instance,
                old_driver=previous_driver,
                new_driver=current_driver,
                status=instance.status,
                created_by=instance.craeted_by,
            )


@receiver(pre_save, sender=Roster)
def update_roster_pricing(sender, instance, **kwargs):
    # update the roster cost field based on the pricing config
    if instance.is_active is True and instance.vehicle is not None:
        pricing_config = Pricing.objects.filter(
            type=instance.type,
            model=instance.vehicle.model, 
            client=instance.client, 
            client_store__in=[instance.client_store],
            is_active=True,
        ).last()
        if pricing_config is not None:
            instance.cost = pricing_config.price