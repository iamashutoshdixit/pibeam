# python imports
import logging
from datetime import datetime
# django imports
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from smart_selects.db_fields import ChainedForeignKey
from django.utils.translation import gettext_lazy as _
from model_utils import FieldTracker
# project imports
from config.models import Config
from libs.models import BaseModel
from fleets.models import Vehicle

logger = logging.getLogger(__name__)


class Roster(BaseModel):
    """
    Model to store roster information
    """
    class STATUS(models.IntegerChoices):
        IN_ACTIVE = 0, _("In Active")
        ACTIVE = 1, _("Active")
        ATTRITION = 2, _("Attrition")
        SERVICE = 3, _("Service")

    class TYPE(models.IntegerChoices):
        RENTAL = 0, _("Rental")
        LOGISTICS_FIXED = 1, _("Logistics - Fixed")
        LOGISTICS_TRIP = 2, _("Logistics - Trip")
        LOGISTICS_DELIVERY = 3, _("Logistics - Delivery")

    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    client_store = ChainedForeignKey(
        "clients.ClientStore",
        chained_field="client",
        chained_model_field="client",
        show_all=False,
        null=True,
        blank=True,
    )
    type = models.PositiveSmallIntegerField(
        choices=TYPE.choices,
        default=TYPE.LOGISTICS_FIXED,
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS.choices,
        default=STATUS.ACTIVE,
    )
    city = models.CharField(max_length=50, null=True, editable=False)
    driver = models.ForeignKey("drivers.Driver", on_delete=models.PROTECT, blank=True, null=True)
    vehicle = models.ForeignKey("fleets.Vehicle", blank=True, null=True, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    holiday = ArrayField(
        models.DateField(null=True, blank=True),
        null=True,
        blank=True,
    )
    slot_start_time = models.TimeField()
    slot_end_time = models.TimeField()
    lat = models.FloatField(editable=False)
    long = models.FloatField(editable=False)
    address = models.CharField(max_length=200, editable=False)
    destination_station = models.ForeignKey(
        "fleets.Station",
        on_delete=models.PROTECT,
    )
    remarks = models.CharField(max_length=250, null=True, blank=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        editable=False,
        null=True,
        blank=True,
    )
    cost = models.FloatField(null=True, editable=False)
    tracker = FieldTracker()

    @property
    def destination_lat(self):
        return self.destination_station.lat

    @property
    def destination_long(self):
        return self.destination_station.long

    @classmethod
    def is_valid_driver_entry(
        cls,
        driver,
        start_time,
        end_time,
        start_date,
        end_date,
        current_id=None,
    ):
        time_diff = Config.get_timedelta()
        tmp = datetime(
            2000,
            1,
            1,
            start_time.hour,
            start_time.minute,
            start_time.second,
        )
        start_time = (tmp - time_diff).time()
        tmp = datetime(
            2000,
            1,
            1,
            end_time.hour,
            end_time.minute,
            end_time.second,
        )
        end_time = (tmp + time_diff).time()
        qs = Roster.objects.filter(driver=driver, is_active=True).exclude(id=current_id)
            
        # check if the date is overlapping
        valid = True
        for obj in qs:
            if cls.is_date_overlapped(obj.start_date, obj.end_date, start_date, end_date) is True:
                if cls.is_time_overlapped(obj.slot_start_time, obj.slot_end_time, start_time, end_time) is True:
                    valid = False
                    break

        return valid

    @classmethod
    def is_time_overlapped(cls, s1, e1, s2, e2):
        return any(
            [
                s1 <= s2 <= e1,
                s1 <= e2 <= e1,
                s2 <= s1 <= e2,
                s2 <= e1 <= e2,
            ]
        )

    @classmethod
    def is_date_overlapped(cls, start1, end1, start2, end2):
        return (start1 <= end2) and (start2 <= end1)

    @classmethod
    def is_valid_vehicle_entry(
        cls,
        vehicle,
        start_time,
        end_time,
        start_date,
        end_date,
        current_id=None,
    ):
        time_diff = Config.get_timedelta()
        tmp = datetime(
            2000,
            1,
            1,
            start_time.hour,
            start_time.minute,
            start_time.second,
        )
        start_time = (tmp - time_diff).time()
        tmp = datetime(
            2000,
            1,
            1,
            end_time.hour,
            end_time.minute,
            end_time.second,
        )
        end_time = (tmp + time_diff).time()
        qs = Roster.objects.filter(vehicle=vehicle, is_active=True).exclude(id=current_id)

        # check if the date is overlapping
        valid = True
        for obj in qs:
            if cls.is_date_overlapped(obj.start_date, obj.end_date, start_date, end_date) is True:
                if cls.is_time_overlapped(obj.slot_start_time, obj.slot_end_time, start_time, end_time) is True:
                    valid = False
                    break
        return valid

    def clean(self):
        if self.client_store is None:
            raise ValidationError(_("Client Store is mandatory."), code="invalid")
        if self.status is Roster.STATUS.ACTIVE.value: 
            if self.vehicle is None:
                raise ValidationError(_("Vehicle must be added for creating an active roster"), code="invalid")
            if self.type != Roster.TYPE.RENTAL.value and self.driver is None:
                raise ValidationError(_("Driver is mandatory for non-rental rosters"), code="invalid")
        if self.vehicle is not None:
            if self.vehicle.is_active is False:
                raise ValidationError(_("Vehicle is inactive"), code="invalid")
            if self.vehicle.status in [
                Vehicle.STATUS.UNDER_MAINTENANCE.value, 
                Vehicle.STATUS.UNDER_SERVICING.value
            ]:
                raise ValidationError(_("Vehicle is under servicing/maintanence"), code="invalid")
            if Roster.is_valid_vehicle_entry(
                    self.vehicle,
                    self.slot_start_time,
                    self.slot_end_time,
                    self.start_date,
                    self.end_date,
                    self.id,
                ) is False:
                    raise ValidationError(_("Vehicle already occupied"), code="invalid")
        try:
            if self.driver is not None:
                if Roster.is_valid_driver_entry(
                    self.driver,
                    self.slot_start_time,
                    self.slot_end_time,
                    self.start_date,
                    self.end_date,
                    self.id,
                ) is False:
                    raise ValidationError(_("Driver already occupied"), code="invalid")
                if not self.driver.onboarding.has_driver_license and self.vehicle.speed == Vehicle.SPEED.HIGH:
                    raise ValidationError(_("Cannot assign high speed vehicle to driver without license."), code="invalid")
        except AttributeError:
            logger.warning("Roster Creation Failed", exc_info=True)


    class Meta:
        verbose_name = "Roster"
        verbose_name_plural = "Rosters"

    @property
    def is_roster_active(self):
        diff_start = datetime.now().date() - self.start_date
        diff_end = self.end_date - datetime.now().date()
        return diff_end.days >= 0 and diff_start.days >= 0


class Trip(BaseModel):
    """
    Model to store trips records of a roster
    """

    class STATUS(models.IntegerChoices):
        RIDE_STARTED = 0, _("Ride Started")
        CHECK_IN = 1, _("Check In")
        CHECK_OUT = 2, _("Check Out")
        RIDE_COMPLETED = 3, _("Ride Completed")

    roster = models.ForeignKey("Roster", on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField(
        choices=STATUS.choices,
        null=True,
    )
    checkin_time = models.DateTimeField(null=True, blank=True)
    checkout_time = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    start_km = models.FloatField(null=True, blank=True)
    end_km = models.FloatField(null=True, blank=True)
    in_latitude = models.FloatField(null=True, blank=True)
    in_longitude = models.FloatField(null=True, blank=True)
    out_latitude = models.FloatField(null=True, blank=True)
    out_longitude = models.FloatField(null=True, blank=True)
    trip_sheet_photo = models.URLField(null=True, blank=True)
    vehicle_photos = ArrayField(models.URLField(), null=True, blank=True)

    class Meta:
        verbose_name = "Trip"
        verbose_name_plural = "Trips"

    @property
    def vehicle_regd_no(self):
        return self.vehicle.registration_number


class RosterDriverLog(models.Model):
    roster = models.ForeignKey("Roster", on_delete=models.PROTECT)
    old_driver = models.ForeignKey("drivers.Driver", on_delete=models.PROTECT, null=True, related_name="old_driver")
    new_driver = models.ForeignKey("drivers.Driver", on_delete=models.PROTECT, null=True, related_name="new_driver")
    status = models.PositiveSmallIntegerField(
        choices=Roster.STATUS.choices,
        default=Roster.STATUS.ACTIVE,
    )
    created_by = models.ForeignKey(
        "users.User", 
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Roster Driver Log"
        verbose_name_plural = "Roster Driver Logs"

    @classmethod
    def get_fields(cls):
        return [field.name for field in cls._meta.get_fields()]


class RosterVehicleLog(models.Model):
    roster = models.ForeignKey("Roster", on_delete=models.PROTECT)
    old_vehicle = models.ForeignKey("fleets.Vehicle", on_delete=models.PROTECT, null=True, related_name="old_vehicle")
    new_vehicle = models.ForeignKey("fleets.Vehicle", on_delete=models.PROTECT, null=True, related_name="new_vehicle")
    status = models.PositiveSmallIntegerField(
        choices=Roster.STATUS.choices,
        default=Roster.STATUS.ACTIVE,
    )
    created_by = models.ForeignKey(
        "users.User", 
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Roster Vehicle Log"
        verbose_name_plural = "Roster Vehicle Logs"

    @classmethod
    def get_fields(cls):
        return [field.name for field in cls._meta.get_fields()]