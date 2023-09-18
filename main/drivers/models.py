# python imports
import logging

# django imports
from django.db import models
from django.core.validators import (
    MaxValueValidator as Max,
    MinValueValidator as Min,
)
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from model_utils import FieldTracker
# project level imports
from libs.models import BaseModel
from users.models import User

# app level imports
from .helpers import driver_age_validator

logger = logging.getLogger(__name__)


class Onboarding(BaseModel):
    """
    Model to store onboarding information for drivers
    """

    def validate_digits(account_number):
        if not account_number.isdigit():
            raise ValidationError('This field cannot contain alphabets')

    class Status(models.IntegerChoices):
        REGISTERED = 0, _("Registered")
        UNDER_APPROVAL = 1, _("Under Approval")
        APPROVED = 2, _("Approved")
        REJECTED = 3, _("Rejected")

    full_name = models.CharField(max_length=50)
    dob = models.DateField()
    mobile_no = models.BigIntegerField(
        unique=True,
        validators=[Min(1000000000), Max(9999999999)],
    )
    # current address
    house_no = models.CharField(max_length=15)
    street = models.CharField(max_length=100)
    locality = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    pincode = models.IntegerField(
        validators=[Min(100000), Max(999999)],
    )
    state = models.CharField(max_length=50)
    # permanent address
    permanent_house_no = models.CharField(max_length=15, null=True, blank=True)
    permanent_street = models.CharField(max_length=100, null=True, blank=True)
    permanent_locality = models.CharField(max_length=100, null=True, blank=True)
    permanent_city = models.CharField(max_length=50, null=True, blank=True)
    permanent_pincode = models.IntegerField(
        validators=[Min(100000), Max(999999)],
        null=True, blank=True,
    )
    permanent_state = models.CharField(max_length=50, null=True, blank=True)
    own_house = models.BooleanField(default=True)
    photo = models.URLField()
    aadhar_number = models.BigIntegerField(unique=True)
    aadhar_front = models.URLField()
    aadhar_back = models.URLField()
    aadhar_verified = models.BooleanField(default=False)
    pan_number = models.CharField(max_length=10, null=True, blank=True)
    pan_front = models.URLField(null=True, blank=True)
    driver_license_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    driver_license_front = models.URLField(null=True, blank=True)
    driver_license_back = models.URLField(null=True, blank=True)
    has_driver_license = models.BooleanField()
    account_number = models.CharField(max_length=50, validators=[validate_digits])
    account_name = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=15)
    ref_name = models.CharField(max_length=100, null=True, blank=True)
    passbook_front = models.URLField(null=True, blank=True)
    ref_contact_no = models.BigIntegerField(
        null=True,
        blank=True,
        validators=[Min(1000000000), Max(9999999999)],
    )
    ref_relationship = models.CharField(max_length=100, null=True, blank=True)
    status = models.IntegerField(choices=Status.choices, default=0)
    remarks = models.CharField(max_length=250, null=True, blank=True)
    referred_by = models.BigIntegerField(
        validators=[Min(1000000000), Max(9999999999)],
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.id} | {self.mobile_no}"


class Driver(BaseModel):
    """
    Model to store driver information once onboarding approved
    """
    class Status(models.IntegerChoices):
        ACTIVE = 1, _("Active")
        INACTIVE = 0, _("In Active")

    user = models.OneToOneField(
        User, on_delete=models.PROTECT, null=True, blank=True, editable=False
    )
    onboarding = models.OneToOneField(
        Onboarding, on_delete=models.PROTECT, null=True, blank=True, editable=False
    )
    contract_accepted = models.BooleanField(default=False)
    contract = models.ForeignKey("drivers.DriverContract", on_delete=models.PROTECT, null=True, blank=True)
    doj = models.DateField()
    dol = models.DateField(null=True, blank=True)
    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    remarks = models.CharField(max_length=250, null=True, blank=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
    )
    app_version = models.CharField(max_length=8, null=True, blank=True)
    tracker = FieldTracker()

    @property
    def full_name(self):
        return self.onboarding.full_name
        
    @property
    def dob(self):
        return self.onboarding.dob
        
    @property
    def mobile_no(self):
        return self.onboarding.mobile_no
        
    @property
    def house_no(self):
        return self.onboarding.house_no
        
    @property
    def street(self):
        return self.onboarding.street
        
    @property
    def locality(self):
        return self.onboarding.locality
        
    @property
    def city(self):
        return self.onboarding.city
        
    @property
    def pincode(self):
        return self.onboarding.pincode
        
    @property
    def own_house(self):
        return self.onboarding.own_house
        
    @property
    def aadhar_number(self):
        return self.onboarding.aadhar_number
        
    @property
    def pan_number(self):
        return self.onboarding.pan_number
        
    @property
    def account_number(self):
        return self.onboarding.account_number
        
    @property
    def account_name(self):
        return self.onboarding.account_name
        
    @property
    def ifsc_code(self):
        return self.onboarding.ifsc_code
        

    def clean(self):
        errors = {}
        try:
            driver_age_validator(self.dob)
        except ValidationError as e:
            errors["dob"] = e
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.id} | {self.onboarding.full_name}"


class DriverLocations(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT)
    created_at = models.DateTimeField()
    lat = models.FloatField()
    long = models.FloatField()

    class Meta:
        verbose_name = "Driver Location"
        verbose_name_plural = "Driver Locations"


class DriverAadharDetails(models.Model):
    aadhar_number = models.BigIntegerField()
    data = models.JSONField()
    full_name = models.CharField(max_length=100, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    district = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    po = models.CharField(max_length=50, null=True, blank=True)
    loc = models.CharField(max_length=50, null=True, blank=True)
    vtc = models.CharField(max_length=50, null=True, blank=True)
    subdist = models.CharField(max_length=50, null=True, blank=True)
    street = models.CharField(max_length=50, null=True, blank=True)
    house = models.CharField(max_length=50, null=True, blank=True)
    landmark = models.CharField(max_length=50, null=True, blank=True)
    zip = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        verbose_name = "Driver Aadhar Details"
        verbose_name_plural = "Driver Aadhar Details"


class DriverContract(BaseModel):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    url = models.URLField()

    def __str__(self):
        return f"{self.id} | {self.name}"

    class Meta:
        verbose_name = "Driver Contract"
        verbose_name_plural = "Driver Contracts"


class DriverContractLog(models.Model):
    contract = models.ForeignKey("DriverContract", on_delete=models.PROTECT)
    driver = models.ForeignKey("Driver", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Driver Contract Log"
        verbose_name_plural = "Driver Contract Logs"
