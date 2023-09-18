# python imports
import logging
# from cerberus import Validator, DocumentError
# django imports
from django.db import models
from django.utils.translation import gettext_lazy as _
# from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator as Max,
    MinValueValidator as Min,
)
from smart_selects.db_fields import ChainedManyToManyField
from model_utils import FieldTracker
# project imports
from libs.models import BaseModel
from fleets.models import Vehicle
from bookings.models import Roster

logger = logging.getLogger(__name__)


class Client(BaseModel):
    """
    model to store client information
    """

    class Status(models.IntegerChoices):
        ACTIVE = 0, _("Active")
        INACTIVE = 1, _("Inactive")
        ON_HOLD = 2, _("On Hold")

    class ServiceType(models.IntegerChoices):
        DRIVER = 0, _("With Driver")
        NO_DRIVER = 1, _("Without Driver")

    def default_pricing_config():
        return {"price_per_trip": 0}
        
    name = models.CharField(max_length=50)
    gst = models.CharField(max_length=15)
    contract = models.URLField()
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    locality = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    contact_person = models.CharField(max_length=50)
    contact_number = models.BigIntegerField(
        validators=[Min(1000000000), Max(9999999999)],
    )
    onboarding_date = models.DateField()
    renewal_date = models.DateField()
    status = models.PositiveSmallIntegerField(
        choices=Status.choices,
    )
    service_type = models.PositiveSmallIntegerField(
        choices=ServiceType.choices,
    )
    updated_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    tracker = FieldTracker()

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"{self.id} | {self.name}"


class ClientContractLog(BaseModel):
    """
    model to store client contract logs
    """
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    old_contract = models.URLField()
    new_contract = models.URLField()
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Client Contract Log"
        verbose_name_plural = "Client Contract Logs"


class ClientStore(BaseModel):
    """
    model to store client store information
    """
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)
    lat = models.FloatField()
    long = models.FloatField()
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    locality = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    contact_number = models.BigIntegerField(
        validators=[Min(1000000000), Max(9999999999)],
    )

    def __str__(self):
        return f"{self.id} | {self.name}"

    class Meta:
        verbose_name = "Client Store"
        verbose_name_plural = "Client Stores"


class Pricing(BaseModel):
    """
    Model for storing the pricing based on clients, type, and vehicle model
    """
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    client_store = ChainedManyToManyField(
        "clients.ClientStore",
        chained_field="client",
        chained_model_field="client",
        horizontal=True,
        blank=True,
    )
    type = models.PositiveSmallIntegerField(
        choices=Roster.TYPE.choices,
        default=Roster.TYPE.LOGISTICS_FIXED,
    )
    model = models.IntegerField(choices=Vehicle.MODEL.choices)
    price = models.FloatField()

    class Meta:
        verbose_name = "Pricing Configuration"
        verbose_name_plural = "Pricing Configurations"
