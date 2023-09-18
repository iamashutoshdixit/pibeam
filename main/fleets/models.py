# python imports
import re
import uuid 

# Django imports
from django.utils.translation import gettext_lazy as _
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.core.exceptions import ValidationError
from django.db import models
from model_utils import FieldTracker

# User imports
from libs.models import BaseModel
from config.models import Config
from users.models import User


class Vehicle(BaseModel):
    """
    Model to store vehicle details
    """

    class MODEL(models.IntegerChoices):
        PIMO = 0, _("Pimo")
        HERO_NYX = 1, _("Hero Nyx")
        HERO_LECTRO = 2, _("Hero Lectro")
        TREO_ZOR = 3, _("Treo Zor")
        LOG9 = 4, _("Log9")
        OMEGA_SEIKO = 5, _("Omega Seiki")
        ALTIGREEN = 6, _("Altigreen")
        EXPONENT = 7, _("Exponent")

    class TYPE(models.IntegerChoices):
        L0 = 0, _("L0")
        L1 = 1, _("L1")
        L2 = 2, _("L2")
        L3 = 3, _("L3")
        L5 = 4, _("L5")
        

    class STATUS(models.IntegerChoices):
        FOR_DEPLOYMENT = 0, _("For Deployment")
        ON_GROUND = 1, _("On Ground")
        UNDER_MAINTENANCE = 2, _("Under Maintenance")
        UNDER_SERVICING = 3, _("Under Servicing")

    class SPEED(models.IntegerChoices):
        LOW = 1, _("Low")
        HIGH = 2, _("High")

    def chassis_default():
        return uuid.uuid4().time_low

    registration_number = models.CharField(
        max_length=50,
        unique=True,
    )
    model = models.IntegerField(choices=MODEL.choices)
    type = models.IntegerField(choices=TYPE.choices, default=TYPE.L1)
    status = models.IntegerField(choices=STATUS.choices)
    speed = models.IntegerField(choices=SPEED.choices)
    station = models.ForeignKey(
        "fleets.Station",
        on_delete=models.PROTECT,
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        editable=False,
    )
    rc_document = models.URLField(null=True, blank=True)
    insurance_document = models.URLField(null=True, blank=True)
    insurance_start_date = models.DateField(null=True, blank=True)
    insurance_renewal_date = models.DateField(null=True, blank=True)
    chassis_number = models.CharField(
        max_length=50,
        null=False,
        unique=True,
        default=chassis_default
    )
    engine_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        unique=True,
        default=None,
    )
    dealer = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="dealer",
    )
    financier = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="financier",
    )
    is_backup = models.BooleanField(default=False)
    tracker = FieldTracker(fields=['station', 'status'])

    @classmethod
    def valid_registration(cls, rno, speed):
        """
        Returns true if a registration number is valid
        """
        pattern = r""
        if speed == Vehicle.SPEED.LOW:
            pattern = r"^PI [1-9][0-9]{4}$"
        if speed == Vehicle.SPEED.HIGH:
            pattern = r"^([A-Z]{2}\s{1}\d{2}\s{1}[A-Z]{1,2}\s{1}\d{1,4})?([A-Z]{3}\s{1}\d{1,4})?$"
        if re.match(pattern, rno):
            return True
        return False

    def __str__(self):
        return f"{self.registration_number}"

    def clean(self):
        if self.engine_number == "":
            self.engine_number = None
        if self.id is None:
            self.status = Vehicle.STATUS.FOR_DEPLOYMENT
        speed = "low" if self.speed == 1 else "high"
        valid_regd = Vehicle.valid_registration(
            self.registration_number,
            self.speed,
        )
        if not valid_regd:
            error_msg = f"Incorrent format for {speed} speed vehicle."
            raise ValidationError(
                {
                    "registration_number": error_msg,
                }
            )


class Station(BaseModel):
    """
    Model to store station details
    """
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=7, unique=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    area = models.CharField(max_length=50)
    pincode = models.IntegerField(
        validators=[
            MaxValueValidator(999999),
            MinValueValidator(100000),
        ]
    )
    lat = models.FloatField()
    long = models.FloatField()
    updated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        editable=False,
    )

    def __str__(self) -> str:
        return f"{self.name}"

    def clean(self):
        self.code = str(self.city)[:3].upper() + str(uuid.uuid4().time_low)[-4:]


class Battery(BaseModel):

    def code_default():
        return str(uuid.uuid4().time_low)[-10:]

    serial_number = models.CharField(
        max_length=50,
        unique=True,
    )
    code = models.CharField(unique=True, max_length=10, default=code_default)
    model = models.CharField(max_length=50)  # config dropdown
    protocol = models.CharField(max_length=50)  # config dropdown
    chemistry = models.CharField(max_length=50)  # config dropdown
    vehicle = models.ForeignKey(
        "fleets.Vehicle",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    is_canbus_enabled = models.BooleanField()
    cycle = models.IntegerField(null=True, blank=True)
    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
    )
    date_of_purchase = models.DateField()

    class Meta:
        verbose_name = "Battery"
        verbose_name_plural = "Batteries"

    @classmethod
    def get_values(cls, field):
        field_name = f"fleets_battery_{field}"

        def func():
            choices = Config.get_value(field_name)
            if choices is None:
                return []
            return zip(choices, choices)

        return func


class Charger(BaseModel):
    
    def code_default():
        return str(uuid.uuid4().time_low)[-10:]

    serial_number = models.CharField(
        max_length=50,
        unique=True,
    )
    code = models.CharField(unique=True, max_length=10, default=code_default)
    type = models.CharField(max_length=50)  # config dropdown
    connector = models.CharField(max_length=50)  # config dropdown
    wattage = models.CharField(max_length=50)  # config dropdown
    vehicle = models.ForeignKey(
        "fleets.Vehicle",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
    )
    date_of_purchase = models.DateField()

    class Meta:
        verbose_name = "Battery"
        verbose_name_plural = "Batteries"

    @classmethod
    def get_values(cls, field):
        field_name = f"fleets_charger_{field}"

        def func():
            choices = Config.get_value(field_name)
            if choices is None:
                return []
            return zip(choices, choices)

        return func


class GPSTracker(BaseModel):
    serial_number = models.CharField(max_length=50)
    sim_number = models.IntegerField()
    validity = models.DateField()
    type = models.CharField(max_length=50)  # config dropdown
    vehicle = models.ForeignKey(
        "fleets.Vehicle", 
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
    )

    class Meta:
        verbose_name = "GPS Tracker"
        verbose_name_plural = "GPS Trackers"

    @classmethod
    def get_values(cls, field):
        field_name = f"fleets_gpstracker_{field}"

        def func():
            choices = Config.get_value(field_name)
            if choices is None:
                return []
            return zip(choices, choices)

        return func
