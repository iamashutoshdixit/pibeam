# python imports
import logging
# django imports
from django.contrib import admin
from django.urls import reverse
from django.utils.html import escape, mark_safe
# project imports
from libs.mixins import (
    BaseMixin,
    BaseLogMixin, 
    ExportCSVMixin,
)
# app imports
from .models import (
    Service,
    ServiceLog,
)

logger = logging.getLogger(__name__)


class ServiceAdmin(BaseMixin, ExportCSVMixin):
    list_display = [
        "id",
        "get_vehicle_registration_number",
        "status",
        "issue_type",
        "issue_subtype",
        "address",
        "get_google_maps_loc",
        "description",
        "reportee",
        "is_active",
    ]
    csv_fields = [
        "vehicle.registration_number",
        "status",
        "issue_type",
        "issue_subtype",
        "address",
        "latitude",
        "longitude",
        "description",
        "remarks",
        "priority",
        "photos",
        "reportee",
        "created_by",
        "created_at",
        "updated_at",
    ]
    model = Service
    readonly_fields = [
        "vehicle", 
        "issue_type", 
        "issue_subtype",
        "address",
        "latitude",
        "longitude",
        "description",
        "reportee",
        "created_by",
        "created_at",
        "updated_at",
        "service_images",
        "priority",
    ]
    actions = ["change_status", "export_selected"]
    search_fields = ["vehicle__registration_number",]
    search_help_text = "Registration Number, Chassis Number"
    list_filter = ["status", "priority", "vehicle__model", "vehicle__station__city", "issue_type"]
    date_hierarchy = "created_at"
    exclude = ("photos",)

    def get_vehicle_registration_number(self, obj):
        link = reverse("admin:fleets_vehicle_change", args=[obj.vehicle.id])
        return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.vehicle.__str__())}</a>')
    get_vehicle_registration_number.short_description = "Vehicle"

    def get_google_maps_loc(self, obj):
        return mark_safe(
            f'<div>\
                  <a target="_blank" href="http://maps.google.com/maps?q={obj.latitude},{obj.longitude}"> link</a>\
              </div>\
            '
        )
    get_google_maps_loc.short_description = "Location"

    def service_images(self, obj):
        images = ""
        for photo in obj.photos:
            images += f'<img target="_blank" style="margin-right: 1em; max-width: 30%" src="{photo}"/>'
        return mark_safe(
            f'<div>{images}</div>'
        )
    service_images.short_description = "Photos"

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        if obj.status == Service.STATUS.COMPLETED.value:
            obj.is_active = False
        else:
            obj.is_active = True
        super().save_model(request, obj, form, change)


class ServiceLogsAdmin(BaseLogMixin):
    list_display = [
        "id",
        "get_service_id",
        "old_status",
        "new_status",
        "remarks",
        "created_by",
        "created_at",
    ]
    readonly_fields = ServiceLog.get_fields()
    date_hierarchy = "created_at"
    list_filter = ["old_status", "new_status"]
    search_fields = ["service__vehicle__registration_number", "created_by__full_name"]

    def get_service_id(self, obj):
        link = reverse("admin:services_service_change", args=[obj.service.id])
        return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.service.__str__())}</a>')
    get_service_id.short_description = "Service"


admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceLog, ServiceLogsAdmin)