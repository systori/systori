from factory import django
from factory import fuzzy
from .models import Job, Group, Task, LineItem


class JobFactory(django.DjangoModelFactory):
    class Meta:
        model = Job

    name = fuzzy.FuzzyText(length=15)

    @classmethod
    def _create(cls, *args, **kwargs):
        obj = super()._create(*args, **kwargs)
        obj.job = obj
        obj.save()
        return obj


class GroupFactory(django.DjangoModelFactory):
    class Meta:
        model = Group

    name = fuzzy.FuzzyText(length=15)

    @classmethod
    def _create(cls, *args, **kwargs):
        assert 'job' not in kwargs
        kwargs['job'] = kwargs['parent'].job
        return super()._create(*args, **kwargs)


class TaskFactory(django.DjangoModelFactory):
    class Meta:
        model = Task

    name = fuzzy.FuzzyText(length=15)

    @classmethod
    def _create(cls, *args, **kwargs):
        assert 'job' not in kwargs
        kwargs['job'] = kwargs['group'].job
        return super()._create(*args, **kwargs)


class LineItemFactory(django.DjangoModelFactory):
    class Meta:
        model = LineItem

    name = fuzzy.FuzzyText(length=15)

    @classmethod
    def _create(cls, *args, **kwargs):
        assert 'job' not in kwargs
        kwargs['job'] = kwargs['task'].job
        return super()._create(*args, **kwargs)
