from django.test import TestCase
from django.utils.translation import activate
from django.utils import timezone
from .forms import UserForm
from ..company.factories import CompanyFactory
from ..user.factories import UserFactory

class CreateUserDataMixin:

    def setUp(self):
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company)
        self.data = {
            'first_name': 'foo',
            'last_name': 'foo',
            'email': 'foo@bar.com',
            'date_joined': timezone.now().strftime('%Y-%m-%d %T')
        }


class TestUserForm(CreateUserDataMixin, TestCase):

    def test_clean(self):
        activate('en')
        self.assertFalse(UserForm({}).is_valid())
        self.assertEquals('A name or email is required.',
                          UserForm({}).errors['__all__'][0])
        self.assertTrue(UserForm(data=self.data).is_valid())

    def test_clean_password(self):
        self.data.update({
            'password1': 'foo',
            'password2': 'not-foo'
        })
        self.assertEquals("The two password fields didn't match.",
                          UserForm(data=self.data).errors['password2'][0])
        self.data.update({
            'password2': 'foo'
        })
        self.assertTrue(UserForm(data=self.data).is_valid())
