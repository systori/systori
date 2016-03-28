from collections import OrderedDict
from itertools import chain
from datetime import date
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django_fsm import FSMField, transition
from jsonfield import JSONField

from systori.lib.accounting.tools import Amount, JSONEncoder


class Document(models.Model):
    json = JSONField(default={}, dump_kwargs={'cls': JSONEncoder},
                     load_kwargs={'object_hook': Amount.object_hook, 'parse_float': Decimal})
    created_on = models.DateTimeField(auto_now_add=True)
    document_date = models.DateField(_("Date"), default=date.today, blank=True)
    notes = models.TextField(_("Notes"), blank=True, null=True)

    def __str__(self):
        return '{} {} {}'.format(self.get_status_display(),
                                 self.__class__.__name__, self.created_on)

    class Meta:
        abstract = True
        ordering = ['id']


class Proposal(Document):

    class Meta(Document.Meta):
        verbose_name = _("Proposal")
        verbose_name_plural = _("Proposals")

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


class Invoice(Document):

    class Meta(Document.Meta):
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")

    letterhead = models.ForeignKey('document.Letterhead', related_name="invoice_documents")

    invoice_no = models.CharField(_("Invoice No."), max_length=30)
    project = models.ForeignKey("project.Project", related_name="invoices")
    parent = models.ForeignKey("self", related_name="invoices", null=True)

    transaction = models.OneToOneField('accounting.Transaction', related_name="invoice", null=True, on_delete=models.SET_NULL)

    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"

    STATE_CHOICES = (
        (DRAFT, _("Draft")),
        (SENT, _("Sent")),
        (PAID, _("Paid")),
    )

    status = FSMField(default=DRAFT, choices=STATE_CHOICES)

    @transition(field=status, source=DRAFT, target=SENT, custom={'label': _("Mark Sent")})
    def send(self):
        self.transaction.finalize()

    @transition(field=status, source=SENT, target=PAID, custom={'label': _("Pay")})
    def pay(self):
        pass

    def get_invoices(self):
        assert self.parent is None  # make sure this is a parent invoice
        return chain([self], self.invoices.all())

    @property
    def debited_gross(self):
        if self.json.get('debited_gross'):
            return Decimal(self.json['debited_gross'])
        elif self.json.get('debit_gross'):
            return Decimal(self.json['debit_gross'])
        else:
            return Decimal("0")

    @property
    def balance_gross(self):
        if self.json.get('balance_gross'):
            return Decimal(self.json['balance_gross'])
        # elif debit_gross for backwards compatibility
        elif self.json.get('debit_gross'):
            return Decimal(self.json['debit_gross'])
        else:
            return Decimal("0")


class Adjustment(Document):

    class Meta(Document.Meta):
        verbose_name = _("Adjustment")
        verbose_name_plural = _("Adjustment")

    letterhead = models.ForeignKey('document.Letterhead', related_name="adjustment_documents")
    project = models.ForeignKey("project.Project", related_name="adjustments")
    invoice = models.OneToOneField('Invoice', related_name="adjustment", null=True, on_delete=models.SET_NULL)
    transaction = models.OneToOneField('accounting.Transaction', related_name="adjustment", null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '{} {}'.format(self.__class__.__name__, self.created_on)


class Payment(Document):

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        ordering = ['document_date']

    letterhead = models.ForeignKey('document.Letterhead', related_name="payment_documents")
    project = models.ForeignKey("project.Project", related_name="payments")
    invoice = models.OneToOneField('Invoice', related_name="payment", null=True, on_delete=models.SET_NULL)
    transaction = models.OneToOneField('accounting.Transaction', related_name="payment", null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '{} {}'.format(self.__class__.__name__, self.created_on)


class Refund(Document):
    letterhead = models.ForeignKey('document.Letterhead', related_name="refund_documents")
    project = models.ForeignKey("project.Project", related_name="refunds")
    transaction = models.OneToOneField('accounting.Transaction', related_name="refund", null=True,
                                       on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _("Refund")
        verbose_name_plural = _("Refunds")
        ordering = ['id']

    def __str__(self):
        return '{} {}'.format(self.__class__.__name__, self.created_on)


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

    top_margin = models.DecimalField(_('Top Margin'), max_digits=5, decimal_places=2, default=Decimal("25"))
    right_margin = models.DecimalField(_('Right Margin'), max_digits=5, decimal_places=2, default=Decimal("25"))
    bottom_margin = models.DecimalField(_('Bottom Margin'), max_digits=5, decimal_places=2, default=Decimal("25"))
    left_margin = models.DecimalField(_('Left Margin'), max_digits=5, decimal_places=2, default=Decimal("25"))
    top_margin_next = models.DecimalField(_('Top Margin Next'), max_digits=5, decimal_places=2, default=Decimal("25"))
    bottom_margin_next = models.DecimalField(_('Bottom Margin Next'), max_digits=5, decimal_places=2,
                                             default=Decimal("25"))

    A5 = "A5"
    A4 = "A4"
    A3 = "A3"
    LETTER = "LETTER"
    LEGAL = "LEGAL"
    ELEVENSEVENTEEN = "ELEVENSEVENTEEN"
    B5 = "B5"
    B4 = "B4"
    DOCUMENT_FORMAT = (
        (A5, _("A5")),
        (A4, _("A4")),
        (A3, _("A3")),
        (LETTER, _("LETTER")),
        (LEGAL, _("LEGAL")),
        (ELEVENSEVENTEEN, _("ELEVENSEVENTEEN")),
        (B5, _("B5")),
        (B4, _("B4")),
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

    OPEN_SANS = "OpenSans"
    DROID_SERIF = "DroidSerif"
    TINOS = "Tinos"
    FONT = (
        (OPEN_SANS, "Open Sans"),
        (DROID_SERIF, "Droid Serif"),
        (TINOS, "Tinos")
    )
    font = models.CharField(_('Font'), max_length=15,
                            choices=FONT, default=OPEN_SANS)

    def __str__(self):
        return self.name


class DocumentSettings(models.Model):
    language = models.CharField(_('language'), unique=True, default=settings.LANGUAGE_CODE,
                                choices=settings.LANGUAGES, max_length=2)

    proposal_text = models.ForeignKey(DocumentTemplate, null=True, blank=True, on_delete=models.SET_NULL,
                                      related_name="+")
    invoice_text = models.ForeignKey(DocumentTemplate, null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name="+")

    proposal_letterhead = models.ForeignKey("Letterhead", null=True, blank=True, on_delete=models.SET_NULL,
                                            related_name="+")
    invoice_letterhead = models.ForeignKey("Letterhead", null=True, blank=True, on_delete=models.SET_NULL,
                                           related_name="+")
    evidence_letterhead = models.ForeignKey("Letterhead", null=True, blank=True, on_delete=models.SET_NULL,
                                            related_name="+")
    itemized_letterhead = models.ForeignKey("Letterhead", null=True, blank=True, on_delete=models.SET_NULL,
                                            related_name="+")

    @staticmethod
    def get_for_language(lang):
        try:
            return DocumentSettings.objects.get(language=lang)
        except DocumentSettings.DoesNotExist:
            try:
                return DocumentSettings.objects.first()
            except DocumentSettings.DoesNotExist:
                return None
