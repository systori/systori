from django.urls import reverse

from systori.lib.testing import ClientTestCase

from systori.apps.project.factories import ProjectFactory
from systori.apps.main.factories import NoteFactory


class NoteTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.project2 = ProjectFactory()

    def test_create_note_with_project(self):
        note = NoteFactory(project=self.project, content_object=self.project, worker=self.worker)
        response = self.client.get(reverse('note', kwargs={'pk': note.pk}))
        self.assertEqual(response.status_code, 200)

    def test_update_note_with_success_url(self):
        note = NoteFactory(project=self.project, content_object=self.project, worker=self.worker)
        self.client.get(reverse('note', args=[note.pk]))
        response = self.client.post(reverse('note',
                                            args=[note.pk, '/project-{}'.format(self.project.id)]),
                                    {'text': 'this is an update.'},
                                    follow=True)
        self.assertRedirects(response, reverse('project.view', args=[self.project.id]))

    def test_field_note(self):
        note1 = NoteFactory(project=self.project, content_object=self.project, worker=self.worker)
        note2 = NoteFactory(project=self.project2, content_object=self.project2, worker=self.worker)
        response = self.client.get(reverse('field.notes.all'))
        self.assertIn(note1, response.context['object_list'])
        self.assertIn(note2, response.context['object_list'])
        response = self.client.get(reverse('field.notes', kwargs={'project_pk': self.project.pk}))
        self.assertIn(note1, response.context['object_list'])
        self.assertNotIn(note2, response.context['object_list'])

###
# all Tests below had been for django-channels which isn't a dependency currently
# once we get again some websockets/http2 support they should be migrated.
###
# from channels.test import ChannelTestCase
# from django.db.models.signals import post_save
# from systori.apps.user.factories import UserFactory
# from systori.apps.main.models import Note
# from factory.django import mute_signals
#
# class NoteApiTest(ClientTestCase, ChannelTestCase):
#
#     def setUp(self):
#         super().setUp()
#         self.project = ProjectFactory()
#         self.project2 = ProjectFactory()
#
#     @mute_signals(post_save)
#     def test_create_note(self):
#         note = NoteFactory(project=self.project, content_object=self.project, worker=self.worker)
#         response = self.client.get(reverse('note.api', kwargs={'pk': note.pk}))
#         self.assertEqual(response.status_code, 200)
#
#     @mute_signals(post_save)
#     def test_update_note(self):
#         # test edit a note and make sure only this note was edited
#         note = NoteFactory(project=self.project, content_object=self.project, worker=self.worker)
#         note2 = NoteFactory(project=self.project, content_object=self.project, worker=self.worker)
#         note2_text = note2.text
#         note3 = NoteFactory(project=self.project2, content_object=self.project2, worker=self.worker)
#         note3_text = note3.text
#
#         self.client.put(reverse('note.api', kwargs={'pk': note.pk}),
#                                 {'text': 'hallo was geht'}, format='json')
#         self.assertEqual(Note.objects.get(id=note.id).text, 'hallo was geht')
#         self.assertEqual(self.client.get(reverse('note.api', kwargs={'pk': note2.pk})).data.get('text'),
#                          note2.text)
#         self.assertEqual(self.client.get(reverse('note.api', kwargs={'pk': note3.pk})).data.get('text'),
#                          note3.text)
#
#     @mute_signals(post_save)
#     def test_delete_note(self):
#         note = NoteFactory(project=self.project, content_object=self.project, worker=self.worker)
#         response = self.client.delete(reverse('note.api', kwargs={'pk': note.pk}))
#         self.assertEqual(response.status_code, 204)
#
#     @mute_signals(post_save)
#     def test_generic_relation(self):
#         note = NoteFactory(project=self.project, content_object=self.project, worker=self.worker)
#         self.assertEqual(self.project.notes.first(), note)
#
#     @mute_signals(post_save)
#     def test_owner_permission(self):
#         user2 = UserFactory(company=self.company)
#         note = NoteFactory(project=self.project, content_object=self.project, worker=user2.access.first())
#         # trying to delete note from user2 with user1
#         response = self.client.delete(reverse('note.api', kwargs={'pk': note.pk}))
#         self.assertEqual(response.status_code, 403)
#         # trying to edit note from user2 with user1
#         response = self.client.put(reverse('note.api', kwargs={'pk': note.pk}),
#                                    {'text': 'hallo was geht'}, format='json')
#         self.assertEqual(response.status_code, 403)
#         self.assertEqual(Note.objects.count(), 1)
#
#
# class NoteFieldTest(ClientTestCase):
#
#     def setUp(self):
#         super().setUp()
#         self.project = ProjectFactory()
#         self.project2 = ProjectFactory()
#
#     @mute_signals(post_save)
#     def test_note_project_relation(self):
#         note1 = NoteFactory(project=self.project, content_object=self.project, worker=self.worker)
#         note2 = NoteFactory(project=self.project2, content_object=self.project2, worker=self.worker)
#         response = self.client.get(reverse('field.notes.all'))
#         self.assertIn(note1, response.context['object_list'])
#         self.assertIn(note2, response.context['object_list'])
#         response = self.client.get(reverse('field.notes', kwargs={'project_pk': self.project.pk}))
#         self.assertIn(note1, response.context['object_list'])
#         self.assertNotIn(note2, response.context['object_list'])
