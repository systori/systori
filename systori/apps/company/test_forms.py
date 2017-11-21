from django.test import TestCase
from django.utils.translation import activate

from ..user.factories import UserFactory
from ..project.models import Project
from ..accounting.models import Account
from ..document.models import Letterhead, DocumentSettings

from .factories import CompanyFactory
from .models import Company
from . import forms


class CompanyFormTest(TestCase):

    def test_required_field_validation(self):
        activate('en')
        form = forms.CompanyForm(data={
            'name': '', 'schema': '', 'timezone': '',
        })
        self.assertFalse(form.is_valid())
        self.assertEqual({
            'name': ['This field is required.'],
            'schema': ['This field is required.'],
            'timezone': ['This field is required.'],
        }, form.errors)

    def test_schema_validation(self):
        activate('en')

        def errors(s):
            form = forms.CompanyForm(data={'schema': s})
            self.assertIn('schema', form.errors, 'No validation error triggered.')
            return form.errors['schema']

        self.assertEqual(errors('AB'), [Company.SCHEMA_NAME_VALIDATOR_MESSAGE])
        self.assertEqual(errors('a b'), [Company.SCHEMA_NAME_VALIDATOR_MESSAGE])
        self.assertEqual(errors('a%b'), [Company.SCHEMA_NAME_VALIDATOR_MESSAGE])
        self.assertEqual(errors('a,b'), [Company.SCHEMA_NAME_VALIDATOR_MESSAGE])
        self.assertEqual(errors('0'), [Company.SCHEMA_NAME_VALIDATOR_MESSAGE])

    def test_create_save(self):
        form = forms.CompanyForm(data={
            'name': 'My Company',
            'schema': 'company',
            'timezone': 'Europe/Berlin',
        }, user=UserFactory())
        self.assertTrue(form.is_valid())
        company = form.save()
        self.assertIsNotNone(company.pk)
        self.assertTrue(company.workers.get().is_owner)
        self.assertGreater(Account.objects.count(), 1)
        Project.objects.template().get()
        DocumentSettings.objects.get()
        Letterhead.objects.get()

    def test_update_save(self):
        company = CompanyFactory(name='new company')
        self.assertEqual(company.name, 'new company')
        form = forms.CompanyForm(data={
            'name': 'updated company',
            'timezone': 'Europe/Berlin',
        }, instance=company)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        company.refresh_from_db()
        self.assertEqual(company.name, 'updated company')
