from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import *
from .models import User


class UbrUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_laborer', 'is_foreman', 'is_staff', 'is_superuser',
                                       'is_active', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')}),
        (_('Permissions'), {'fields': ('is_laborer', 'is_foreman', 'is_staff',
                                       'is_superuser', 'is_active')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_laborer', 'is_foreman', 'is_staff')
    list_filter = ('is_laborer', 'is_foreman', 'is_staff', 'is_superuser', 'is_active', 'groups')


admin.site.register(User, UbrUserAdmin)