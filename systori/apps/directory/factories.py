import factory
from factory import fuzzy

from .models import Contact, ProjectContact
from ..project.models import Project


class ContactFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Contact
        django_get_or_create = ('first_name',)

    salutation = fuzzy.FuzzyText(length=4)
    first_name = fuzzy.FuzzyText(length=8)
    last_name = fuzzy.FuzzyText(length=12)

