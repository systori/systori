import factory
from factory import fuzzy
from .models import Contact, ProjectContact


class ContactFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Contact
        django_get_or_create = ('first_name',)

    salutation = fuzzy.FuzzyText(length=4)
    first_name = fuzzy.FuzzyText(length=8)
    last_name = fuzzy.FuzzyText(length=12)

    @classmethod
    def _create(cls, *args, **kwargs):
        project = kwargs.pop('project', None)
        is_billable = kwargs.pop('is_billable', False)
        association = kwargs.pop('association', ProjectContact.CUSTOMER)
        contact = super()._create(*args, **kwargs)
        if project is not None:
            ProjectContact.objects.create(
                project=project,
                contact=contact,
                association=association,
                is_billable=is_billable
            )
        return contact
