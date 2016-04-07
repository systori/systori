import factory
from factory import fuzzy

from .models import Project


class ProjectFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Project
        django_get_or_create = ('name',)

    name = fuzzy.FuzzyText(length=15)
