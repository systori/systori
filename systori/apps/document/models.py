from collections import OrderedDict
from itertools import chain
from datetime import date, timedelta
from decimal import Decimal

from django.db import models
from django.db.models.query import QuerySet
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import localtime, now
from django.utils.formats import date_format
from django_fsm import FSMField, transition
from jsonfield import JSONField

from systori.lib import date_utils
from systori.lib.accounting.tools import Amount, JSONEncoder


class Document(models.Model):
    json = JSONField(default={}, dump_kwargs={'cls': JSONEncoder},
                     load_kwargs={'object_hook': Amount.object_hook, 'parse_float': Decimal})
    created_on = models.DateTimeField(auto_now_add=True)
    document_date = models.DateField(_("Date"), default=date.today, blank=True)
    notes = models.TextField(_("Notes"), blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.__class__.__name__, self.created_on)

    class Meta:
        abstract = True
        ordering = ['id']


class TimesheetQuerySet(QuerySet):

    def period(self, year, month):
        return self.filter(
            document_date__range=date_utils.month_range(year, month)
        )


class Timesheet(Document):

    class Meta(Document.Meta):
        verbose_name = _("Timesheet")
        verbose_name_plural = _("Timesheets")

    letterhead = models.ForeignKey('document.Letterhead', related_name="timesheet_documents", on_delete=models.CASCADE)
    worker = models.ForeignKey('company.Worker', related_name='timesheets', on_delete=models.CASCADE)

    objects = TimesheetQuerySet.as_manager()


class Proposal(Document):

    class Meta(Document.Meta):
        verbose_name = _("Proposal")
        verbose_name_plural = _("Proposals")

    letterhead = models.ForeignKey('document.Letterhead', related_name="proposal_documents", on_delete=models.CASCADE)

    project = models.ForeignKey("project.Project", related_name="proposals", on_delete=models.CASCADE)
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

    letterhead = models.ForeignKey('document.Letterhead', related_name="invoice_documents", on_delete=models.CASCADE)

    invoice_no = models.CharField(_("Invoice No."), max_length=30, unique=True)
    project = models.ForeignKey("project.Project", related_name="invoices", on_delete=models.CASCADE)
    parent = models.ForeignKey("self", related_name="invoices", null=True, on_delete=models.CASCADE)

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

    def set_adjustments(self, adjustments):

        self.json['adjustment'] = Amount.zero()
        self.json['corrected'] = Amount.zero()

        for job in self.json['jobs']:

            adjustment = Amount.zero()
            corrected = Amount.zero()

            for row in adjustments:
                if job['job.id'] == row['job.id']:
                    adjustment = row['adjustment']
                    corrected = row['corrected']
                    break

            job['adjustment'] = adjustment
            self.json['adjustment'] += adjustment

            job['corrected'] = corrected
            self.json['corrected'] += corrected

    def clear_adjustments(self):
        self.json.pop('adjustment', 0)
        self.json.pop('corrected', 0)
        for job in self.json['jobs']:
            job.pop('adjustment', 0)
            job.pop('corrected', 0)

    def set_payment(self, splits):

        self.json['payment'] = Amount.zero()

        for job in self.json['jobs']:

            credit = Amount.zero()

            for row in splits:
                if job['job.id'] == row['job.id']:
                    credit = row['credit']
                    break

            job['payment'] = credit
            self.json['payment'] += credit

    def clear_payment(self):
        self.json.pop('payment', 0)
        for job in self.json['jobs']:
            job.pop('payment', 0)

    def delete(self, **kwargs):
        if self.transaction:
            self.transaction.delete()
        super().delete(**kwargs)


class Adjustment(Document):

    class Meta(Document.Meta):
        verbose_name = _("Adjustment")
        verbose_name_plural = _("Adjustment")

    letterhead = models.ForeignKey('document.Letterhead', related_name="adjustment_documents", on_delete=models.CASCADE)
    project = models.ForeignKey("project.Project", related_name="adjustments", on_delete=models.CASCADE)
    invoice = models.OneToOneField('Invoice', related_name="adjustment", null=True, on_delete=models.SET_NULL)
    transaction = models.OneToOneField('accounting.Transaction', related_name="adjustment", null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '{} {}'.format(self.__class__.__name__, self.created_on)

    def delete(self, **kwargs):
        if self.invoice:
            self.invoice.clear_adjustments()
            self.invoice.save()
        if self.transaction:
            self.transaction.delete()
        super().delete(**kwargs)


class Payment(Document):

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        ordering = ['document_date']

    letterhead = models.ForeignKey('document.Letterhead', related_name="payment_documents", on_delete=models.CASCADE)
    project = models.ForeignKey("project.Project", related_name="payments", on_delete=models.CASCADE)
    invoice = models.OneToOneField('Invoice', related_name="payment", null=True, on_delete=models.SET_NULL)
    transaction = models.OneToOneField('accounting.Transaction', related_name="payment", null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '{} {}'.format(self.__class__.__name__, self.created_on)

    def delete(self, **kwargs):
        if self.invoice:
            self.invoice.clear_payment()
            self.invoice.save()
        if self.transaction:
            self.transaction.delete()
        super().delete(**kwargs)


class Refund(Document):
    letterhead = models.ForeignKey('document.Letterhead', related_name="refund_documents", on_delete=models.CASCADE)
    project = models.ForeignKey("project.Project", related_name="refunds", on_delete=models.CASCADE)
    transaction = models.OneToOneField('accounting.Transaction', related_name="refund", null=True,
                                       on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _("Refund")
        verbose_name_plural = _("Refunds")
        ordering = ['id']

    def __str__(self):
        return '{} {}'.format(self.__class__.__name__, self.created_on)

    def delete(self, **kwargs):
        if self.transaction:
            self.transaction.delete()
        super().delete(**kwargs)


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

        date_now = localtime(now()).date()
        return OrderedDict([
            (_('salutation'), project_contact.contact.salutation),
            (_('firstname'), project_contact.contact.first_name),
            (_('lastname'), project_contact.contact.last_name),
            (_('name'), full_name.strip()),
            (_('today'), date_format(date_now, use_l10n=True)),
            (_('today +14'), date_format(date_now+timedelta(14), use_l10n=True)),
            (_('today +21'), date_format(date_now+timedelta(21), use_l10n=True)),
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
    timesheet_letterhead = models.ForeignKey("Letterhead", null=True, blank=True, on_delete=models.SET_NULL,
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
