# Generated by Django 3.2.13 on 2022-12-15 12:20

from django.db import migrations, models
import django.db.models.deletion
import fleets.models


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0006_alter_vendor_type'),
        ('fleets', '0008_auto_20221115_2102'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vehicle',
            old_name='vendor',
            new_name='dealer',
        ),
        migrations.RemoveField(
            model_name='battery',
            name='type',
        ),
        migrations.AddField(
            model_name='station',
            name='code',
            field=models.CharField(max_length=7, null=True),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='financier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='financier', to='vendors.vendor'),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='type',
            field=models.IntegerField(choices=[(0, 'L0'), (1, 'L1'), (2, 'L2'), (3, 'L3'), (4, 'L5')], default=1),
        ),
        migrations.AlterField(
            model_name='battery',
            name='code',
            field=models.CharField(default=fleets.models.Battery.code_default, max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='battery',
            name='cycle',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='model',
            field=models.IntegerField(choices=[(0, 'Pimo'), (1, 'Hero Nyx'), (2, 'Hero Lectro'), (3, 'Treo Zor'), (4, 'Log9'), (5, 'Omega Seiki'), (6, 'Altigreen'), (7, 'Exponent')]),
        ),
    ]
