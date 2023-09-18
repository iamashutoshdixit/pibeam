# Generated by Django 4.1 on 2022-08-11 10:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vendors", "0003_auto_20220705_1159"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="vendor",
            options={"ordering": ["-id"]},
        ),
        migrations.AlterField(
            model_name="vendor",
            name="contact_number",
            field=models.BigIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1000000000),
                    django.core.validators.MaxValueValidator(9999999999),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="vendor",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]