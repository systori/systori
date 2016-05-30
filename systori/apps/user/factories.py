import factory
from factory import fuzzy

from ..company.models import Access
from .models import User


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User
        django_get_or_create = ('email',)

    email = factory.Sequence(lambda n: 'test_user_{}@systori.com'.format(n))
    first_name = fuzzy.FuzzyText(length=15)
    last_name = fuzzy.FuzzyText(length=15)
    password = factory.PostGenerationMethodCall('set_password', 'open sesame')

    @factory.post_generation
    def company(self, create, extracted, **kwargs):
        if extracted is not None:
            Access.objects.create(company=extracted, user=self, is_staff=True)

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if extracted is not None:
            self.set_password(extracted)
