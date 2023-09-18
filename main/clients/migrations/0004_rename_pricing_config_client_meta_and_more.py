# Generated by Django 4.1 on 2022-08-11 10:34

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clients", "0003_auto_20220704_1704"),
    ]

    operations = [
        migrations.RenameField(
            model_name="client",
            old_name="pricing_config",
            new_name="meta",
        ),
        migrations.AlterField(
            model_name="client",
            name="contact_number",
            field=models.BigIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1000000000),
                    django.core.validators.MaxValueValidator(9999999999),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="client",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="clientstore",
            name="contact_number",
            field=models.BigIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1000000000),
                    django.core.validators.MaxValueValidator(9999999999),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="clientstore",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
