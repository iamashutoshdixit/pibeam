# Generated by Django 3.2.13 on 2022-12-14 10:34

from django.db import migrations, models
import drivers.models


class Migration(migrations.Migration):

    dependencies = [
        ('drivers', '0009_auto_20221123_1724'),
    ]

    operations = [
        migrations.RenameField(
            model_name='onboarding',
            old_name='c_city',
            new_name='permanent_city',
        ),
        migrations.RenameField(
            model_name='onboarding',
            old_name='c_house_no',
            new_name='permanent_house_no',
        ),
        migrations.RenameField(
            model_name='onboarding',
            old_name='c_locality',
            new_name='permanent_locality',
        ),
        migrations.RenameField(
            model_name='onboarding',
            old_name='c_pin_code',
            new_name='permanent_pin_code',
        ),
        migrations.RenameField(
            model_name='onboarding',
            old_name='c_state',
            new_name='permanent_state',
        ),
        migrations.RenameField(
            model_name='onboarding',
            old_name='c_street',
            new_name='permanent_street',
        ),
        migrations.AlterField(
            model_name='onboarding',
            name='account_number',
            field=models.CharField(max_length=50, validators=[drivers.models.Onboarding.validate_digits]),
        ),
    ]
