from factory import django
from factory import fuzzy
from .models import Job, Group, Task, LineItem
from systori.lib.templatetags.customformatting import ubrdecimal


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
            kwargs['qty_equation'] = kwargs['qty']
        if 'price' in kwargs and 'price_equation' not in kwargs:
            kwargs['price_equation'] = round(kwargs['price'], 2)
        if 'total' in kwargs and 'total_equation' not in kwargs:
            kwargs['total_equation'] = round(kwargs['total'], 2)
        if 'price' in kwargs and 'total' in kwargs and 'qty' not in kwargs:
            kwargs['qty'] = round(kwargs['total'] / kwargs['price'], 2)
        if 'qty' in kwargs and 'total' in kwargs and 'price' not in kwargs:
            kwargs['price'] = round(kwargs['total'] / kwargs['qty'], 2)
        if 'total' not in kwargs and 'total_equation' not in kwargs:
            _qty = kwargs.get('qty', 0)
            if kwargs.get('unit') == '%':
                _qty /= 100.00
            kwargs['total'] = round(_qty * kwargs.get('price', 0), 2)
        obj = super()._create(*args, **kwargs)
        return obj
