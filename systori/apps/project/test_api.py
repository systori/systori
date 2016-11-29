from datetime import timedelta
from django.core.urlresolvers import reverse
from django.utils.timezone import localtime, now
from django.utils.formats import date_format
from django.utils import translation
from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from ..project.factories import ProjectFactory
from ..document.models import DocumentTemplate
from ..directory.factories import ContactFactory
from ..directory.models import ProjectContact
from systori.lib.testing import SystoriTestCase
from ..project.models import Project


class BaseTestCase(SystoriTestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.worker = UserFactory(company=self.company, language='en', password='open sesame').access.first()
        self.client.login(username=self.worker.email, password='open sesame')
        self.project = ProjectFactory()
        self.contact = ContactFactory()
        self.project_contact = ProjectContact.objects.create(contact=self.contact, project=self.project, is_billable=True)
        self.project.save()
        self.doc_temp = DocumentTemplate.objects.create(
            name="test",
            header="this is a [firstname] test [today]",
            footer="thx and goodbye [today +14]"
        )
        self.doc_temp2 = DocumentTemplate.objects.create(
            name="test2",
            header="das ist ein [Vorname] test [heute]",
            footer="danke und auf wiedersehen [heute +14]"
        )


class DocumentTemplateApiTest(BaseTestCase):

    def test_first_name(self):
        response = self.client.get(reverse('api.document.template', args=[self.project.pk, self.doc_temp.pk]))
        self.assertContains(response, self.contact.first_name)

    def test_today(self):
        date_now = localtime(now()).date()
        response = self.client.get(reverse('api.document.template', args=[self.project.pk, self.doc_temp.pk]))
        self.assertContains(response, date_format(date_now, use_l10n=True))

    def test_today_14(self):
        date_now = localtime(now()).date()
        response = self.client.get(reverse('api.document.template', args=[self.project.pk, self.doc_temp.pk]))
        self.assertContains(response, date_format(date_now+timedelta(14), use_l10n=True))

    def test_vorname(self):
        translation.activate("de")
        response = self.client.get(reverse('api.document.template', args=[self.project.pk, self.doc_temp2.pk]))
        self.assertContains(response, self.contact.first_name)