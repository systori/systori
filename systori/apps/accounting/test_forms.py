from django.test import TestCase
from .test_skr03 import create_data
from .forms import PaymentForm, PaymentSplitFormSet


class AccountingTestCase(TestCase):

    def setUp(self):
        create_data(self)
        self.task.complete = 5
        self.task.save()

        self.management_form = {}
        _management_form = PaymentSplitFormSet(jobs=self.project.jobs.all()).management_form.initial
        for key, value in _management_form.items():
            self.management_form['form-'+key] = value

    def make_split_payment_form(self, data):
        data.update(self.management_form)
        payment_form = PaymentForm(data)
        payment_form.full_clean()
        split_form = PaymentSplitFormSet(data, jobs=self.project.jobs.all())
        split_form.set_payment_form(payment_form)
        return split_form


class PaymentSplitFormTests(AccountingTestCase):

    def test_simple_payment(self):
        form = self.make_split_payment_form({

            'amount': '2',

            'form-0-job': self.job.id,
            'form-0-amount': '1',
            'form-0-discount': '0',

            'form-1-job': self.job2.id,
            'form-1-amount': '1',
            'form-1-discount': '0',

        })
        self.assertTrue(form.is_valid())
