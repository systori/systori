import random

import factory
from factory import fuzzy

from .models import Project, JobSite, DailyPlan
from ..task.factories import JobFactory


class ProjectFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Project

    name = fuzzy.FuzzyText(length=15)

    @factory.post_generation
    def with_job(self: Project, create, extracted, **kwargs):
        if create and extracted:
            JobFactory(project=self, generate_groups=True)


class JobSiteFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = JobSite

    name = fuzzy.FuzzyText(length=15)
    address = fuzzy.FuzzyText(length=15)
    city = fuzzy.FuzzyText(length=15)
    postal_code = fuzzy.FuzzyAttribute(lambda: str(random.randint(1024, 9999)))


class DailyPlanFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = DailyPlan
