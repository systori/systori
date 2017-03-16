# Generated by Django 2.0 on 2017-03-14 00:57

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
        ('equipment', '0004_auto_20170313_2228'),
        ('company', '0010_auto_20170314_0153'),
        ('task', '0008_auto_20170228_1545'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpendReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('comment', models.TextField()),
                ('expended', models.DecimalField(decimal_places=4, default=Decimal('0.00'), max_digits=14, verbose_name='Expended')),
            ],
            options={
                'ordering': ('-timestamp',),
                'verbose_name_plural': 'Expend Reports',
                'verbose_name': 'Expend Report',
            },
        ),
        migrations.RemoveField(
            model_name='progressattachment',
            name='report',
        ),
        migrations.RemoveField(
            model_name='job',
            name='billing_method',
        ),
        migrations.RemoveField(
            model_name='lineitem',
            name='complete',
        ),
        migrations.RemoveField(
            model_name='lineitem',
            name='is_correction',
        ),
        migrations.RemoveField(
            model_name='lineitem',
            name='is_flagged',
        ),
        migrations.AddField(
            model_name='lineitem',
            name='equipment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lineitems', to='equipment.EquipmentType'),
        ),
        migrations.AddField(
            model_name='lineitem',
            name='expended',
            field=models.DecimalField(decimal_places=4, default=Decimal('0.00'), max_digits=14, verbose_name='Expended'),
        ),
        migrations.AddField(
            model_name='lineitem',
            name='labor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lineitems', to='company.LaborType'),
        ),
        migrations.AddField(
            model_name='lineitem',
            name='lineitem_type',
            field=models.CharField(choices=[('labor', 'Labor'), ('material', 'Material'), ('equipment', 'Equipment'), ('other', 'Other')], default='other', max_length=128, verbose_name='Line Item Type'),
        ),
        migrations.AddField(
            model_name='lineitem',
            name='material',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lineitems', to='inventory.MaterialType'),
        ),
        migrations.AlterField(
            model_name='progressreport',
            name='worker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progressreports', to='company.Worker'),
        ),
        migrations.DeleteModel(
            name='ProgressAttachment',
        ),
        migrations.AddField(
            model_name='expendreport',
            name='lineitem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expendreports', to='task.LineItem'),
        ),
        migrations.AddField(
            model_name='expendreport',
            name='worker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expendreports', to='company.Worker'),
        ),
    ]
