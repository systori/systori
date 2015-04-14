import os.path
from collections import OrderedDict
from datetime import date, datetime
from subprocess import Popen, PIPE
from django.template.loader import get_template
from django.template import Context
from django.core.files.base import ContentFile

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_fsm import FSMField, transition

from systori import settings


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
    document_date = models.DateField(_("Date"), default=date.today, blank=True)

    email_pdf = models.FileField(upload_to=generate_file_path)
    email_latex = models.FileField(upload_to=generate_file_path)

    print_pdf = models.FileField(upload_to=generate_file_path)
    print_latex = models.FileField(upload_to=generate_file_path)

    json = models.FileField(upload_to=generate_file_path)

    def __str__(self):
        return '{} {} {}'.format(self.get_status_display(),
                                 self.__class__.__name__, self.created_on)

    class Meta:
        abstract = True

    def get_document_context(self, add_terms):
        project_contact = self.project.billable_contact
        return {
          'doc': self,
          'add_terms': add_terms,
          'add_letterhead': False,
          'contact': project_contact.contact,
          'project_contact': project_contact # this has the association attribute
        }

    def generate_document(self, add_terms=True):

        template = get_template(os.path.join("document/latex", self.latex_template))

        context = Context(self.get_document_context(add_terms))

        print_latex = template.render(context).encode('utf-8')
        self.print_latex.save('print.tex', ContentFile(print_latex), save=False)

        context.update({'add_letterhead': True})
        email_latex = template.render(context).encode('utf-8')
        self.email_latex.save('email.tex', ContentFile(email_latex), save=False)

        dir_path = os.path.dirname(self.email_latex.path)

        # generate pdf files
        for format, latex in [('email', email_latex), ('print', print_latex)]:

            for i in range(3):
                process = Popen(
                    ['pdflatex', '-output-directory', dir_path,
                     '-jobname', format],
                    stdin=PIPE,
                    stdout=PIPE,
                    cwd=settings.LATEX_WORKING_DIR
                    )
                process.communicate(latex)

            setattr(self, format+'_pdf', os.path.join(dir_path, format+'.pdf'))

        # save file paths to database
        self.save()


class Proposal(Document):
    project = models.ForeignKey("project.Project", related_name="proposals")
    jobs = models.ManyToManyField("task.Job", verbose_name=_('Jobs'),
                                  related_name="proposals")

    latex_template = models.CharField(_('Template'), max_length=512, default="proposal.tex")

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

    @transition(field=status, source=NEW, target=SENT,
                custom={'label': _("Send")})
    def send(self):
        pass

    @transition(field=status, source=SENT, target=APPROVED,
                custom={'label': _("Approve")})
    def approve(self):
        for job in self.jobs.all():
            job.status = job.APPROVED
            job.save()

    @transition(field=status, source=SENT, target=DECLINED,
                custom={'label': _("Decline")})
    def decline(self):
        for job in self.jobs.all():
            job.status = job.DRAFT
            job.save()

    def delete(self, using=None):
        for job in self.jobs.all():
            job.status = job.DRAFT
            job.save()
        super(Proposal, self).delete(using)

    def get_document_context(self, add_terms):
        context = super(Proposal, self).get_document_context(add_terms)
        context['jobs'] = self.jobs.all()
        return context

    class Meta:
        verbose_name = _("Proposal")
        verbose_name_plural = _("Proposals")
        ordering = ['id']


class Invoice(Document):
    invoice_no = models.CharField(_("Invoice No."), max_length=30)

    project = models.ForeignKey("project.Project", related_name="invoices")

    latex_template = models.CharField(_('Template'), max_length=512, default="invoice.tex")

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

    def get_document_context(self, add_terms):
        context = super(Invoice, self).get_document_context(add_terms)
        context['project'] = self.project
        return context

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")
        ordering = ['id']


class Evidence(models.Model):
    notes = models.TextField(_("Notes"), blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    document_date = models.DateField(_("Date"), default=date.today, blank=True)

    print_pdf = models.FileField(upload_to=generate_file_path)
    print_latex = models.FileField(upload_to=generate_file_path)

    json = models.FileField(upload_to=generate_file_path)

    project = models.ForeignKey("project.Project", related_name="evidences")
    jobs = models.ManyToManyField("task.Job", related_name="evidences")

    LATEX_TEMPLATE = "document/latex/evidence.tex"

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")
        ordering = ['id']

    def generate_document(self, add_terms=True):

        template = get_template(self.LATEX_TEMPLATE)

        # generate latex files
        context = Context({
          'doc': self,
          'jobs': self.jobs.all(),
        })
        print_latex = template.render(context).encode('utf-8')
        self.print_latex.save('print.tex', ContentFile(print_latex), save=False)

        dir_path = os.path.dirname(self.print_latex.path)

        # generate pdf files
        for format, latex in [('print', print_latex)]:

            for i in range(2):
                process = Popen(
                    ['pdflatex', '-output-directory', dir_path,
                     '-jobname', format],
                    stdin=PIPE,
                    stdout=PIPE,
                    cwd=settings.LATEX_WORKING_DIR
                    )
                process.communicate(latex)

            setattr(self, format+'_pdf', os.path.join(dir_path, format+'.pdf'))

        # save file paths to database
        self.save()


class SampleContact:
    salutation = _('Mr')
    first_name = _('John')
    last_name = _('Smith')


class SampleProjectContact:
    contact = SampleContact


class DocumentTemplate(models.Model):
    name = models.CharField(_('Name'), max_length=512)
    header = models.TextField(_("Header"))
    footer = models.TextField(_("Footer"))

    PROPOSAL = "proposal"
    INVOICE = "invoice"
    EVIDENCE = "evidence"
    DOCUMENT_TYPE = (
        (PROPOSAL, _("Proposal")),
        (INVOICE, _("Invoice")),
        (EVIDENCE, _("Evidence")),
    )
    document_type = models.CharField(_('Document Type'), max_length=128,
                                     choices=DOCUMENT_TYPE, default=PROPOSAL)

    class Meta:
        verbose_name = _("Document Template")
        verbose_name_plural = _("Document Templates")
        ordering = ['name']

    def vars(self, project=None):
        project_contact = project.billable_contact if project \
            else SampleProjectContact
        full_name = '%s %s %s' % (
            project_contact.contact.salutation,
            project_contact.contact.first_name,
            project_contact.contact.last_name)

        return OrderedDict([
            (_('salutation'), project_contact.contact.salutation),
            (_('firstname'), project_contact.contact.first_name),
            (_('lastname'), project_contact.contact.last_name),
            (_('name'), full_name.strip())
        ])

    def render(self, project=None):
        vars = self.vars(project)
        result = {
            'header': self.header,
            'footer': self.footer
        }
        for key in result:
            value = result[key]
            for var in vars:
                value = value.replace('['+str(var)+']', str(vars[var]))
            result[key] = value
        return result

    def __str__(self):
        return self.name
