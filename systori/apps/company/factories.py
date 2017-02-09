import factory
from factory import fuzzy

from ..project.factories import ProjectFactory
from .models import Company, Worker


class CompanyFactory(factory.django.DjangoModelFactory):
    name = fuzzy.FuzzyText(length=15)
    # This should be left static to avoid conflicts
    schema = 'testcompany'

    class Meta:
        model = Company
        django_get_or_create = ('schema', 'name',)

    @classmethod
    def _create(cls, *args, **kwargs):
        obj = super()._create(*args, **kwargs)
        obj.activate()
        ProjectFactory(is_template=True)
        return obj


class WorkerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Worker
