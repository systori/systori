from systori.lib.testing import ClientTestCase
from ..project.factories import ProjectFactory
from .factories import NoteFactory


class NoteApiTest(ClientTestCase):

    def setUp(self):
        self.project = ProjectFactory()

    def test_create_note(self):
        note = NoteFactory()
