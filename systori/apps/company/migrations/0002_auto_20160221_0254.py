# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='users',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, through='company.Access', related_name='companies'),
        ),
        migrations.AddField(
            model_name='access',
            name='company',
            field=models.ForeignKey(to='company.Company', related_name='users_access', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='access',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='companies_access', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='access',
            unique_together=set([('company', 'user')]),
        ),
    ]
