from django.db.models.signals import post_delete
from django.dispatch import receiver
from ..project.models import Job
from .models import Account


@receiver(post_delete, sender=Job)
def job_delete_handler(sender, instance, **kwargs):
    Account.objects.get(id=instance.account_id).delete()
