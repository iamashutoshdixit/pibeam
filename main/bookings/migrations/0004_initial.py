# Generated by Django 3.2.13 on 2022-06-09 13:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("bookings", "0003_initial"),
        ("drivers", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("fleets", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="roster",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="roster",
            name="destination_station",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="fleets.station"
            ),
        ),
        migrations.AddField(
            model_name="roster",
            name="driver",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="drivers.driver"
            ),
        ),
        migrations.AddField(
            model_name="roster",
            name="vehicle",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="fleets.vehicle"
            ),
        ),
    ]
