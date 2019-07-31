# Generated by Django 2.0.13 on 2019-07-30 20:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('business', models.CharField(blank=True, max_length=512, verbose_name='Business')),
                ('salutation', models.CharField(blank=True, max_length=512, verbose_name='Salutation')),
                ('first_name', models.CharField(blank=True, max_length=512, verbose_name='First Name')),
                ('last_name', models.CharField(blank=True, max_length=512, verbose_name='Last Name')),
                ('phone', models.CharField(blank=True, max_length=512, verbose_name='Phone')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('website', models.URLField(blank=True, verbose_name='Website')),
                ('address', models.CharField(blank=True, max_length=512, verbose_name='Address')),
                ('postal_code', models.CharField(blank=True, max_length=512, verbose_name='Postal Code')),
                ('city', models.CharField(blank=True, max_length=512, verbose_name='City')),
                ('country', models.CharField(default='Deutschland', max_length=512, verbose_name='Country')),
                ('is_address_label_generated', models.BooleanField(default=True, verbose_name='auto-generate address label')),
                ('address_label', models.TextField(blank=True, verbose_name='Address Label')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
            ],
            options={
                'verbose_name': 'Contact',
                'verbose_name_plural': 'Contacts',
                'ordering': ['first_name', 'last_name'],
            },
        ),
        migrations.CreateModel(
            name='ProjectContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('association', models.CharField(choices=[('customer', 'Customer'), ('contractor', 'Contractor'), ('supplier', 'Supplier'), ('architect', 'Architect'), ('other', 'Other')], default='customer', max_length=128, verbose_name='Association')),
                ('is_billable', models.BooleanField(default=False, verbose_name='Is Billable?')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_contacts', to='directory.Contact')),
            ],
            options={
                'verbose_name': 'Project Contact',
                'verbose_name_plural': 'Project Contacts',
                'ordering': ['association', 'id'],
            },
        ),
    ]
