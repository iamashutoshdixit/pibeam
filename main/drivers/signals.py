# python imports
import logging
import json
from datetime import datetime

# django imports
from django.db.models.signals import post_save, pre_save
from django.db.utils import IntegrityError
from django.core.cache import cache
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
# project level imports
from users.models import User
from config.models import Config

# app level imports
from .models import (
    Onboarding,
    Driver,
    DriverAadharDetails,
    DriverContract,
)

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Driver)
def driver_pre_save_handler(sender, instance, **kwargs):
    user = User.objects.filter(username=str(instance.onboarding.mobile_no)).first()
    if user is not None:
        user.username = str(instance.onboarding.mobile_no)
        user.full_name = instance.onboarding.full_name
        user.phone_no = instance.onboarding.mobile_no
        user.set_password(instance.onboarding.full_name.replace(" ", "")[:4] + str(instance.onboarding.mobile_no)[:4])
        user.save()
        return
    username = str(instance.onboarding.mobile_no)
    password = instance.onboarding.full_name[:4] + username[:4]
    try:
        user = User.objects.create_user(
            username=username,
            password=password,
            full_name=instance.onboarding.full_name,
            phone_no=instance.onboarding.mobile_no,
            role=0,
        )
        instance.user = user
        instance.id = user.id
    except Exception:
        logger.error(
            "{} ERROR creating user for the driver {}".format(
                datetime.now(),
                username,
            ), exc_info=True
        )


@receiver(pre_save, sender=Driver)
def driver_post_save_handler(sender, instance, **kwargs):
    """
        Activate/Deactivate the user associated with the driver    
    """
    if instance.tracker.has_changed('is_active'):
        try:
            user = instance.user
            if instance.is_active is False:
                user.auth_token.delete()
                user.is_active = False
            else:
                user.is_active = True
                Token.objects.create(user=user)
            user.save()
        except Exception:
            logger.error("Error deleting the user token", exc_info=True)


@receiver(post_save, sender=Onboarding)
def onboarding_post_save_handler(sender, instance, created, **kwargs):
    if instance.status is Onboarding.Status.APPROVED.value:
        mobile_no = instance.mobile_no
        vendor = None
        if hasattr(instance, "vendor"):
            vendor = instance.vendor
        try:
            Driver.objects.get_or_create(
                onboarding=instance,
                doj=datetime.now().date(),
                vendor=vendor,
                remarks=instance.remarks,
            )
        except IntegrityError:
            logger.info(
                "{} INFO driver with mobile number {} already exists.".format(
                    datetime.now(),
                    mobile_no,
                )
            )


@receiver(pre_save, sender=Onboarding)
def verify_onboarding(sender, instance, update_fields=None, **kwargs):
    # set has_driving_license field
    if (
        instance.driver_license_number and
        instance.driver_license_front and
        instance.driver_license_back
    ):
        instance.has_driver_license = True
    else:
        instance.has_driver_license = False

    # verify the aadhar details
    details = cache.get(f"{instance.aadhar_number}", None)
    if details is None:
        return
    data = details["data"]
    DriverAadharDetails.objects.get_or_create(
        aadhar_number=instance.aadhar_number,
        data=json.dumps(data),
        full_name=data["full_name"],
        dob=data["dob"],
        gender=data["gender"],
        country=data["address"]["country"],
        district=data["address"]["dist"],
        state=data["address"]["state"],
        po=data["address"]["po"],
        loc=data["address"]["loc"],
        vtc=data["address"]["vtc"],
        subdist=data["address"]["subdist"],
        street=data["address"]["street"],
        house=data["address"]["house"],
        landmark=data["address"]["landmark"],
        zip=data["zip"],
    )
    dob = f"{instance.dob}"
    if instance.full_name == data["full_name"] and str(dob) == data["dob"]:
        instance.aadhar_verified = True


@receiver(post_save, sender=DriverContract)
def mark_contract_accepted_false(sender, instance, created, **kwargs):
    if created is True:
        contract_config = Config.objects.get(key="latest_contract")
        contract_config.value = instance.id
        contract_config.save()
        Driver.objects.all().update(contract_accepted=False)
