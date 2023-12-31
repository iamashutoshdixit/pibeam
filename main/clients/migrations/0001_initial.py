# Generated by Django 3.2.13 on 2022-06-09 13:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Client",
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
                ("name", models.CharField(max_length=50)),
                ("gst", models.CharField(max_length=15)),
                ("contract", models.URLField()),
                ("address", models.CharField(max_length=100)),
                ("city", models.CharField(max_length=30)),
                ("locality", models.CharField(max_length=30)),
                ("state", models.CharField(max_length=30)),
                ("contact_person", models.CharField(max_length=30)),
                ("contact_number", models.BigIntegerField()),
                ("onboarding_date", models.DateField()),
                ("renewal_date", models.DateField()),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "Active"), (1, "Inactive"), (2, "On Hold")]
                    ),
                ),
                (
                    "service_type",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "With Driver"), (1, "Without Driver")]
                    ),
                ),
                ("pricing_config", models.JSONField()),
            ],
            options={
                "verbose_name": "Client",
                "verbose_name_plural": "Clients",
            },
        ),
        migrations.CreateModel(
            name="ClientStore",
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
                ("name", models.CharField(max_length=50)),
                ("lat", models.FloatField()),
                ("long", models.FloatField()),
                ("address", models.CharField(max_length=100)),
                ("city", models.CharField(max_length=30)),
                ("locality", models.CharField(max_length=30)),
                ("state", models.CharField(max_length=30)),
                ("contact_number", models.BigIntegerField()),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="clients.client"
                    ),
                ),
            ],
            options={
                "verbose_name": "Client Store",
                "verbose_name_plural": "Client Stores",
            },
        ),
    ]
