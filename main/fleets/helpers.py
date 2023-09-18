# Python imports
import logging
from datetime import datetime
# Django imports
from django.db.utils import IntegrityError
# User imports
from vendors.models import Vendor
from .models import (
    Vehicle, 
    Station, 
    GPSTracker, 
    Battery,
    Charger,
)

logger = logging.getLogger(__name__)


def vehicle_import_csv_handler(file, user=None):
    clean_data = file.read().decode().strip()
    lines = clean_data.split("\n")
    added, invalid, skipped = 0, 0, 0
    status_list = dict((s.label.lower(), s.value) for s in Vehicle.STATUS)
    model_list = dict((m.label.lower(), m.value) for m in Vehicle.MODEL)
    for line in lines[1:]:
        fields = line.split(",")
        try:
            (
                registration_number,
                model,
                type,
                status,
                speed,
                station,
                insurance_start_date,
                insurance_renewal_date,
                chassis_number,
                engine_number,
                dealer,
                financier,
                is_active,
            ) = fields
        except ValueError as e:
            logger.error(f"{datetime.now()} wrong csv uploaded for vehicles")
            return (-1, -1, -1)
        speed = 1 if speed.lower() == "low" else 2
        if not Vehicle.valid_registration(registration_number, speed):
            logger.error(f"{datetime.now()} wrong format for vehicle {registration_number}")
            invalid += 1
            continue
        model = model_list.get(model.lower())
        status = status_list.get(status.lower())
        station_obj = Station.objects.filter(
            name__iexact=station.strip(),
        ).first()
        is_active = True if is_active.replace("\r", "").lower() == "true" else False
        dealer_obj = None
        if dealer:
            dealer_obj = Vendor.objects.filter(id=dealer, type=Vendor.TYPE.VEHICLE)
        financier_obj = None
        if financier:
            financier_obj = Vendor.objects.filter(id=financier, type=Vendor.TYPE.VEHICLE)
        if not station_obj:
            logger.error(
                "{} station not found for vehicle {}".format(
                    datetime.now(),
                    registration_number,
                )
            )
            invalid += 1
            continue
        elif station_obj.is_active is False:
            logger.error(
                "{} station is inactive {}".format(
                    datetime.now(),
                    registration_number,
                )
            )
            invalid += 1
            continue
        try:
            __, created = Vehicle.objects.get_or_create(
                registration_number=registration_number,
                defaults={
                    "model":model,
                    "type":getattr(Vehicle.TYPE, type),
                    "speed": speed,
                    "status": status,
                    "station": station_obj,
                    "engine_number": engine_number,
                    "insurance_start_date": insurance_start_date or None,
                    "insurance_renewal_date": insurance_renewal_date or None,
                    "chassis_number": chassis_number,
                    "dealer": dealer_obj,
                    "financier": financier_obj,
                    "is_active": is_active,
                    "updated_by": user,
                },
            )
            if created:
                logger.info(f"{datetime.now()} vehicle {registration_number} created.")
                added += 1
            else:
                logger.info(
                    f"{datetime.now()} vehicle with registration number\
                         {registration_number} already exists. skipped."
                )
                skipped += 1
        except IntegrityError:
            logger.error(
                "{} multiple vehicles\
                     with conflicting registration number {}".format(
                    datetime.now(),
                    registration_number,
                )
            )
            invalid += 1
            continue
    return (added, skipped, invalid)


def station_import_csv_handler(file, user=None):
    clean_data = file.read().decode().strip()
    lines = clean_data.split("\n")
    added, skipped = 0, 0
    for line in lines[1:]:
        fields = line.split(",")
        try:
            name, city, area, pincode, state, address, lat, long, is_active = fields
        except ValueError:
            logger.error(f"{datetime.now()} wrong csv uploaded for stations.")
            return (-1, -1)
        pincode = int(pincode)
        is_active = True if is_active.lower() == "true" else False
        lat = float(lat)
        long = float(long)
        __, created = Station.objects.get_or_create(
            name=name,
            lat=lat,
            long=long,
            defaults={
                "city":city,
                "area":area,
                "address":address,
                "state":state,
                "pincode":pincode,
                "is_active":is_active,
            },
        )
        if created:
            logger.info(f"{datetime.now()} station {name} created.")
            added += 1
        else:
            logger.info(
                "{} station {} already exists. skipped.".format(
                    datetime.now(),
                    name,
                )
            )
            skipped += 1
    return (added, skipped)

def battery_import_csv_handler(file, user=None):
    clean_data = file.read().decode().strip()
    lines = clean_data.split("\n")
    added, skipped = 0, 0
    for line in lines[1:]:
        fields = line.split(",")
        try:
            (
                serial_number,
                model,
                protocol,
                chemistry,
                vehicle,
                is_canbus_enabled,
                cycle,
                vendor,
                date_of_purchase,
                is_active,
            ) = fields
        except ValueError:
            logger.error(f"{datetime.now()} wrong csv uploaded for batteries.")
            return (-1, -1)
        try:
            if vendor != '':
                vendor = Vendor.objects.get(id=vendor, type=Vendor.TYPE.BATTERY)
            else:
                vendor = None
        except Vendor.DoesNotExist:
            logger.info(f"{datetime.now()} vendor doesn't exist.")
            skipped += 1
            continue

        try:
            vehicle = Vehicle.objects.get(registration_number=vehicle)
        except Vehicle.DoesNotExist:
            logger.info(f"{datetime.now()} vehicle doesn't exist.")
            skipped += 1
            continue
        is_canbus_enabled = True if is_canbus_enabled.lower() == "true" else False
        if date_of_purchase == '':
            date_of_purchase = None
        else:
            date_of_purchase = datetime.strptime(date_of_purchase, "%d/%m/%Y").date()
        is_active = True if is_active.replace("\r", "").lower() == "true" else False
        __, created = Battery.objects.get_or_create(
            serial_number=serial_number,
            defaults={
                "model":model,
                "protocol":protocol,
                "chemistry":chemistry,
                "cycle":cycle,
                "vendor":vendor,
                "date_of_purchase":date_of_purchase,
                "vehicle":vehicle,
                "is_canbus_enabled":is_canbus_enabled,
                "is_active":is_active,
            },
        )
        if created:
            logger.info(f"{datetime.now()} battery {serial_number} created.")
            added += 1
        else:
            logger.info(
                "{} battery {} already exists. skipped.".format(
                    datetime.now(),
                    serial_number,
                )
            )
            skipped += 1
    return (added, skipped)


def charger_import_csv_handler(file, user=None):
    clean_data = file.read().decode().strip()
    lines = clean_data.split("\n")
    added, skipped = 0, 0
    for line in lines[1:]:
        fields = line.split(",")
        try:
            (
                serial_number,
                type,
                connector,
                wattage,
                vehicle,
                vendor,
                date_of_purchase,
                is_active,
            ) = fields
        except ValueError:
            logger.error(f"{datetime.now()} wrong csv uploaded for batteries.")
            return (-1, -1)
        try:
            if vendor != '':
                vendor = Vendor.objects.get(id=vendor, type=Vendor.TYPE.CHARGER)
            else:
                vendor = None
        except Vendor.DoesNotExist:
            logger.info(f"{datetime.now()} vendor doesn't exist.")
            skipped += 1
            continue

        try:
            vehicle = Vehicle.objects.get(registration_number=vehicle)
        except Vehicle.DoesNotExist:
            logger.info(f"{datetime.now()} vehicle doesn't exist.")
            skipped += 1
            continue
        is_canbus_enabled = True if is_canbus_enabled.lower() == "true" else False
        date_of_purchase = datetime.strptime(date_of_purchase, "%d/%m/%Y").date()
        is_active = True if is_active.replace("\r", "").lower() == "true" else False
        __, created = Charger.objects.get_or_create(
            serial_number=serial_number,
            defaults={
                "type":type,
                "connector":connector,
                "wattage":wattage,
                "vendor":vendor,
                "date_of_purchase":date_of_purchase,
                "vehicle":vehicle,
                "is_active":is_active,
            },
        )
        if created:
            logger.info(f"{datetime.now()} charger {serial_number} created.")
            added += 1
        else:
            logger.info(
                "{} charger {} already exists. skipped.".format(
                    datetime.now(),
                    serial_number,
                )
            )
            skipped += 1
    return (added, skipped)


def tracker_import_csv_handler(file, user=None):
    clean_data = file.read().decode().strip()
    lines = clean_data.split("\n")
    added, skipped = 0, 0
    for line in lines[1:]:
        fields = line.split(",")
        try:
            serial_number, sim_number, vendor, validity, type, vehicle, is_active = fields
        except ValueError:
            logger.error(f"{datetime.now()} wrong csv uploaded for stations.")
            return (-1, -1)
        is_active = True if is_active.lower() == "true" else False
        try:
            if vendor != '':
                vendor = Vendor.objects.get(id=vendor, type=Vendor.TYPE.GPS_TRACKER)
            else:
                vendor = None
        except Vendor.DoesNotExist:
            logger.info(f"{datetime.now()} vendor doesn't exist.")
            skipped += 1
            continue

        try:
            vehicle = Vehicle.objects.get(registration_number=vehicle)
        except Vehicle.DoesNotExist:
            logger.info(f"{datetime.now()} vehicle doesn't exist.")
            skipped += 1
            continue

        validity = datetime.strptime(validity, "%d/%m/%Y").date()

        __, created = GPSTracker.objects.get_or_create(
            serial_number=serial_number,
            sim_number=int(sim_number),
            defaults={
                "vendor":vendor,
                "validity":validity,
                "type":type,
                "vehicle":vehicle,
                "is_active":is_active,
            },
        )
        if created:
            logger.info(f"{datetime.now()} tracker {serial_number} created.")
            added += 1
        else:
            logger.info(
                "{} tracker {} already exists. skipped.".format(
                    datetime.now(),
                    serial_number,
                )
            )
            skipped += 1
    return (added, skipped)
