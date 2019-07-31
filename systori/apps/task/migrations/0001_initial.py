# Generated by Django 2.0.13 on 2019-07-30 20:10

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion
import django_fsm
import tsvector_field


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('project', '0001_initial'),
        ('inventory', '0001_initial'),
        ('equipment', '0001_initial'),
        ('accounting', '0001_initial'),
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpendReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('comment', models.TextField()),
                ('expended', models.DecimalField(decimal_places=3, default=Decimal('0.00'), max_digits=13, verbose_name='Expended')),
            ],
            options={
                'verbose_name': 'Expend Report',
                'verbose_name_plural': 'Expend Reports',
                'ordering': ('-timestamp',),
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True)),
                ('name', models.CharField(blank=True, default='', max_length=512, verbose_name='Name')),
                ('description', models.TextField(blank=True, default='', verbose_name='Description')),
                ('depth', models.PositiveIntegerField(db_index=True, editable=False)),
                ('token', models.BigIntegerField(null=True, verbose_name='api token')),
                ('search', tsvector_field.SearchVectorField(columns=[tsvector_field.WeightedColumn('name', 'A'), tsvector_field.WeightedColumn('description', 'D')], language='german')),
            ],
            options={
                'verbose_name': 'Group',
                'verbose_name_plural': 'Groups',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True)),
                ('name', models.CharField(blank=True, max_length=512, verbose_name='Name')),
                ('qty', models.DecimalField(decimal_places=3, default=Decimal('0.00'), max_digits=13, verbose_name='Quantity')),
                ('qty_equation', models.CharField(blank=True, max_length=512)),
                ('expended', models.DecimalField(decimal_places=3, default=Decimal('0.00'), max_digits=12, verbose_name='Expended')),
                ('unit', models.CharField(blank=True, max_length=512, verbose_name='Unit')),
                ('price', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Price')),
                ('price_equation', models.CharField(blank=True, max_length=512)),
                ('total', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Total')),
                ('total_equation', models.CharField(blank=True, max_length=512)),
                ('lineitem_type', models.CharField(choices=[('material', 'Material'), ('labor', 'Labor'), ('equipment', 'Equipment'), ('other', 'Other')], default='other', max_length=128, verbose_name='Line Item Type')),
                ('token', models.BigIntegerField(null=True, verbose_name='api token')),
                ('is_hidden', models.BooleanField(default=False)),
                ('equipment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lineitems', to='equipment.EquipmentType')),
                ('labor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lineitems', to='company.LaborType')),
                ('material', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lineitems', to='inventory.MaterialType')),
            ],
            options={
                'verbose_name': 'Line Item',
                'verbose_name_plural': 'Line Items',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='ProgressReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('comment', models.TextField()),
                ('complete', models.DecimalField(decimal_places=3, default=Decimal('0.00'), max_digits=13, verbose_name='Complete')),
            ],
            options={
                'verbose_name': 'Progress Report',
                'verbose_name_plural': 'Progress Reports',
                'ordering': ('-timestamp',),
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True)),
                ('name', models.CharField(max_length=512, verbose_name='Name')),
                ('description', models.TextField(blank=True)),
                ('search', tsvector_field.SearchVectorField(columns=[tsvector_field.WeightedColumn('name', 'A'), tsvector_field.WeightedColumn('description', 'D')], language='german')),
                ('qty', models.DecimalField(blank=True, decimal_places=3, default=Decimal('0.00'), max_digits=13, null=True, verbose_name='Quantity')),
                ('qty_equation', models.CharField(blank=True, max_length=512)),
                ('complete', models.DecimalField(decimal_places=3, default=Decimal('0.00'), max_digits=12, verbose_name='Completed')),
                ('unit', models.CharField(blank=True, max_length=512, verbose_name='Unit')),
                ('price', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Price')),
                ('price_equation', models.CharField(blank=True, max_length=512)),
                ('total', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Total')),
                ('total_equation', models.CharField(blank=True, max_length=512)),
                ('started_on', models.DateField(blank=True, null=True)),
                ('completed_on', models.DateField(blank=True, null=True)),
                ('variant_group', models.PositiveIntegerField(default=0)),
                ('variant_serial', models.PositiveIntegerField(default=0)),
                ('is_provisional', models.BooleanField(default=False)),
                ('status', django_fsm.FSMField(blank=True, choices=[('approved', 'Approved'), ('ready', 'Ready'), ('running', 'Running'), ('done', 'Done')], max_length=50)),
                ('token', models.BigIntegerField(null=True, verbose_name='api token')),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Task',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('root', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='+', serialize=False, to='task.Group')),
                ('is_revenue_recognized', models.BooleanField(default=False)),
                ('is_locked', models.BooleanField(default=False)),
                ('status', django_fsm.FSMField(choices=[('draft', 'Draft'), ('proposed', 'Proposed'), ('approved', 'Approved'), ('started', 'Started'), ('completed', 'Completed')], default='draft', max_length=50)),
                ('account', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job', to='accounting.Account')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='project.Project')),
            ],
            options={
                'verbose_name': 'Job',
                'verbose_name_plural': 'Job',
            },
            bases=('task.group',),
        ),
        migrations.AddField(
            model_name='task',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='task.Group'),
        ),
        migrations.AddField(
            model_name='progressreport',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progressreports', to='task.Task'),
        ),
        migrations.AddField(
            model_name='progressreport',
            name='worker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progressreports', to='company.Worker'),
        ),
        migrations.AddField(
            model_name='lineitem',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lineitems', to='task.Task'),
        ),
        migrations.AddField(
            model_name='group',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='task.Group'),
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
        migrations.AddField(
            model_name='task',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_tasks', to='task.Job'),
        ),
        migrations.AddField(
            model_name='lineitem',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_lineitems', to='task.Job'),
        ),
        migrations.AddField(
            model_name='group',
            name='job',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='all_groups', to='task.Job'),
        ),
    ]
