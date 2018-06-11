# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import systori.apps.user.models


class Migration(migrations.Migration):

    dependencies = [("auth", "0006_require_contenttypes_0002")]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True,
                        verbose_name="ID",
                        auto_created=True,
                        serialize=False,
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        null=True, verbose_name="last login", blank=True
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        verbose_name="superuser status",
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        max_length=30, verbose_name="first name", blank=True
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        max_length=30, verbose_name="last name", blank=True
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        unique=True,
                        max_length=254,
                        null=True,
                        verbose_name="email address",
                        blank=True,
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "language",
                    models.CharField(
                        max_length=2,
                        choices=[("de", "Deutsch"), ("en", "English")],
                        blank=True,
                        verbose_name="language",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        verbose_name="groups",
                        to="auth.Group",
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        verbose_name="user permissions",
                        to="auth.Permission",
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                    ),
                ),
            ],
            options={
                "ordering": ("first_name",),
                "verbose_name": "user",
                "verbose_name_plural": "users",
            },
            managers=[("objects", systori.apps.user.models.UserManager())],
        )
    ]
