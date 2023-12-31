# Generated by Django 3.2.13 on 2022-06-23 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clients", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="city",
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name="client",
            name="contact_person",
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name="client",
            name="locality",
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name="client",
            name="state",
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name="clientstore",
            name="city",
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name="clientstore",
            name="locality",
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name="clientstore",
            name="state",
            field=models.CharField(max_length=50),
        ),
    ]
