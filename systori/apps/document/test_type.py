from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from .type import proposal, utils
from .models import Proposal


class UtilsTest(TestCase):

    def test_update_instance(self):
        proposal = Proposal(json={})
        original_date = timezone.now().date()
        proposal = utils.update_instance(
            proposal, 
            {'field': 'value', 'document_date': original_date},
            {'document_date': 'date'}
        )
        self.assertEqual(proposal.json, {'date': original_date, 'field': 'value'})
        self.assertEqual(proposal.document_date, original_date)

        new_date = original_date - timedelta(days=2)
        proposal = utils.update_instance(
            proposal, 
            {'field': 'value', 'document_date': new_date}
        )
        self.assertEqual(proposal.json, {'date': original_date, 'field': 'value'})
        self.assertEqual(proposal.document_date, new_date)
