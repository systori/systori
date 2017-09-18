from systori.lib.testing import ClientTestCase
from django.urls import reverse

from ..project.factories import ProjectFactory
from .models import Note
from .factories import NoteFactory


class NoteApiTest(ClientTestCase):

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()

    def test_create_note(self):
        note = NoteFactory(project=self.project, content_object=self.project, worker=self.worker)
        response = self.client.get(reverse('note.api', kwargs={'pk': note.pk}))
        self.assertEqual(response.status_code, 200)

    def test_update_note(self):
        note = NoteFactory(project=self.project, content_object=self.project, worker=self.worker)
        self.client.put(reverse('note.api', kwargs={'pk': note.pk}),
                                {'text': 'hallo was geht'}, format='json')
        self.assertEqual(Note.objects.get(id=note.id).text, 'hallo was geht')

    def test_delete_note(self):
        note = NoteFactory(project=self.project, content_object=self.project, worker=self.worker)
        response = self.client.delete(reverse('note.api', kwargs={'pk': note.pk}))
        self.assertEqual(response.status_code, 204)

    def test_generic_relation(self):
        note = NoteFactory(project=self.project, content_object=self.project, worker=self.worker)
        self.assertEqual(self.project.notes.first(), note)
