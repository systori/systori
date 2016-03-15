from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from .models import Timer


class UserForm(ModelForm):

    class Meta:
        model = Timer
        fields = ['kind']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        if Timer.objects.filter(user=self.user, end__isnull=True).exists():
            raise forms.ValidationError(_('Timer already running'))

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        instance.user = self.user
