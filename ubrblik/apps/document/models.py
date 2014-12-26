from collections import namedtuple
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_fsm import FSMField, transition


class Document(models.Model):
    pdf = models.FileField()
    notes = models.TextField(_("Notes"), blank=True, null=True)
    amount = models.DecimalField(_("Amount"), max_digits=12, decimal_places=2)
    created_on = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return '{} {} {}'.format(self.get_status_display(), self.__class__.__name__, self.created_on)
    class Meta:
        abstract = True


class Proposal(Document):
    project = models.ForeignKey("project.Project", related_name="proposals")
    jobs = models.ManyToManyField("task.Job", related_name="proposals")

    NEW = "new"
    SENT = "sent"
    APPROVED = "approved"
    DECLINED = "declined"

    STATE_CHOICES = (
        (NEW, _("New")),
        (SENT, _("Sent")),
        (APPROVED, _("Approved")),
        (DECLINED, _("Declined"))
    )

    status = FSMField(default=NEW, choices=STATE_CHOICES)

    @transition(field=status, source=NEW, target=SENT, custom={'label': _("Send")})
    def send(self):
        pass

    @transition(field=status, source=SENT, target=APPROVED, custom={'label': _("Approve")})
    def approve(self):
        for job in self.jobs.all():
            job.status = job.APPROVED
            job.save()

    @transition(field=status, source=SENT, target=DECLINED, custom={'label': _("Decline")})
    def decline(self):
        for job in self.jobs.all():
            job.status = job.DRAFT
            job.save()

    def delete(self, using=None):
        for job in self.jobs.all():
            job.status = job.DRAFT
            job.save()
        super(Proposal, self).delete(using)

    class Meta:
        verbose_name = _("Proposal")
        verbose_name_plural = _("Proposals")
        ordering = ['id']


class Invoice(Document):
    project = models.ForeignKey("project.Project", related_name="invoices")
    jobs = models.ManyToManyField("task.Job", related_name="invoices")

    NEW = "new"
    SENT = "sent"
    PAID = "paid"
    DISPUTED = "disputed"

    STATE_CHOICES = (
        (NEW, _("New")),
        (SENT, _("Sent")),
        (PAID, _("Paid")),
        (DISPUTED, _("Disputed"))
    )

    status = FSMField(default=NEW, choices=STATE_CHOICES)

    @transition(field=status, source=NEW, target=SENT, custom={'label': _("Send")})
    def send(self):
        pass

    @transition(field=status, source=SENT, target=PAID, custom={'label': _("Pay")})
    def pay(self):
        pass

    @transition(field=status, source=SENT, target=DISPUTED, custom={'label': _("Dispute")})
    def dispute(self):
        pass

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")
        ordering = ['id']