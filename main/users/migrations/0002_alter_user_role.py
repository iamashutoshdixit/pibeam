# Generated by Django 3.2.13 on 2022-08-10 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Driver'), (1, 'Operations Manager'), (2, 'Fleet Manager'), (3, 'Service Manager'), (4, 'Operations Executive')], default=2),
        ),
    ]