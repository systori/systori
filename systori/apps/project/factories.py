import factory
from factory import fuzzy

from .models import Project, JobSite


class ProjectFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Project
        django_get_or_create = ('name',)

    name = fuzzy.FuzzyText(length=15)


class JobSiteFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = JobSite
        django_get_or_create = ('name',)

    name = fuzzy.FuzzyText(length=15)
    address = fuzzy.FuzzyText(length=15)
    city = fuzzy.FuzzyText(length=15)
    postal_code = fuzzy.FuzzyInteger(1024, 9999)
