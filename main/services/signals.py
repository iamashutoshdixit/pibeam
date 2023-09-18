# python imports
import logging
from datetime import datetime
# django imports
from django.db.models.signals import post_save
from django.dispatch import receiver
# project imports
from fleets.models import Vehicle
from bookings.models import Roster
from libs.helpers import email
# app imports
from .models import (
    Service,
    ServiceLog,
)

logger = logging.getLogger(__name__)


def send_open_mail_to_service(instance):
    # send an email to the servicing team for newly opened tickets
    if instance.status == Service.STATUS.OPEN.value:
        try:
            email(
                subject=f"NEW SERVICE TICKET FOR {instance.vehicle.registration_number}",
                message=f"\
                    Registration Number: {instance.vehicle.registration_number}\n \
                    Issue Type: {instance.issue_type}\n \
                    Issue Subtype: {instance.issue_subtype}\n \
                    Reportee: {instance.reportee.phone_no if instance.reportee else None}\n \
                    Location: http://maps.google.com/maps?q={instance.latitude},{instance.longitude}\n \
                    City: {instance.vehicle.station.city}\n \
                    Description: {instance.description}\n \
                    Created By: {instance.created_by}\n \
                    Ticket: http://65.1.9.250:8001/a0ce743445e30281/admin/services/servicing/{instance.id}/change\n \
                ",
                recipient_list=["Service@fynmobility.com", "aravind.s@fynmobility"],
            )
        except Exception:
            logger.error(
                "{} Error while sending email to the service team for vehicle {}".format(
                    datetime.now(),
                    instance.vehicle.registration_number,
                )
            )


def send_complete_mail_to_ops(instance):
    # send an email to the servicing team for newly opened tickets
    if instance.status == Service.STATUS.OPEN.value:
        try:
            email(
                subject=f"SERVICE COMPLETE FOR {instance.vehicle.registration_number}",
                message=f"\
                    Ticket Number: {instance.id}\n \
                    Registration Number: {instance.vehicle.registration_number}\n \
                    Issue Type: {instance.issue_type}\n \
                    Issue Subtype: {instance.issue_subtype}\n \
                    Reportee: {instance.reportee.phone_no if instance.reportee else None}\n \
                    City: {instance.vehicle.station.city}\n \
                    Description: {instance.description}\n \
                    ============================================== \n \
                    Remarks: {instance.remarks}\n \
                    Updated At: {instance.updated_at}\n \
                    Ticket: http://65.1.9.250:8001/a0ce743445e30281/admin/services/servicing/{instance.id}/change\n \
                ",
                recipient_list=["operations@fynmobility.com"],
            )
        except Exception:
            logger.error(
                "{} Error while sending email to the ops team, for the vehicle: {}".format(
                    datetime.now(),
                    instance.vehicle.registration_number,
                )
            )



@receiver(post_save, sender=Service)
def update_vehicle_status(
    sender,
    instance,
    created,
    **kwargs,
):
    """
        1. Update the Vehicle Status to Service Statuses
        2. Remove the Vehicle from Rosters
        3. Send mail
    """
    vehicle = instance.vehicle
    if created is True:
        rosters = Roster.objects.filter(vehicle=vehicle)
        for roster in rosters:
            roster.vehicle = None
            roster.status = Roster.STATUS.SERVICE
            roster.save()
        # move the vehicle to under_maintenance status
        vehicle.status = Vehicle.STATUS.UNDER_MAINTENANCE
        vehicle.save()
        send_open_mail_to_service(instance)
    else: 
        # if there's no change in the status, do nothing
        if instance.tracker.has_changed('status') is False:
            return

        # move the vehicle to under_servicing status
        if instance.status in [ 
            Service.STATUS.IN_PROGRESS.value, 
            Service.STATUS.ON_HOLD.value,
        ]:
            vehicle.status = Vehicle.STATUS.UNDER_SERVICING
            vehicle.save()

        # move the vehicle to for_deployment status and mark service record as inactive
        if instance.status == Service.STATUS.COMPLETED.value:
            vehicle.status = Vehicle.STATUS.FOR_DEPLOYMENT
            vehicle.save()
            # send mail to ops
            send_complete_mail_to_ops(instance)
        
        
        # log the changes
        logger.info(
            "{} INFO service status: {} updated for vehicle: {}".format(
                datetime.now(),
                instance.status,
                vehicle.registration_number,
            )
        )

        # create service status logs
        ServiceLog.objects.create(
            service=instance,
            old_status=instance.tracker.previous('status'),
            new_status=instance.status,
            remarks=instance.remarks,
            created_by=instance.updated_by,
            created_at=instance.updated_at,
        )
        
    
