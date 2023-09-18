# Django imports
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from model_utils import FieldTracker
# User imports
from libs.models import BaseModel


class Service(BaseModel):
    """
    Model to store vehicle details
    """

    class STATUS(models.IntegerChoices):
        OPEN = 0, _("Open")
        IN_PROGRESS = 1, _("In Progress")
        ON_HOLD = 2, _("On Hold")
        COMPLETED = 3, _("Completed")

    class ISSUE_TYPE(models.IntegerChoices):
        OTHER_ISSUE = 0, _("Other Issue")
        ELECTRICAL = 1, _("Electrical")
        MECHANICAL = 2, _("Mechanical")

    class PRIORITY(models.IntegerChoices):
        MEDIUM = 0, _("Medium")
        HIGH = 1, _("High")

    vehicle = models.ForeignKey(
        "fleets.Vehicle",
        on_delete=models.PROTECT,
    )
    status = models.IntegerField(choices=STATUS.choices)
    issue_type = models.IntegerField(choices=ISSUE_TYPE.choices)
    issue_subtype = models.CharField(max_length=50)
    address = models.CharField(max_length=250)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    description = models.CharField(max_length=250)
    remarks = models.CharField(max_length=250, null=True, blank=True)
    priority = models.IntegerField(choices=PRIORITY.choices)
    photos = ArrayField(models.URLField(), null=True, blank=True)
    reportee = models.ForeignKey(
        "users.User", 
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="servicing_reportee",
    )
    created_by = models.ForeignKey(
        "users.User", 
        on_delete=models.PROTECT,
        related_name="servicing_created_by",
    )
    tracker = FieldTracker()


    class Meta:
        verbose_name = "Vehicle Service"
        verbose_name_plural = "Vehicle Services"

    def __str__(self):
        return f"{self.id} | {self.vehicle.registration_number}"

    def clean(self):
        if self.id is not None and self.status == Service.STATUS.OPEN.value:
            raise ValidationError(_("Cannot move to OPEN status from the current state"), code="invalid")

class ServiceLog(models.Model):
    service = models.ForeignKey(
        "services.Service",
        on_delete=models.PROTECT,
    )
    old_status = models.IntegerField(choices=Service.STATUS.choices)
    new_status = models.IntegerField(choices=Service.STATUS.choices)
    remarks = models.CharField(max_length=250, null=True, blank=True)
    created_by = models.ForeignKey(
        "users.User", 
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vehicle Service Log"
        verbose_name_plural = "Vehicle Service Logs"

    @classmethod
    def get_fields(cls):
        return [field.name for field in cls._meta.get_fields()]