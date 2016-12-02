import os.path
import factory
from factory import fuzzy
from django.conf import settings

from systori.lib.accounting.tools import Amount

from .models import Proposal, Invoice
from .models import Letterhead, DocumentSettings, DocumentTemplate


class DocumentTemplateFactory(factory.django.DjangoModelFactory):

    name = fuzzy.FuzzyText(length=15)

    class Meta:
        model = DocumentTemplate


class ProposalFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Proposal


class InvoiceFactory(factory.django.DjangoModelFactory):

    json = {'debit': Amount.zero()}

    class Meta:
        model = Invoice


class DocumentSettingsFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = DocumentSettings


class LetterheadFactory(factory.django.DjangoModelFactory):

    name = fuzzy.FuzzyText(length=15)
    letterhead_pdf = os.path.join(settings.BASE_DIR, 'apps/document/test_data/letterhead.pdf')

    class Meta:
        model = Letterhead

    @classmethod
    def _create(cls, *args, **kwargs):
        obj = super()._create(*args, **kwargs)
        DocumentSettingsFactory(
            language='de',
            evidence_letterhead=obj,
            proposal_letterhead=obj,
            invoice_letterhead=obj
        )
        return obj
