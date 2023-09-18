# python imports
from datetime import datetime

# django imports
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import (
    MaxValueValidator as Max,
    MinValueValidator as Min,
)

# project imports
from libs.models import BaseModel
from config.models import Config

# app imports
from .constants import VENDOR_PER_TRIP_AMOUNT


class Vendor(BaseModel):
    """
        Contains the information about the third-party vendors    
    """
    class TYPE(models.IntegerChoices):
        DRIVER = 0, _("Driver")
        GPS_TRACKER = 1, _("GPS Tracker")
        BATTERY = 2, _("Battery")
        VEHICLE = 3, _("Vehicle")
        CHARGING_STATION = 4, _("Charging Station")
        PARKING_LOT = 5, _("Parking Lot")
        FINANCE = 6, _("Finance")
        CHARGER = 7, _("Charger")

    name = models.CharField(max_length=50)
    type = models.IntegerField(choices=TYPE.choices, null=True, blank=False)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    locality = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    contact_person = models.CharField(max_length=50)
    contact_number = models.BigIntegerField(
        validators=[Min(1000000000), Max(9999999999)],
    )
    gst = models.CharField(max_length=15)
    account_number = models.BigIntegerField()
    account_name = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.id} | {self.name}"
