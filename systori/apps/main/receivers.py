# import json
#
# from channels import Group
#
# from django.templatetags.l10n import localize
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from django.urls import reverse
# from .models import Note
#
#
# @receiver(post_save, sender=Note)
# def send_notes_update(sender, instance, created, **kwargs):
#     message = {
#         'note-pk': instance.pk,
#         'op': 'update',
#         'user': str(instance.worker),
#         'created': localize(instance.created),
#         'html': instance.html,
#     }
#     if created:
#         message.update({
#             'op': 'created',
#         })
#     if instance.project:
#         project_id = instance.project.id
#         message.update({
#             'project-id': project_id,
#             'project-url': reverse('project.view', kwargs={'pk':project_id})
#         })
#     Group('notes').send({'text': json.dumps(message)})
#
#
# @receiver(post_delete, sender=Note)
# def send_notes_delete(sender, instance, **kwargs):
#     message = {
#         'note-pk': instance.pk,
#         'op': 'delete',
#         'html': '<p>this note was deleted</p>',
#     }
#     Group('notes').send({'text': json.dumps(message)})
