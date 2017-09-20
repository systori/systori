import json
from mistune import markdown

from channels import Group

from django.templatetags.l10n import localize
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from .models import Note


@receiver(post_save, sender=Note)
def send_notes_update(sender, instance, **kwargs):
    message = {
        'user': str(instance.worker),
        'created': localize(instance.created),
        'html': markdown(instance.text)
    }
    if instance.project:
        project_id = instance.project.id
        message.update({
            'project-id': project_id,
            'project-url': reverse('project.view', kwargs={'pk':project_id})
        })
    Group('notes').send({'text': json.dumps(message)})
