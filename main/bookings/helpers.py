# python imports
import logging
from datetime import datetime
from django.contrib.admin import SimpleListFilter


# project impotts
from .models import Roster
from drivers.models import Driver
from fleets.models import Vehicle, Station
from clients.models import ClientStore

logger = logging.getLogger(__name__)


class DriverAssignmentFilter(SimpleListFilter):
        title = 'Driver Assignment'
        parameter_name = 'driver'

        def lookups(self, request, model_admin):
            return [('0', 'Without Driver'), ('1', 'With Driver')]

        def queryset(self, request, queryset):
            if self.value() == '1':
                return queryset.filter(driver__isnull=False)
            if self.value() == '0':
                return queryset.filter(driver__isnull=True)

class VehicleAssignmentFilter(SimpleListFilter):
        title = 'Vehicle Assignment'
        parameter_name = 'vehicle'

        def lookups(self, request, model_admin):
            return [('0', 'Without Vehicle'), ('1', 'With Vehicle')]

        def queryset(self, request, queryset):
            if self.value() == '1':
                return queryset.filter(vehicle__isnull=False)
            if self.value() == '0':
                return queryset.filter(vehicle__isnull=True)


def roster_import_csv_handler(file, user):
    """
    Handler for csv roster imports
    """

    clean_data = file.read().decode().strip()
    lines = clean_data.split("\n")
    added, invalid, skipped, no_license = 0, 0, 0, 0
    for lineno, line in enumerate(lines[1:], 1):
        fields = line.split(",")
        try:
            (
                driver,
                vehicle,
                client_store,
                start_date,
                end_date,
                holiday,
                start_time,
                end_time,
                lat,
                long,
                destination_station,
            ) = fields
        except Exception:
            return (-1, -1, -1, -1)
        client_obj = ClientStore.objects.filter(
            name__iexact=client_store
        ).first()
        driver_obj = Driver.objects.filter(
            mobile_no=int(driver),
            is_active=True,
        ).first()
        vehicle_obj = Vehicle.objects.filter(
            registration_number=vehicle,
            is_active=True,
        ).first()
        destination = Station.objects.filter(
            name__iexact=destination_station,
            is_active=True
        ).first()
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        if holiday:
            holiday = [datetime.strptime(day, "%Y-%m-%d").date() for day in holiday.split("|")]
        else: 
            holiday = []
        slot_start = datetime.strptime(start_time, "%I:%M %p").time()
        slot_end = datetime.strptime(end_time, "%I:%M %p").time()
        lat = float(lat)
        long = float(long)
        
        if client_obj and driver_obj and vehicle_obj and destination:
            if (
                Roster.is_valid_vehicle_entry(
                    vehicle_obj, slot_start, slot_end, start_date, end_date
                ) is False and
                Roster.is_valid_driver_entry(
                    driver_obj, slot_start, slot_end, start_date, end_date
                ) is False
            ):
                continue
            if (
                driver_obj.has_driver_license is False and
                vehicle_obj.speed is Vehicle.SPEED.HIGH
            ):
                no_license += 1
                continue
            qs = Roster.objects.filter(
                driver=driver_obj,
                client_store=client_obj,
                vehicle=vehicle_obj,
                start_date=start_date,
                end_date=end_date,
                slot_start_time=slot_start,
                slot_end_time=slot_end,
                destination_station=destination,
            )
            if not qs:
                added += 1
                Roster.objects.create(
                    driver=driver_obj,
                    client_store=client_obj,
                    client=client_obj.client,
                    client_name=client_obj.name,
                    city=client_obj.city,
                    vehicle=vehicle_obj,
                    start_date=start_date,
                    end_date=end_date,
                    holiday=holiday,
                    slot_start_time=slot_start,
                    slot_end_time=slot_end,
                    lat=lat,
                    long=long,
                    address=client_obj.address,
                    destination_station=destination,
                    created_by=user,
                )
            else:
                skipped += 1
        else:
            if not driver_obj:
                logger.error(
                    "{} ERROR invalid driver for roster in line {}".format(
                        datetime.now(),
                        lineno,
                    )
                )
            if not vehicle_obj:
                logger.error(
                    "{} ERROR invalid vehicle for roster in line {}".format(
                        datetime.now(),
                        lineno,
                    )
                )
            if not destination:
                logger.error(
                    "{} ERROR invalid destination in line {}".format(
                        datetime.now(),
                        lineno,
                    )
                )
            invalid += 1
    return (added, skipped, invalid, no_license)
