# Generated by Django 4.1 on 2022-08-11 10:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("drivers", "0004_auto_20220705_0046"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="driver",
            options={"ordering": ["-id"]},
        ),
        migrations.AlterModelOptions(
            name="onboarding",
            options={"ordering": ["-id"]},
        ),
        migrations.RemoveField(
            model_name="driveraadhardetails",
            name="email_hash",
        ),
        migrations.RemoveField(
            model_name="driveraadhardetails",
            name="mobile_hash",
        ),
        migrations.RemoveField(
            model_name="onboarding",
            name="pan_back",
        ),
        migrations.AlterField(
            model_name="driver",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="drivercontract",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="onboarding",
            name="house_no",
            field=models.CharField(max_length=15),
        ),
        migrations.AlterField(
            model_name="onboarding",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="onboarding",
            name="locality",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="onboarding",
            name="street",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="onboarding",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
