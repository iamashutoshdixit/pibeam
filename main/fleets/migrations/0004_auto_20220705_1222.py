# Generated by Django 3.2.13 on 2022-07-05 06:52

from django.db import migrations, models
import django.db.models.deletion
import fleets.models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0003_auto_20220705_1159'),
        ('fleets', '0003_auto_20220623_1757'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehiclestationlogs',
            old_name='datetime',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='vehiclestationlogs',
            old_name='changed_by',
            new_name='updated_by',
        ),
        migrations.RenameField(
            model_name='vehiclestatuslogs',
            old_name='datetime',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='vehiclestatuslogs',
            old_name='changed_by',
            new_name='updated_by',
        ),
        migrations.AddField(
            model_name='battery',
            name='code',
            field=models.CharField(default=fleets.models.Battery.code_default, max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='battery',
            name='vendor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='vendors.vendor'),
        ),
        migrations.AlterField(
            model_name='gpstracker',
            name='vendor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='vendors.vendor'),
        ),
        migrations.AlterField(
            model_name='station',
            name='address',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='chassis_number',
            field=models.CharField(default=fleets.models.Vehicle.chassis_default, max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='insurance_document',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='insurance_renewal_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='insurance_start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='model',
            field=models.IntegerField(choices=[(0, 'Pimo'), (1, 'Hero Nyx'), (2, 'Hero Lectro'), (3, 'Treo Zor'), (4, 'Log9'), (5, 'Omega Seiko'), (6, 'Altigreen')]),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='rc_document',
            field=models.URLField(blank=True, null=True),
        ),
    ]