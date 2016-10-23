import factory
from factory import django
from factory import fuzzy
from .models import Job, Group, Task, LineItem


class JobFactory(django.DjangoModelFactory):
    class Meta:
        model = Job

    name = fuzzy.FuzzyText(length=15)


class GroupFactory(django.DjangoModelFactory):
    class Meta:
        model = Group

    name = fuzzy.FuzzyText(length=15)


class TaskFactory(django.DjangoModelFactory):
    class Meta:
        model = Task

    name = fuzzy.FuzzyText(length=15)


class LineItemFactory(django.DjangoModelFactory):
    class Meta:
        model = LineItem

    name = fuzzy.FuzzyText(length=15)

    @classmethod
    def _create(cls, *args, **kwargs):
        if 'qty' in kwargs and 'qty_equation' not in kwargs:
            kwargs['qty_equation'] = str(kwargs['qty'])
        if 'price' in kwargs and 'price_equation' not in kwargs:
            kwargs['price_equation'] = str(kwargs['price'])
        if 'total' in kwargs and 'total_equation' not in kwargs:
            kwargs['total_equation'] = str(kwargs['total'])
        if 'total' not in kwargs and 'total_equation' not in kwargs:
            _qty = kwargs.get('qty', 0)
            if kwargs.get('unit') == '%':
                _qty /= 100.00
            kwargs['total'] = _qty * kwargs.get('price', 0)
            kwargs['total_equation'] = str(kwargs['total'])
        obj = super()._create(*args, **kwargs)
        return obj
