# Generated by Django 3.2.13 on 2022-08-10 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0006_alter_roster_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='roster',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='trip',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
