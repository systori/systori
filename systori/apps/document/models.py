from collections import OrderedDict
from datetime import date
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_fsm import FSMField, transition
from jsonfield import JSONField


class Document(models.Model):

    json = JSONField(default={})
    json_version = models.CharField(max_length=5)
    amount = models.DecimalField(_("Amount"), max_digits=12, decimal_places=2)
    created_on = models.DateTimeField(auto_now_add=True)
    document_date = models.DateField(_("Date"), default=date.today, blank=True)
    notes = models.TextField(_("Notes"), blank=True, null=True)


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
    jobs = models.ManyToManyField("task.Job", verbose_name=_('Jobs'), related_name="proposals")

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
        pass

    @property
    def is_approved(self):
        return self.status == Proposal.APPROVED
    
    @transition(field=status, source=SENT, target=DECLINED, custom={'label': _("Decline")})
    def decline(self):
        pass

    class Meta:
        verbose_name = _("Proposal")
        verbose_name_plural = _("Proposals")
        ordering = ['id']


class Invoice(Document):
    invoice_no = models.CharField(_("Invoice No."), max_length=30)
    project = models.ForeignKey("project.Project", related_name="invoices")

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
    DOCUMENT_TYPE = (
        (PROPOSAL, _("Proposal")),
        (INVOICE, _("Invoice")),
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
