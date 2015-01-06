import os.path, shutil
from datetime import datetime
from subprocess import Popen, PIPE
from django.template.loader import get_template
from django.template import Context
from django.core.files.base import ContentFile

from collections import namedtuple
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_fsm import FSMField, transition

from ubrblik import settings


def generate_file_path(self, filename):
    if not hasattr(self, '_document_directory_path'):
        doc_type = self.__class__.__name__.lower()
        path_fmt = 'documents/project-{}/%Y_%m_%d_{}_{}'
        path = path_fmt.format(self.project.id, doc_type, self.id)
        self._document_directory_path = datetime.now().strftime(path)
    return os.path.join(self._document_directory_path, filename)


class Document(models.Model):

    notes = models.TextField(_("Notes"), blank=True, null=True)
    amount = models.DecimalField(_("Amount"), max_digits=12, decimal_places=2)
    header = models.TextField(_("Header"))
    footer = models.TextField(_("Footer"))
    created_on = models.DateTimeField(auto_now_add=True)

    pdf = models.FileField(upload_to=generate_file_path)
    latex = models.FileField(upload_to=generate_file_path)
    json = models.FileField(upload_to=generate_file_path)

    def __str__(self):
        return '{} {} {}'.format(self.get_status_display(), self.__class__.__name__, self.created_on)

    class Meta:
        abstract = True

    def generate_document(self):

        template = get_template(self.LATEX_TEMPLATE)

        context = Context({
          'doc': self,
          'jobs': self.jobs.all(),
          'contact': self.project.billable_contact
        })

        rendered_latex = template.render(context).encode('utf-8')

        # create latex file
        self.latex.save('document.tex', ContentFile(rendered_latex), save=False)

        dir_path = os.path.dirname(self.latex.path)

        # create pdf file
        for i in range(2):
            process = Popen(
                ['pdflatex', '-output-directory', dir_path],
                stdin=PIPE,
                stdout=PIPE,
                cwd=settings.LATEX_WORKING_DIR
            )
            process.communicate(rendered_latex)

        self.pdf = os.path.join(dir_path, 'texput.pdf')

        # save file paths to database
        self.save()


class Proposal(Document):
    project = models.ForeignKey("project.Project", related_name="proposals")
    jobs = models.ManyToManyField("task.Job", verbose_name=_('Jobs'), related_name="proposals")

    LATEX_TEMPLATE = "document/latex/proposal.tex"

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

    LATEX_TEMPLATE = "document/latex/invoice.tex"

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