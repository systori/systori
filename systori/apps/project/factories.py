import factory
from factory import fuzzy

from .models import Project, JobSite


class ProjectFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Project

    name = fuzzy.FuzzyText(length=15)
    structure = "01.01.001"
    maximum_depth = 1


class JobSiteFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = JobSite

    name = fuzzy.FuzzyText(length=15)
    address = fuzzy.FuzzyText(length=15)
    city = fuzzy.FuzzyText(length=15)
    postal_code = fuzzy.FuzzyInteger(1024, 9999)
