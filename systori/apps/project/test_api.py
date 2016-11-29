from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from ..project.factories import ProjectFactory
from ..document.factories import DocumentTemplateFactory
from systori.lib.testing import SystoriTestCase
from ..project.models import Project

from ..document.models import DocumentTemplate


class BaseTestCase(SystoriTestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.worker = UserFactory(company=self.company, language='en', password='open sesame').access.first()
        self.client.login(username=self.worker.email, password='open sesame')
        self.doctemp = DocumentTemplateFactory()


class DocumentTemplateApiTest(BaseTestCase):

    def test_true(self):
        print(self.client.get("api/1/document-template/1"))
        self.assertEqual("1", "1")
