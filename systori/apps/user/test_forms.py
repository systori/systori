from django.test import TestCase
from django.utils.translation import activate

from .factories import UserFactory
from .forms import UserForm
from ..company.factories import CompanyFactory


class TestUserForm(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company, language='en', password='foo')

    def test_clean(self):
        activate('en')
        self.assertFalse(UserForm({}).is_valid())
        self.assertEquals('A name or email is required.',
                          UserForm({}).errors['__all__'][0])
        self.assertTrue(UserForm({'first_name': 'foo'}).is_valid())
        self.assertTrue(UserForm({'last_name': 'foo'}).is_valid())
        self.assertTrue(UserForm({'email': 'foo@bar.com'}).is_valid())

    def test_clean_password(self):
        self.assertEquals("The two password fields didn't match.",
                          UserForm({'first_name': 'foo', 'password1': 'foo'}).errors['password2'][0])
        form = UserForm({'first_name': 'foo', 'password1': 'foo', 'password2': 'foo'})
        self.assertTrue(form.is_valid(), form.errors)
