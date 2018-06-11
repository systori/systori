from django.test import TestCase
from django.db import IntegrityError
from django.utils.translation import activate

from ..project.factories import ProjectFactory
from ..company.factories import CompanyFactory
from ..task.factories import JobFactory

from .forms import BankAccountForm
from .models import Account, create_account_for_job
from .constants import DEBTOR_CODE_RANGE, BANK_CODE_RANGE
from .workflow import create_chart_of_accounts


class TestBankAccountForm(TestCase):
    def setUp(self):
        CompanyFactory()

    def test_account_already_exists(self):
        job = JobFactory(project=ProjectFactory())
        create_account_for_job(job)
        message = "Account with code 1{:04} already exists.".format(job.id)
        with self.assertRaisesMessage(IntegrityError, message):
            create_account_for_job(job)

    def test_account_id_outside_range(self):
        job = JobFactory(project=ProjectFactory())
        job.id = DEBTOR_CODE_RANGE[1] - DEBTOR_CODE_RANGE[0] + 1
        message = "Account id %s is outside the maximum range of %s." % (
            DEBTOR_CODE_RANGE[1] + 1,
            DEBTOR_CODE_RANGE[1],
        )
        with self.assertRaisesMessage(ValueError, message):
            create_account_for_job(job)

    def test_form_initial_incremented_code(self):
        create_chart_of_accounts()
        self.assertEquals(
            str(BANK_CODE_RANGE[0] + 1), BankAccountForm().initial["code"]
        )

    def test_form_edit_code(self):
        self.assertEquals(
            "hi",
            BankAccountForm(instance=Account.objects.create(code="hi")).initial["code"],
        )

    def test_valid_code(self):
        self.assertTrue(BankAccountForm({"code": "1200"}).is_valid())
        self.assertTrue(BankAccountForm({"code": "1288"}).is_valid())

    def test_invalid_code(self):
        activate("en")
        self.assertFalse(BankAccountForm({"code": "foo"}).is_valid())
        self.assertFalse(BankAccountForm({"code": "1199"}).is_valid())
        self.assertFalse(BankAccountForm({"code": "1289"}).is_valid())

        form = BankAccountForm({"code": "1a"})
        self.assertEquals(
            "Account code must be a number between 1200 and 1288 inclusive.",
            form.errors["code"][0],
        )
