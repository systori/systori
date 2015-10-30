from collections import OrderedDict
from datetime import date

from django.db import models
from django.conf import settings
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


class Proposal(Document):
    letterhead = models.ForeignKey('document.Letterhead', related_name="proposal_documents")

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

    @transition(field=status, source=[SENT, DECLINED], target=APPROVED, custom={'label': _("Approve")})
    def approve(self):
        pass

    @property
    def is_approved(self):
        return self.status == Proposal.APPROVED

    @transition(field=status, source=[SENT, APPROVED], target=DECLINED, custom={'label': _("Decline")})
    def decline(self):
        pass

    class Meta:
        verbose_name = _("Proposal")
        verbose_name_plural = _("Proposals")
        ordering = ['id']


class Invoice(Document):
    letterhead = models.ForeignKey('document.Letterhead', related_name="invoice_documents")

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
                value = value.replace('[' + str(var) + ']', str(vars[var]))
            result[key] = value
        return result

    def __str__(self):
        return self.name


class Letterhead(models.Model):
    """
    This Class is responsible for letting the User Upload letterheads/stationaries for his company. In best case it's a
    real PDF with vector based graphics. Can affect printable documents like 'Invoice' or 'Proposal'.
    """
    name = models.CharField(_('Name'), max_length=512)

    # todo: Delete not needed PDF Binaries from FS. Make sure that they are not needed (Use Count?)
    letterhead_pdf = models.FileField(_('Letterhead PDF'), upload_to='letterhead', max_length=100)

    mm = "mm"
    cm = "cm"
    inch = "inch"
    DOCUMENT_UNIT = (
        (mm, "mm"),
        (cm, "cm"),
        (inch, "inch")
    )
    document_unit = models.CharField(_('Document Unit'), max_length=5,
                                     choices=DOCUMENT_UNIT, default=mm)

    top_margin = models.DecimalField(_('Top Margin'), max_digits=4, decimal_places=2)
    right_margin = models.DecimalField(_('Right Margin'), max_digits=4, decimal_places=2)
    bottom_margin = models.DecimalField(_('Bottom Margin'), max_digits=4, decimal_places=2)
    left_margin = models.DecimalField(_('Left Margin'), max_digits=4, decimal_places=2)
    top_margin_next = models.DecimalField(_('Top Margin Next'), max_digits=4, decimal_places=2)

    A6 = "A6"
    A5 = "A5"
    A4 = "A4"
    A3 = "A3"
    A2 = "A2"
    A1 = "A1"
    A0 = "A0"
    LETTER = "LETTER"
    LEGAL = "LEGAL"
    ELEVENSEVENTEEN = "ELEVENSEVENTEEN"
    B6 = "B6"
    B5 = "B5"
    B4 = "B4"
    B3 = "B3"
    B2 = "B2"
    B1 = "B1"
    B0 = "B0"
    DOCUMENT_FORMAT = (
        (A6, _("A6")),
        (A5, _("A5")),
        (A4, _("A4")),
        (A3, _("A3")),
        (A2, _("A2")),
        (A1, _("A1")),
        (A0, _("A0")),
        (LETTER, _("LETTER")),
        (LEGAL, _("LEGAL")),
        (ELEVENSEVENTEEN, _("ELEVENSEVENTEEN")),
        (B6, _("B6")),
        (B5, _("B5")),
        (B4, _("B4")),
        (B3, _("B3")),
        (B2, _("B2")),
        (B1, _("B1")),
        (B0, _("B0")),
    )
    document_format = models.CharField(_('Pagesize'), max_length=30,
                                       choices=DOCUMENT_FORMAT, default=A4)

    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    ORIENTATION = (
        (PORTRAIT, _("Portrait")),
        (LANDSCAPE, _("Landscape"))
    )
    orientation = models.CharField(_('Orientation'), max_length=15,
                                   choices=ORIENTATION, default=PORTRAIT)

    debug = models.BooleanField(_("Debug Mode"), default=True)


class DocumentSettings(models.Model):
    language = models.CharField(_('language'), unique=True, default=settings.LANGUAGE_CODE, choices=settings.LANGUAGES, max_length=2)

    proposal_text = models.ForeignKey(DocumentTemplate, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    invoice_text = models.ForeignKey(DocumentTemplate, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    #proposal_letterhead = models.ForeignKey("Letterhead", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    #invoice_letterhead = models.ForeignKey("Letterhead", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    #evidence_letterhead = models.ForeignKey("Letterhead", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    #itemized_letterhead = models.ForeignKey("Letterhead", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    @staticmethod
    def get_for_language(lang):
        try:
            return DocumentSettings.objects.get(language=lang)
        except DocumentSettings.DoesNotExist:
            return None

