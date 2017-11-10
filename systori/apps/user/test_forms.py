from django.test import TestCase
from django.utils.translation import activate

from .factories import UserFactory
from .forms import UserForm
from ..company.factories import CompanyFactory


class TestUserForm(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.user = UserFactory(company=self.company, language='en', password='foo')
        activate('en')

    def test_clean(self):
        self.assertEqual(UserForm({}).errors, {'first_name': ['This field is required.']})
        # first_name is bare minimum
        self.assertTrue(UserForm({'first_name': 'foo'}).is_valid())

    def test_clean_email(self):
        # due to how db handles unique columns, blank email must be NULL
        form = UserForm({'email': ''})
        form.full_clean()
        self.assertEqual(form.cleaned_data['email'], None)
        form = UserForm({'email': 'foo@foo.com'})
        form.full_clean()
        self.assertEqual(form.cleaned_data['email'], 'foo@foo.com')

    def test_clean_password(self):
        self.assertEquals(
            UserForm({'first_name': 'foo', 'password1': 'foo'}).errors, {
                'password2': ["The two password fields didn't match."]
            }
        )
        self.assertTrue(UserForm({'first_name': 'foo', 'password1': 'foo', 'password2': 'foo'}).is_valid())
