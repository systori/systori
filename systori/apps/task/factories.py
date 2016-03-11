import factory
from factory import django
from factory import fuzzy
from .models import Job, TaskGroup, Task, TaskInstance, LineItem


class JobFactory(django.DjangoModelFactory):
    class Meta:
        model = Job

    job_code = factory.Sequence(lambda n: n)
    name = fuzzy.FuzzyText(length=15)


class TaskGroupFactory(django.DjangoModelFactory):
    class Meta:
        model = TaskGroup

    name = fuzzy.FuzzyText(length=15)


class TaskFactory(django.DjangoModelFactory):
    class Meta:
        model = Task

    name = fuzzy.FuzzyText(length=15)


class TaskInstanceFactory(django.DjangoModelFactory):
    class Meta:
        model = TaskInstance

    name = fuzzy.FuzzyText(length=15)


class LineItemFactory(django.DjangoModelFactory):
    class Meta:
        model = LineItem

    name = fuzzy.FuzzyText(length=15)
