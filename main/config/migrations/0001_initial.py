# Generated by Django 3.2.13 on 2022-06-09 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Config",
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
                ("key", models.CharField(max_length=50, unique=True)),
                ("value", models.JSONField()),
            ],
            options={
                "verbose_name": "Config",
                "verbose_name_plural": "Configs",
            },
        ),
    ]
