# Generated by Django 3.2.13 on 2022-06-09 13:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Driver",
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
                ("full_name", models.CharField(max_length=50)),
                ("dob", models.DateField()),
                (
                    "mobile_no",
                    models.BigIntegerField(
                        unique=True,
                        validators=[
                            django.core.validators.MinValueValidator(1000000000),
                            django.core.validators.MaxValueValidator(9999999999),
                        ],
                    ),
                ),
                ("house_no", models.CharField(max_length=10)),
                ("street", models.CharField(max_length=20)),
                ("locality", models.CharField(max_length=20)),
                ("city", models.CharField(max_length=20)),
                (
                    "pin_code",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(100000),
                            django.core.validators.MaxValueValidator(999999),
                        ]
                    ),
                ),
                ("state", models.CharField(max_length=25)),
                ("own_house", models.BooleanField(default=True)),
                ("photo", models.URLField()),
                ("aadhar_number", models.BigIntegerField(unique=True)),
                ("aadhar_front", models.URLField()),
                ("aadhar_back", models.URLField()),
                ("pan_number", models.CharField(blank=True, max_length=10, null=True)),
                ("pan_front", models.URLField(blank=True, null=True)),
                (
                    "driver_license_number",
                    models.CharField(blank=True, max_length=16, null=True),
                ),
                ("driver_license_front", models.URLField(blank=True, null=True)),
                ("driver_license_back", models.URLField(blank=True, null=True)),
                ("has_driver_license", models.BooleanField()),
                ("contract_accepted", models.BooleanField(default=False)),
                ("account_number", models.BigIntegerField()),
                ("account_name", models.CharField(max_length=30)),
                ("ifsc_code", models.CharField(max_length=15)),
                ("doj", models.DateField()),
                ("dol", models.DateField(blank=True, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="DriverAadharDetails",
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
                ("aadhar_number", models.BigIntegerField()),
                ("data", models.JSONField()),
                ("full_name", models.CharField(blank=True, max_length=100, null=True)),
                ("dob", models.DateField(blank=True, null=True)),
                ("gender", models.CharField(blank=True, max_length=1, null=True)),
                ("country", models.CharField(blank=True, max_length=10, null=True)),
                ("district", models.CharField(blank=True, max_length=30, null=True)),
                ("state", models.CharField(blank=True, max_length=30, null=True)),
                ("po", models.CharField(blank=True, max_length=30, null=True)),
                ("loc", models.CharField(blank=True, max_length=30, null=True)),
                ("vtc", models.CharField(blank=True, max_length=30, null=True)),
                ("subdist", models.CharField(blank=True, max_length=30, null=True)),
                ("street", models.CharField(blank=True, max_length=30, null=True)),
                ("house", models.CharField(blank=True, max_length=30, null=True)),
                ("landmark", models.CharField(blank=True, max_length=30, null=True)),
                ("zip", models.CharField(blank=True, max_length=7, null=True)),
                ("email_hash", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "mobile_hash",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                "verbose_name": "Driver Aadhar Details",
                "verbose_name_plural": "Driver Aadhar Details",
            },
        ),
        migrations.CreateModel(
            name="DriverContract",
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
                ("name", models.CharField(max_length=30)),
                ("description", models.CharField(max_length=100)),
                ("url", models.URLField()),
            ],
            options={
                "verbose_name": "Driver Contract",
                "verbose_name_plural": "Driver Contracts",
            },
        ),
        migrations.CreateModel(
            name="DriverContractLog",
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
                ("timestamp", models.DateTimeField()),
            ],
            options={
                "verbose_name": "Driver Contract Log",
                "verbose_name_plural": "Driver Contract Logs",
            },
        ),
        migrations.CreateModel(
            name="DriverLocations",
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
                ("datetime", models.DateTimeField()),
                ("lat", models.FloatField()),
                ("long", models.FloatField()),
            ],
            options={
                "verbose_name": "Driver Location",
                "verbose_name_plural": "Driver Locations",
            },
        ),
        migrations.CreateModel(
            name="Onboarding",
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
                ("full_name", models.CharField(max_length=50)),
                ("dob", models.DateField()),
                (
                    "mobile_no",
                    models.BigIntegerField(
                        unique=True,
                        validators=[
                            django.core.validators.MinValueValidator(1000000000),
                            django.core.validators.MaxValueValidator(9999999999),
                        ],
                    ),
                ),
                ("house_no", models.CharField(max_length=10)),
                ("street", models.CharField(max_length=20)),
                ("locality", models.CharField(max_length=20)),
                ("city", models.CharField(max_length=20)),
                (
                    "pin_code",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(100000),
                            django.core.validators.MaxValueValidator(999999),
                        ]
                    ),
                ),
                ("state", models.CharField(max_length=25)),
                ("own_house", models.BooleanField(default=True)),
                ("photo", models.URLField()),
                ("aadhar_number", models.BigIntegerField(unique=True)),
                ("aadhar_front", models.URLField()),
                ("aadhar_back", models.URLField()),
                ("aadhar_verified", models.BooleanField(default=False)),
                ("pan_number", models.CharField(blank=True, max_length=10, null=True)),
                ("pan_front", models.URLField(blank=True, null=True)),
                ("pan_back", models.URLField(blank=True, null=True)),
                (
                    "driver_license_number",
                    models.CharField(blank=True, max_length=16, null=True),
                ),
                ("driver_license_front", models.URLField(blank=True, null=True)),
                ("driver_license_back", models.URLField(blank=True, null=True)),
                ("has_driver_license", models.BooleanField()),
                ("account_number", models.BigIntegerField()),
                ("account_name", models.CharField(max_length=30)),
                ("ifsc_code", models.CharField(max_length=15)),
                (
                    "status",
                    models.IntegerField(
                        choices=[
                            (0, "Registered"),
                            (1, "Under Approval"),
                            (2, "Approved"),
                            (3, "Rejected"),
                        ],
                        default=0,
                    ),
                ),
                ("remarks", models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Vendor",
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
                ("name", models.CharField(max_length=10)),
                ("address", models.CharField(max_length=10)),
                ("city", models.CharField(max_length=10)),
                ("locality", models.CharField(max_length=10)),
                ("state", models.CharField(max_length=10)),
                ("contact_person", models.CharField(max_length=10)),
                ("contact_number", models.BigIntegerField()),
                ("gst", models.CharField(max_length=10)),
                ("account_number", models.BigIntegerField()),
                ("account_name", models.CharField(max_length=10)),
                ("ifsc_code", models.CharField(max_length=10)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
