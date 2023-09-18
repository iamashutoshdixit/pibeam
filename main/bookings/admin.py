# python imports
from datetime import datetime
# django imports
from django.contrib import admin, messages
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.urls import reverse, path
from django.utils.html import escape, mark_safe
from django.forms.models import model_to_dict
from rangefilter.filters import DateRangeFilter
from django.utils.html import mark_safe
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
# project imports
from libs.mixins import BaseMixin, BaseLogMixin, ExportCSVMixin
from libs.forms import ImportCSVForm
# app imports
from .models import (
    Roster, 
    Trip,
    RosterDriverLog, 
    RosterVehicleLog, 
)
from .forms import (
    ChangeRosterStatus,
    ChangeTripStatus,
)
from .helpers import (
    roster_import_csv_handler,
    DriverAssignmentFilter,
    VehicleAssignmentFilter,
)


class RosterAdmin(BaseMixin, ExportCSVMixin):
    list_display = [
        "id",
        "type",
        "driver_str",
        "vehicle_str",
        "client_store_str",
        "city",
        "start_date",
        "end_date",
        "slot_start_time",
        "slot_end_time",
        "status",
        "created_by",
    ]
    list_select_related = ("vehicle",)
    list_filter = [
        "status",
        "type",
        "city",
        "vehicle__model",
        "vehicle__type",
        DriverAssignmentFilter,
        VehicleAssignmentFilter,
    ]
    autocomplete_fields = ['client', 'vehicle', 'driver', 'destination_station', ]
    search_fields = [
        "driver__onboarding__mobile_no",
        "vehicle__registration_number",
        "client__name",
    ]
    search_help_text = "Driver Mobile No, Registraion Number, Client Name"
    model = Roster
    csv_fields = [
        "client.id",
        "client.name",
        "client_store.id",
        "client_store.name",
        "city",
        "driver.onboarding.mobile_no",
        "type",
        "vehicle.registration_number",
        "start_date",
        "end_date",
        "holiday",
        "slot_start_time",
        "slot_end_time",
        "lat",
        "long",
        "address",
        "destination_station.id",
        "destination_station.name",
        "created_by.username",
        "created_at",
        "updated_at",
        "is_active",
    ]
    actions = ["export_selected", "change_status"]
    readonly_fields = ["is_active", "remarks"]

    def vehicle_str(self, obj):
        if obj.vehicle is not None:
            link = reverse("admin:fleets_vehicle_change", args=[obj.vehicle.id])
            return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.vehicle.__str__())}</a>')
        return None
    vehicle_str.short_description = 'Vehicle'

    def driver_str(self, obj):
        if obj.driver is not None:
            link = reverse("admin:drivers_driver_change", args=[obj.driver.id])
            return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.driver.__str__())}</a>')
        return None
    driver_str.short_description = 'Driver'

    def client_store_str(self, obj):
        if obj.client_store is not None:
            link = reverse("admin:clients_clientstore_change", args=[obj.client_store.id])
            return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.client_store.__str__())}</a>')
        return None
    client_store_str.short_description = 'Client Store'


    def save_model(self, request, obj, form, change):
        # for the history table
        obj.created_by = request.user    
        obj.client_name = obj.client_store.name
        obj.city = obj.client_store.city
        obj.lat = obj.client_store.lat
        obj.long = obj.client_store.long
        obj.address = obj.client_store.address + ", " + obj.client_store.city + ", " + obj.client_store.state
        if change is True:
            new = model_to_dict(obj)
            old = form.initial
            changed = ["{0}: {1} -> {2}".format(key, old[key], new[key]) for key in old if old[key] != new[key]]
            message = "Fields Changed " + ", ".join(changed)
            self.log_change(request, obj, message=message)
        super().save_model(request, obj, form, change)

    def log_change(self, request, object, message):
        """
        Override the default log entry for changes
        """
        if isinstance(message, str) and message.startswith("Fields"):
            super().log_change(request, object, message)
        return False

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "import-roster-csv/",
                self.import_csv,
                name="import_roster_csv",
            ),
            path(
                "export-roster-csv/",
                self.export_selected,
                name="export_roster_csv",
            ),
        ]
        return my_urls + urls

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        statuses = Roster.STATUS.choices
        remove_statuses = [(2, "Attrition"), (3, 'Service'), ]
        statuses = list(set(statuses) - set(remove_statuses))
        if db_field.name == 'status':
            kwargs['choices'] = statuses
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        """
         To show only the active vehicles in the dropdown
        """
        form = super().get_form(request, obj, **kwargs)
        try:
            # remove add / edit / remove actions for drivers
            field = form.base_fields["driver"]
            field.widget.can_add_related = False
            field.widget.can_change_related = False
            field.widget.can_delete_related = False
        except KeyError:
            pass
        return form
   
    def import_csv(self, request):
        if "import_csv" in request.POST:
            form = ImportCSVForm(request.POST, request.FILES)
            if form.is_valid():
                f = request.FILES["file"]
                (
                    added,
                    skipped,
                    invalid,
                    no_license,
                ) = roster_import_csv_handler(f, request.user)
                if added == -1 and skipped == -1 and invalid == -1:
                    return HttpResponse("Invalid roster csv.")
                messages.add_message(
                    request,
                    messages.INFO,
                    f"{added} entries added. {skipped} skipped.",
                )
                if no_license > 0:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        f"{no_license} entries skippped.\
                        Cannot assign high speed vehicle to driver\
                        without driver license.",
                    )
                if invalid > 0:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        f"{invalid} invalid entries.\
                        Driver or vehicle not found.",
                    )
                return HttpResponseRedirect("..")
        else:
            form = ImportCSVForm()

        return render(
            request,
            "drivers/html/import_csv.html",
            {"title": "Choose CSV File", "form": form},
        )

    def change_status(self, request, queryset):
        """
        change status of roster
        """
        if "set_status" in request.POST:
            form = ChangeRosterStatus(request.POST)
            if form.is_valid():
                status = form.cleaned_data["status"]
                remarks = form.cleaned_data["remarks"]
                if queryset.count() > 1:
                    return HttpResponse(
                        "please select one roster at a time"
                    )
                if status == "0" and not remarks:
                    return HttpResponse("remarks required if marked inactive")
                
                obj = queryset.last()
                if status == "0":
                    obj.status = Roster.STATUS.IN_ACTIVE
                    obj.is_active = False 
                    obj.remarks = remarks
                    obj.created_by = request.user
                    obj.save()
                if status == "1":
                    # do necessary checks before marking a roster active
                    try: 
                        obj.clean()
                    except Exception as e:
                        messages.add_message(
                            request,
                            messages.ERROR,
                            e.message,
                        )
                        return HttpResponseRedirect(".")
                    obj.status = Roster.STATUS.ACTIVE
                    obj.is_active = True
                    obj.remarks = remarks
                    obj.created_by = request.user
                    obj.save()
                if status == "2":
                    # mark the roster as attrition
                    if obj.driver is not None:
                        # deactivate the driver-user
                        obj.driver.is_active = False
                        obj.driver.dol = datetime.now().date()
                        obj.driver.save()
                        obj.driver = None
                    if obj.vehicle is not None:
                        obj.vehicle = None
                    obj.status = Roster.STATUS.ATTRITION
                    obj.created_by = request.user
                    obj.save()
                # update the LogEntry for history
                message = f"Status has been\
                    marked - {Roster.STATUS(int(status)).name} with\
                    the following remarks - {remarks}"
                ctype = ContentType.objects.get_for_model(Roster)
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ctype.id,
                    object_id=obj.id,
                    object_repr=str(obj),
                    change_message=message,
                    action_flag=CHANGE,
                )
                messages.add_message(
                    request,
                    messages.INFO,
                    f"Status has been marked - {Roster.STATUS(int(status)).name} for the Roster {obj.id}",
                )
                return HttpResponseRedirect(".")
        else:
            form = ChangeRosterStatus()

        return render(
            request,
            "drivers/html/change_status.html",
            {"title": "Choose status", "objects": queryset, "form": form},
        )


class TripAdmin(BaseMixin, ExportCSVMixin):

    list_display = [
        "id",
        "get_roster_client_store",
        "get_roster_driver",
        "get_roster_vehicle",
        "get_roster_city",
        "status",
        "get_roster_start_time",
        "get_roster_end_time",
        "created_at",
        "checkin_time",
        "checkout_time",
        "ended_at",
        "is_active",
    ]
    list_select_related = ("roster",)
    list_filter = [
        "is_active",
        "roster__city",
        "status",
        ("checkin_time", DateRangeFilter),
        ("checkout_time", DateRangeFilter),
    ]
    csv_fields = [
        "id",
        "roster.driver.mobile_no",
        "roster.vehicle.registration_number",
        "roster.client.city",
        "roster.id",
        "created_at",
        "checkin_time",
        "checkout_time",
        "ended_at",
        "in_latitude",
        "in_longitude",
        "out_latitude",
        "out_longitude",
        "start_km",
        "end_km",
        "trip_sheet_photo",
        "updated_at",
        "is_active",
    ]
    date_hierarchy = 'created_at'
    model = Trip
    actions = ["export_selected", "change_status"]
    search_fields = [
        "roster__driver__onboarding__mobile_no",
        "roster__vehicle__registration_number",
        "roster__client__name",
        "roster__client_store__name",
    ]
    search_help_text = "Driver Mobile No, Registraion Number, Client Name, Client Store Name"

    def get_roster_start_time(self, obj):
        return obj.roster.slot_start_time
    get_roster_start_time.short_description = "Slot Start Time"

    def get_roster_end_time(self, obj):
        return obj.roster.slot_end_time
    get_roster_end_time.short_description = "Slot End Time"
    
    def get_roster_client_store(self, obj):
        link = reverse("admin:clients_clientstore_change", args=[obj.roster.client_store.id])
        return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.roster.client_store.__str__())}</a>')
    get_roster_client_store.short_description = "Client Store"

    def get_roster_city(self, obj):
        return obj.roster.city
    get_roster_city.short_description = "City"

    def get_roster_driver(self, obj):
        if obj.roster.driver is not None:
            link = reverse("admin:drivers_driver_change", args=[obj.roster.driver.id])
            return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.roster.driver.__str__())}</a>')
        return None
    get_roster_driver.short_description = "Driver"

    def get_roster_vehicle(self, obj):
        if obj.roster.vehicle is not None:
            link = reverse("admin:fleets_vehicle_change", args=[obj.roster.vehicle.id])
            return mark_safe(f'<a style="white-space: nowrap;" href="{link}">{escape(obj.roster.vehicle.__str__())}</a>')
        return None
    get_roster_vehicle.short_description = "Vehicle"

    def vehicle_image(self, obj=None):
        """
        return vehicle images
        """
        if len(obj.vehicle_photos) > 0:
            for photo in obj.vehicle_photos:
                return mark_safe(
                    f'<div>\
                        <img style="margin-right: 1em; max-width: 30%" \
                            src="{photo}"/>\
                    </div>\
                    '
                )
        return None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "export-trip-csv/",
                self.export_selected,
                name="export_trip_csv",
            ),
        ]
        return my_urls + urls
    
    def change_status(self, request, queryset):
        """
        change status of onboarding
        """
        if "set_status" in request.POST:
            form = ChangeTripStatus(request.POST)
            if form.is_valid():
                status = form.cleaned_data["status"]
                for obj in queryset:
                    obj.is_active = bool(int(status))
                    obj.save()
                    # update the LogEntry for history
                    message = f"Status has been\
                        marked - {Roster.STATUS(int(status)).name}"
                    ctype = ContentType.objects.get_for_model(Trip)
                    LogEntry.objects.log_action(
                        user_id=request.user.id,
                        content_type_id=ctype.id,
                        object_id=obj.id,
                        object_repr=str(obj),
                        change_message=message,
                        action_flag=CHANGE,
                    )
                    messages.add_message(
                        request,
                        messages.INFO,
                        f"{queryset.count()} records has been marked - {Roster.STATUS(int(status)).name}",
                    )
                return HttpResponseRedirect(".")
        else:
            form = ChangeTripStatus()

        return render(
            request,
            "drivers/html/change_status.html",
            {"title": "Choose status", "objects": queryset, "form": form},
        )


class RosterDriverLogAdmin(BaseLogMixin):
    list_display = [
        "id",
        "roster",
        "old_driver",
        "new_driver",
        "status",
        "created_by",
        "created_at",
    ]
    list_filter = [
        "status",
    ]
    model = RosterDriverLog
    search_fields = ["roster__id, roster__driver__mobile_no"]
    search_help_text = "Driver Mobile Number, Roster ID"
    date_hierarchy = 'created_at'
    actions = ["export_selected"]
    csv_fields = [
        "id",
        "roster.id",
        "old_driver.full_name",
        "old_driver.mobile_no",
        "new_driver.full_name",
        "new_driver.mobile_no",
        "status",
        "created_by",
        "created_at",
    ]


class RosterVehicleLogAdmin(BaseLogMixin):
    list_display = [
        "id",
        "roster",
        "old_vehicle",
        "new_vehicle",
        "status",
        "created_by",
        "created_at",
    ]
    list_filter = [
        "status",
    ]
    model = RosterVehicleLog
    search_fields = ["roster__id", "roster__vehicle__registration_number"]
    search_help_text = "Vehicle Registration Number, Roster ID"
    date_hierarchy = 'created_at'
    actions = ["export_selected"]
    csv_fields = [
        "id",
        "roster.id",
        "old_vehicle.registration_number",
        "new_vehicle.registration_number",
        "status",
        "created_by",
        "created_at",
    ]


admin.site.register(Trip, TripAdmin)
admin.site.register(Roster, RosterAdmin)
admin.site.register(RosterDriverLog, RosterDriverLogAdmin)
admin.site.register(RosterVehicleLog, RosterVehicleLogAdmin)
