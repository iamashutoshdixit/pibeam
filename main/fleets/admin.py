# python imports
import logging
# django imports
from django.contrib import admin, messages
from django.shortcuts import render
from django.urls import reverse, path
from django.utils.html import escape, mark_safe
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
# project imports
from libs.mixins import BaseMixin, ExportCSVMixin
from libs.forms import ImportCSVForm
from libs.helpers import S3FileUpload
from services.forms import ServiceForm
from services.models import Service
# app imports
from .forms import (
    VehicleForm,
    BatteryForm,
    ChargerForm,
    GPSTrackerForm,
    VehicleDocumentUploadForm,
)
from .models import (
    Vehicle,
    Station,
    Battery,
    Charger,
    GPSTracker,
)
from .helpers import (
    tracker_import_csv_handler,
    charger_import_csv_handler,
    battery_import_csv_handler,
    station_import_csv_handler,
    vehicle_import_csv_handler,
)

admin.site.site_header = "Fyn Platform"
admin.site.site_title = "Ops Center"
admin.site.index_title = "Ops Center"

logger = logging.getLogger(__name__)


class VehicleAdmin(BaseMixin, ExportCSVMixin):
    list_display = [
        "id",
        "registration_number",
        "model",
        "type",
        "status",
        "station",
        "speed",
        "updated_by",
        "is_active",
    ]
    csv_fields = [
        "registration_number",
        "model",
        "type",
        "status",
        "speed",
        "station.id",
        "station.name",
        "rc_document",
        "insurance_document",
        "insurance_start_date",
        "insurance_renewal_date",
        "chassis_number",
        "dealer.id",
        "dealer.name",
        "financier.id",
        "financier.name",
        "updated_at",
        "updated_by.mobile_no",
        "created_at",
        "is_active",
    ]
    model = Vehicle
    form = VehicleForm
    actions = [
        "upload_documents", 
        "export_selected", 
        "mark_vehicle_for_servicing"
    ]
    search_fields = ["model", "registration_number", "chassis_number"]
    search_help_text = "Registration Number, Model, Chassis Number"
    list_filter = ["is_active", "is_backup", "status", "type", "model", "station__city"]
    readonly_fields = ["status", "rc_document", "insurance_document"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "import-vehicle-csv/",
                self.import_csv,
                name="import_vehicle_csv",
            ),
            path(
                "export-vehicle-csv/",
                self.export_selected,
                name="export_vehicle_csv",
            ),
        ]
        return my_urls + urls

    def upload_documents(self, request, queryset):
        vehicle = queryset.first()
        if "set_status" in request.POST:
            form = VehicleDocumentUploadForm(request.POST)
            if form.is_valid():
                rc_document = request.FILES.get('rc_document')
                insurance_document = request.FILES.get('insurance_document')
                image_upload = S3FileUpload()
                if rc_document is not None:
                    success, rc_document_url = image_upload.upload_file(
                        rc_document, 
                        settings.AWS_CONFIG["S3"]["FOLDERS"]["vehicle-documents"],
                    )
                    if success is False:
                        return messages.add_message(
                            request,
                            messages.ERROR,
                            f"Error while uploading the rc_document. Please try again.",
                        )
                    vehicle.rc_document = rc_document_url
                if insurance_document is not None:
                    success, insurance_document_url = image_upload.upload_file(
                        insurance_document, 
                        settings.AWS_CONFIG["S3"]["FOLDERS"]["vehicle-documents"],
                    )
                    if success is False:
                        return messages.add_message(
                            request,
                            messages.ERROR,
                            f"Error while uploading the insurance_document. Please try again.",
                        )
                    vehicle.insurance_document = insurance_document_url
                vehicle.save()
                messages.add_message(
                    request,
                    messages.INFO,
                    f"Documents uploaded for vehicle {vehicle.registration_number}.",
                )
                logger.info(
                    "Documents uploaded for vehicle {}".format(
                        vehicle.registration_number,
                    )
                )
            return HttpResponseRedirect(".")
        else:
            if queryset.count() > 1:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"please select one vehicle at a time",
                )
                return HttpResponseRedirect(".")
            form = VehicleDocumentUploadForm()

        return render(
            request,
            "services/html/servicing.html",
            {"title": "Vehicle Documents", "objects": queryset, "form": form, "action": "upload_documents"},
        )

    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def mark_vehicle_for_servicing(self, request, queryset):
        vehicle = queryset.first()
        status = Service.STATUS.OPEN
        if "set_status" in request.POST:
            POST = request.POST.copy()
            POST["vehicle"] = vehicle
            POST["status"] = status
            form = ServiceForm(POST, request.FILES)
            if form.is_valid():
                photos = request.FILES.getlist('photos')
                photo_urls = []
                for photo in photos:
                    image_upload = S3FileUpload()
                    success, file_url = image_upload.upload_file(photo, settings.AWS_CONFIG["S3"]["FOLDERS"]["servicing"])
                    if success is True:
                        photo_urls.append(file_url)
                    else:
                        return messages.add_message(
                            request,
                            messages.ERROR,
                            f"Error uploading the image. Please try again.",
                        )

                service = Service(
                    vehicle=form.cleaned_data["vehicle"],
                    status=form.cleaned_data["status"],
                    issue_type=form.cleaned_data["issue_type"],
                    issue_subtype=form.cleaned_data["issue_subtype"],
                    address=form.cleaned_data["address"],
                    latitude=form.cleaned_data["latitude"],
                    longitude=form.cleaned_data["longitude"],
                    description=form.cleaned_data["description"],
                    reportee=form.cleaned_data["reportee"],
                    priority=form.cleaned_data["priority"],
                    photos=photo_urls,
                    created_by=request.user,
                )
                service.save()
                messages.add_message(
                    request,
                    messages.INFO,
                    f"Service record for vehicle {vehicle.registration_number} created",
                )
                logger.info(
                    "service record created for vehicle {}".format(
                        vehicle.registration_number,
                    )
                )
            return HttpResponseRedirect(".")
        else:
            if queryset.count() > 1:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"please select one vehicle at a time",
                )
                return HttpResponseRedirect(".")
            if vehicle.status in [
                Vehicle.STATUS.UNDER_MAINTENANCE.value, 
                Vehicle.STATUS.UNDER_SERVICING.value
            ]:
                messages.add_message(
                    request,
                    messages.ERROR,
                    f"The vehicle is already under service/maintenance.",
                )
                return HttpResponseRedirect(".")
            form = ServiceForm(initial={'vehicle': vehicle, 'status': status})

        return render(
            request,
            "services/html/servicing.html",
            {"title": "Mark Vehicle For Servicing", "objects": queryset, "form": form, "action": "mark_vehicle_for_servicing"},
        )


    def import_csv(self, request):
        if "import_csv" in request.POST:
            form = ImportCSVForm(request.POST, request.FILES)
            if form.is_valid():
                f = request.FILES["file"]
                added, skipped, invalid = vehicle_import_csv_handler(
                    f,
                    request.user,
                )
                if added == -1 and skipped == -1 and invalid == -1:
                    return HttpResponse("Invalid vehicle CSV.")
                messages.add_message(
                    request,
                    messages.INFO,
                    f"{added} entries added. {skipped} skipped.",
                )
                if invalid:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        f"{invalid} invalid entries. Reason:\
                        Duplicate/invalid registration number,\
                        station not found",
                    )
                return HttpResponseRedirect("..")
        else:
            form = ImportCSVForm()

        return render(
            request,
            "fleets/html/import_csv.html",
            {"title": "Choose CSV File", "form": form},
        )


class StationAdmin(BaseMixin, ExportCSVMixin):
    list_display = [
        "id",
        "name",
        "code",
        "city",
        "area",
        "pincode",
        "state",
        "address",
        "lat",
        "long",
        "created_at",
        "updated_at",
        "updated_by",
        "is_active",
    ]
    csv_fields = list_display
    search_fields = ["name", "code", ]
    search_help_text = "Name"
    list_filter = ["is_active", "city", "state"]
    model = Station

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "import-station-csv/",
                self.import_csv,
                name="import_station_csv",
            ),
            path(
                "export-station-csv/",
                self.export_selected,
                name="export_station_csv",
            ),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if "import_csv" in request.POST:
            form = ImportCSVForm(request.POST, request.FILES)
            if form.is_valid():
                f = request.FILES["file"]
                added, skipped = station_import_csv_handler(f, request.user)
                if added == -1 and skipped == -1:
                    return HttpResponse("Invalid Station CSV")
                messages.add_message(
                    request,
                    messages.INFO,
                    f"{added} entries added. {skipped} skipped.",
                )
                return HttpResponseRedirect("..")
        else:
            form = ImportCSVForm()

        return render(
            request,
            "fleets/html/import_csv.html",
            {"title": "Choose CSV File", "form": form},
        )


class BatteryAdmin(BaseMixin, ExportCSVMixin):
    list_display = ["id", "serial_number", "model", "vehicle_str", "vendor_str", "is_active"]
    form = BatteryForm
    list_select_related = ("vehicle",)
    search_fields = ["vehicle__registration_number", "serial_number", "code",]
    search_help_text = "Registration Number, Serial Number, Code"
    list_filter = ["model", "vendor", "is_active"]
    csv_fields = [
        "serial_number",
        "code",
        "model",
        "protocol",
        "chemistry",
        "vehicle.registration_number",
        "is_canbus_enabled",
        "cycle",
        "vendor.id",
        "vendor.name",
        "date_of_purchase",
        "created_at",
        "updated_at",
        "is_active",
    ]
    model = Battery
    autocomplete_fields = ['vehicle', ]

    def vehicle_str(self, obj):
        if obj.vehicle is not None:
            link = reverse("admin:fleets_vehicle_change", args=[obj.vehicle.id])
            return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.vehicle.__str__())}</a>')
        return None
    vehicle_str.short_description = 'Vehicle'

    def vendor_str(self, obj):
        if obj.vendor is not None:
            link = reverse("admin:vendors_vendor_change", args=[obj.vendor.id])
            return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.vendor.__str__())}</a>')
        return None
    vendor_str.short_description = 'Vendor'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "import-battery-csv/",
                self.import_csv,
                name="import_battery_csv",
            ),
            path(
                "export-battery-csv/",
                self.export_selected,
                name="export_battery_csv",
            ),
        ]
        return my_urls + urls
    
    def import_csv(self, request):
        if "import_csv" in request.POST:
            form = ImportCSVForm(request.POST, request.FILES)
            if form.is_valid():
                f = request.FILES["file"]
                added, skipped = battery_import_csv_handler(f, request.user)
                if added == -1 and skipped == -1:
                    return HttpResponse("Invalid Battery CSV")
                messages.add_message(
                    request,
                    messages.INFO,
                    f"{added} entries added. {skipped} skipped.",
                )
                return HttpResponseRedirect("..")
        else:
            form = ImportCSVForm()

        return render(
            request,
            "fleets/html/import_csv.html",
            {"title": "Choose CSV File", "form": form},
        )


class ChargerAdmin(BaseMixin, ExportCSVMixin):
    list_display = [
        "id",
        "serial_number",
        "code",
        "vehicle_str",
        "vendor_str",
        "type",
        "connector",
        "wattage",
        "is_active",
    ]
    form = ChargerForm
    list_select_related = ("vehicle",)
    search_fields = ["vehicle__registration_number", "serial_number", "code",]
    search_help_text = "Registration Number, Serial Number, Code"
    list_filter = ["type", "connector", "wattage", "vendor", "is_active"]
    csv_fields = [
        "serial_number",
        "code",
        "vehicle.registration_number",
        "type",
        "connector",
        "wattage",
        "vendor.id",
        "vendor.name",
        "date_of_purchase",
        "created_at",
        "updated_at",
        "is_active",
    ]
    model = Charger
    autocomplete_fields = ['vehicle', ]

    def vehicle_str(self, obj):
        if obj.vehicle is not None:
            link = reverse("admin:fleets_vehicle_change", args=[obj.vehicle.id])
            return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.vehicle.__str__())}</a>')
        return None
    vehicle_str.short_description = 'Vehicle'

    def vendor_str(self, obj):
        if obj.vendor is not None:
            link = reverse("admin:vendors_vendor_change", args=[obj.vendor.id])
            return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.vendor.__str__())}</a>')
        return None
    vendor_str.short_description = 'Vendor'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "import-charger-csv/",
                self.import_csv,
                name="import_charger_csv",
            ),
            path(
                "export-charger-csv/",
                self.export_selected,
                name="export_charger_csv",
            ),
        ]
        return my_urls + urls
    
    def import_csv(self, request):
        if "import_csv" in request.POST:
            form = ImportCSVForm(request.POST, request.FILES)
            if form.is_valid():
                f = request.FILES["file"]
                added, skipped = charger_import_csv_handler(f, request.user)
                if added == -1 and skipped == -1:
                    return HttpResponse("Invalid Charger CSV")
                messages.add_message(
                    request,
                    messages.INFO,
                    f"{added} entries added. {skipped} skipped.",
                )
                return HttpResponseRedirect("..")
        else:
            form = ImportCSVForm()

        return render(
            request,
            "fleets/html/import_csv.html",
            {"title": "Choose CSV File", "form": form},
        )


class GPSTrackerAdmin(BaseMixin, ExportCSVMixin):
    list_display = ["id", "serial_number", "vehicle_str", "vendor_str", "is_active"]
    form = GPSTrackerForm
    list_select_related = ("vehicle",)
    search_fields = ["vehicle__registration_number", "serial_number"]
    search_help_text = "Registration Number, Serial Number"
    list_filter = ["vendor", "is_active"]
    csv_fields = [
        "serial_number",
        "sim_number",
        "vendor.id",
        "vendor.name",
        "validity",
        "type",
        "vehicle.registration_number",
        "created_at",
        "updated_at",
        "is_active",
    ]
    model = GPSTracker
    autocomplete_fields = ['vehicle', ]

    def vehicle_str(self, obj):
        if obj.vehicle is not None:
            link = reverse("admin:fleets_vehicle_change", args=[obj.vehicle.id])
            return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.vehicle.__str__())}</a>')
        return None
    vehicle_str.short_description = 'Vehicle'

    def vendor_str(self, obj):
        if obj.vendor is not None:
            link = reverse("admin:vendors_vendor_change", args=[obj.vendor.id])
            return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.vendor.__str__())}</a>')
        return None
    vendor_str.short_description = 'Vendor'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "import-tracker-csv/",
                self.import_csv,
                name="import_tracker_csv",
            ),
            path(
                "export-tracker-csv/",
                self.export_selected,
                name="export_tracker_csv",
            ),
        ]
        return my_urls + urls


    def import_csv(self, request):
        if "import_csv" in request.POST:
            form = ImportCSVForm(request.POST, request.FILES)
            if form.is_valid():
                f = request.FILES["file"]
                added, skipped = tracker_import_csv_handler(f, request.user)
                if added == -1 and skipped == -1:
                    return HttpResponse("Invalid Tracker CSV")
                messages.add_message(
                    request,
                    messages.INFO,
                    f"{added} entries added. {skipped} skipped.",
                )
                return HttpResponseRedirect("..")
        else:
            form = ImportCSVForm()

        return render(
            request,
            "fleets/html/import_csv.html",
            {"title": "Choose CSV File", "form": form},
        )


admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(Battery, BatteryAdmin)
admin.site.register(Charger, ChargerAdmin)
admin.site.register(GPSTracker, GPSTrackerAdmin)
