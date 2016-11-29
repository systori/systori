import factory
from factory import fuzzy

from .models import Contact, ProjectContact
from ..project.models import Project


class ContactFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Contact
        django_get_or_create = ('name',)

    salutation = fuzzy.FuzzyText(length=4)
    first_name = fuzzy.FuzzyText(length=8)
    last_name = fuzzy.FuzzyText(length=12)


class ProjectContactFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = ProjectContact
        django_get_or_create = ('association',)

    contact = Contact.objects.first()
    project = Project.objects.first()
