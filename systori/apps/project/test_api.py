from django.core.urlresolvers import reverse
from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from ..project.factories import ProjectFactory
from ..document.factories import DocumentTemplateFactory
from ..directory.factories import ContactFactory, ProjectContactFactory
from systori.lib.testing import SystoriTestCase
from ..project.models import Project

from ..document.models import DocumentTemplate


class BaseTestCase(SystoriTestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.worker = UserFactory(company=self.company, language='en', password='open sesame').access.first()
        self.client.login(username=self.worker.email, password='open sesame')
        self.doctemp = DocumentTemplateFactory()
        self.contact = ContactFactory()
        #self.project_contact = ProjectContactFactory()


class DocumentTemplateApiTest(BaseTestCase):

    def test_true(self):
        self.client.get(reverse('api.document.template', args=[1, 1]))
        self.assertEqual("1", "1")
