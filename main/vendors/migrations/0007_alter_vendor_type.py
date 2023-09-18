# Generated by Django 3.2.13 on 2022-12-22 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0006_alter_vendor_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='type',
            field=models.IntegerField(choices=[(0, 'Driver'), (1, 'GPS Tracker'), (2, 'Battery'), (3, 'Vehicle'), (4, 'Charging Station'), (5, 'Parking Lot'), (6, 'Finance'), (7, 'Charger')], null=True),
        ),
    ]
