# python imports
import logging
from datetime import datetime
# django imports
from django.db.models.signals import post_save
from django.dispatch import receiver
# project imports
from bookings.models import Roster
# app imports
from .models import (
    Client, 
    ClientContractLog,
    Pricing,
)

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Client)
def create_client_contract_logs(
    sender,
    instance,
    created,
    **kwargs,
):
    if created is False:
        if instance.tracker.has_changed('contract'):
            try:
                ClientContractLog.objects.create(
                    client=instance,
                    old_contract=instance.tracker.previous('contract'),
                    new_contract=instance.contract,
                    updated_by=instance.updated_by,
                )
            except Exception:
                logger.error(
                    "{} ERROR creating client contract log {}".format(
                        datetime.now(),
                        instance.id,
                    ), exc_info=True,
                )

@receiver(post_save, sender=Pricing)
def set_roster_pricing(sender, instance, created, **kwargs):
    """
        Set the pricing in the roster model
    """
    rosters = Roster.objects.filter(
        client=instance.client,
        type=instance.type,
        vehicle__model=instance.model,
    )
    if instance.client_store.count() > 0:
        rosters = rosters.filter(
            client_store__in=instance.client_store.filter(),
        )   

    # set the pricing
    for roster in rosters:
        roster.cost = instance.price if instance.is_active is True else None
        roster.save()