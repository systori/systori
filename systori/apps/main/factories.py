import factory
from factory import fuzzy
from .models import Note


class NoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Note

    text = fuzzy.FuzzyText(length=15)
