# Generated by Django 4.1 on 2022-08-19 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0007_auto_20220810_1805"),
    ]

    operations = [
        migrations.AlterField(
            model_name="roster",
            name="address",
            field=models.CharField(max_length=200),
        ),
    ]
