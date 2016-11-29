import factory
from factory import fuzzy

from .models import DocumentTemplate


class DocumentTemplateFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = DocumentTemplate
        django_get_or_create = ('name',)

    name = fuzzy.FuzzyText(length=15)
    header = fuzzy.FuzzyText(length=10, suffix=" [today]")
    footer = fuzzy.FuzzyText(length=10, suffix=" [today +14]")
