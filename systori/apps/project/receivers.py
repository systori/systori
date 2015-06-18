from django.db.models.signals import post_save
from django.dispatch import receiver
from ..document.models import Proposal
from ..task.models import Job


@receiver(post_save, sender=Proposal)
def proposal_save_handler(sender, instance, created, **kwargs):
    if created and instance.project.is_prospective:
        instance.project.begin_tendering()
        instance.project.save()

    elif instance.is_approved and instance.project.is_tendering:
        instance.project.begin_planning()
        instance.project.save()


@receiver(post_save, sender=Job)
def job_save_handler(sender, instance, created, **kwargs):
    if instance.is_started and instance.project.is_planning:
        instance.project.begin_executing()
        instance.project.save()
