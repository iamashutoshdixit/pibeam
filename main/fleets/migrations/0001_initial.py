# Generated by Django 3.2.13 on 2022-06-09 13:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Battery",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("serial_number", models.CharField(max_length=20, unique=True)),
                ("model", models.CharField(max_length=50)),
                ("type", models.CharField(max_length=50)),
                ("protocol", models.CharField(max_length=50)),
                ("chemistry", models.CharField(max_length=50)),
                ("is_canbus_enabled", models.BooleanField()),
                ("cycle", models.IntegerField()),
                ("vendor", models.CharField(max_length=50)),
                ("date_of_purchase", models.DateField()),
            ],
            options={
                "verbose_name": "Battery",
                "verbose_name_plural": "Batteries",
            },
        ),
        migrations.CreateModel(
            name="GPSTracker",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("serial_number", models.CharField(max_length=20)),
                ("sim_number", models.IntegerField()),
                ("vendor", models.CharField(max_length=50)),
                ("validity", models.DateField()),
                ("type", models.CharField(max_length=50)),
            ],
            options={
                "verbose_name": "GPS Tracker",
                "verbose_name_plural": "GPS Trackers",
            },
        ),
        migrations.CreateModel(
            name="Station",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=20)),
                ("city", models.CharField(max_length=20)),
                ("state", models.CharField(max_length=20)),
                ("address", models.CharField(max_length=20)),
                ("area", models.CharField(max_length=20)),
                (
                    "pin_code",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MaxValueValidator(999999),
                            django.core.validators.MinValueValidator(100000),
                        ]
                    ),
                ),
                ("lat", models.FloatField()),
                ("long", models.FloatField()),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Vehicle",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("registration_number", models.CharField(max_length=20, unique=True)),
                (
                    "model",
                    models.IntegerField(
                        choices=[
                            (0, "Pimo"),
                            (1, "Hero Nyx"),
                            (2, "Hero Lectro"),
                            (3, "Treo Zor"),
                        ]
                    ),
                ),
                (
                    "status",
                    models.IntegerField(
                        choices=[
                            (0, "Available for Booking"),
                            (1, "Under Booking"),
                            (2, "Under Maintenance"),
                            (3, "Under Servicing"),
                        ]
                    ),
                ),
                ("city", models.CharField(max_length=20)),
                ("speed", models.IntegerField(choices=[(1, "Low"), (2, "High")])),
                ("rc_document", models.URLField(null=True)),
                ("insurance_document", models.URLField(null=True)),
                ("insurance_start_date", models.DateField(null=True)),
                ("insurance_renewal_date", models.DateField(null=True)),
                (
                    "chassis_number",
                    models.CharField(max_length=20, null=True, unique=True),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="VehicleStationLogs",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("datetime", models.DateTimeField(editable=False)),
            ],
            options={
                "verbose_name": "Vehicle Station Log",
                "verbose_name_plural": "Vehicle Station Logs",
            },
        ),
        migrations.CreateModel(
            name="VehicleStatusLogs",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("old_status", models.CharField(max_length=25)),
                ("new_status", models.CharField(max_length=25)),
                ("datetime", models.DateTimeField(editable=False)),
            ],
            options={
                "verbose_name": "Vehicle Status Logs",
                "verbose_name_plural": "Vehicle Status Logs",
            },
        ),
    ]