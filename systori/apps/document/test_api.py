from datetime import timedelta
from django.core.urlresolvers import reverse
from django.utils.timezone import localtime, now
from django.utils.formats import date_format

from systori.lib.testing import ClientTestCase

from ..project.factories import ProjectFactory
from ..document.factories import DocumentTemplateFactory
from ..directory.factories import ContactFactory


class DocumentTemplateApiTest(ClientTestCase):

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.contact = ContactFactory(salutation="Mr", first_name="Ben", last_name="Schmidt",
                                      project=self.project, is_billable=True)

    def test_english_variables(self):
        self.user.language = "en"
        self.user.save()
        doc = DocumentTemplateFactory(
            header="this is a [firstname] test [today]",
            footer="thx and goodbye [today +14]"
        )
        response = self.client.get(
            reverse('api.document.template', args=[self.project.pk, doc.pk]),
            format='json'
        )
        date_now = localtime(now()).date()
        self.assertDictEqual({
            'header': 'this is a Ben test {}'.format(date_format(date_now, use_l10n=True)),
            'footer': 'thx and goodbye {}'.format(date_format(date_now+timedelta(14), use_l10n=True)),
        }, response.data)

    def test_german_variables(self):
        self.user.language = "de"
        self.user.save()
        doc = DocumentTemplateFactory(
            header="this is a [Anrede] [Vorname] [Nachname] [Name] test [heute]",
            footer="thx and goodbye [heute +14] and [heute +21]"
        )
        response = self.client.get(
            reverse('api.document.template', args=[self.project.pk, doc.pk]),
            format='json'
        )
        date_now = localtime(now()).date()
        self.assertDictEqual({
            'header': 'this is a Mr Ben Schmidt Mr Ben Schmidt test {}'.format(date_format(date_now, use_l10n=True)),
            'footer': 'thx and goodbye {} and {}'.format(
                date_format(date_now + timedelta(14), use_l10n=True),
                date_format(date_now + timedelta(21), use_l10n=True)),
        }, response.data)
