import string

import factory
from factory import fuzzy
from django.conf import settings

from .models import Company


class CompanyFactory(factory.django.DjangoModelFactory):
    name = fuzzy.FuzzyText(length=15)
    schema = fuzzy.FuzzyText(length=10, chars=string.ascii_lowercase)

    class Meta:
        model = Company
        django_get_or_create = ('schema', 'name',)

    @classmethod
    def _create(cls, *args, **kwargs):
        obj = super()._create(*args, **kwargs)
        obj.activate()
        return obj
