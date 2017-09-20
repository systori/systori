import json

from channels import Group

from django.templatetags.l10n import localize
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Note


@receiver(post_save, sender=Note)
def send_notes_update(sender, instance, **kwargs):
    Group('notes').send({
        'text': json.dumps({
            'user': str(instance.worker),
            'created': localize(instance.created),
            'text': instance.text
        })
    })
