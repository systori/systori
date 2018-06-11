import factory
from factory import fuzzy
from ..company.models import Worker, Contract
from .models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: "test_user_{}@systori.com".format(n))
    first_name = fuzzy.FuzzyText(length=15)
    last_name = fuzzy.FuzzyText(length=15)

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted or "open sesame"
        self.set_password(password)

    @factory.post_generation
    def company(self, create, extracted, **kwargs):
        if extracted is not None:
            worker = Worker.objects.create(company=extracted, user=self, is_staff=True)
            worker.contract = Contract.objects.create(worker=worker, rate=0)
            worker.save()
