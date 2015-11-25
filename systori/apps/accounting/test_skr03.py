from django.test import TestCase
from django.db import IntegrityError
from .models import create_account_for_job
from .constants import DEBTOR_CODE_RANGE


class TestAccountCodeValidations(TestCase):
    def test_creating_account_for_job(self):
        self.job.account = create_account_for_job(self.job)
        self.assertRaisesMessage(IntegrityError,
                                 "Account with code %s already exists." % '1{:04}'.format(self.job.id),
                                 create_account_for_job, self.job)

        self.job.id = DEBTOR_CODE_RANGE[1] - DEBTOR_CODE_RANGE[0] + 1
        self.assertRaisesMessage(ValueError,
                                 "Account id %s is outside the maximum range of %s." % (
                                     DEBTOR_CODE_RANGE[1] + 1, DEBTOR_CODE_RANGE[1]),
                                 create_account_for_job, self.job)
