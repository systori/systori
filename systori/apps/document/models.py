from calendar import monthrange
from collections import OrderedDict
from itertools import chain
from datetime import date, timedelta
from decimal import Decimal

from django.db import models
from django.db.models.query import QuerySet
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import localtime, now
from django.utils.formats import date_format
from django_fsm import FSMField, transition
from jsonfield import JSONField

from systori.lib.accounting.tools import Amount, JSONEncoder

from ..timetracking.models import Timer

from . import type as pdf_type
from .type.font import font_families


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
        first = date(year, month, 1)
        last = date(year, month, monthrange(year, month)[1])
        return self.filter(document_date__range=(first, last))

    def get_previous_or_current(self, worker):
        today = now().date()
        previous_month = today.replace(day=1) - timedelta(days=2)
        for day in (today, previous_month):
            timesheet = self.period(day.year, day.month).filter(worker=worker).first()
            if timesheet:
                return timesheet


class Timesheet(Document):

    class Meta(Document.Meta):
        verbose_name = _("Timesheet")
        verbose_name_plural = _("Timesheets")

    letterhead = models.ForeignKey('document.Letterhead', related_name="timesheet_documents", on_delete=models.PROTECT)
    worker = models.ForeignKey('company.Worker', related_name='timesheets', on_delete=models.CASCADE)

    objects = TimesheetQuerySet.as_manager()

    initial = {
        'work_correction': 0,
        'work_correction_notes': '',
        'overtime_correction': 0,
        'overtime_correction_notes': '',
        'vacation_correction': 0,
        'vacation_correction_notes': '',
    }

    def calculate_vacation_balance(self):
        self.json['vacation_added'] = self.worker.contract.vacation
        self.json['vacation_net'] = self.json['vacation_added'] - self.json['vacation_total']
        self.json['vacation_balance'] = (
            self.json['vacation_transferred'] +
            self.json['vacation_net'] +
            self.json['vacation_correction']
        )

    def calculate_overtime_balance(self):
        self.json['overtime_net'] = self.json['overtime_total'] - self.json['paid_leave_total']
        self.json['overtime_balance'] = (
            self.json['overtime_transferred'] +
            self.json['overtime_net'] +
            self.json['overtime_correction']
        )

    def calculate_final_compensation(self):
        self.json['compensation_final'] = self.json['compensation_total'] + self.json['work_correction']

    def calculate_transferred_amounts(self):
        previous_month = (self.document_date.replace(day=1)-timedelta(days=2))
        previous_query = Timesheet.objects\
            .period(previous_month.year, previous_month.month)\
            .filter(worker=self.worker)
        if previous_query.exists():
            previous = previous_query.get()
            self.json['vacation_transferred'] = previous.json['vacation_balance']
            self.json['overtime_transferred'] = previous.json['overtime_balance']
        else:
            self.json['vacation_transferred'] = 0
            self.json['overtime_transferred'] = 0

    def calculate(self):
        year, month = self.document_date.year, self.document_date.month
        if not self.json:
            self.json = self.initial.copy()
        self.json.update(pdf_type.timesheet.serialize(
            Timer.objects.month(year, month, worker=self.worker).all(),
            year, month
        ))
        self.calculate_transferred_amounts()
        self.calculate_vacation_balance()
        self.calculate_overtime_balance()
        self.calculate_final_compensation()
        return self

    @classmethod
    def generate(cls, day: date):
        assert isinstance(day, date)

        letterhead = DocumentSettings.objects.first().timesheet_letterhead
        current = list(cls.objects.period(day.year, day.month))
        workers = Timer.objects.month(day.year, day.month).get_workers()

        for worker in workers:
            sheet = None
            for ts in current:
                if ts.worker.pk == worker.pk:
                    sheet = ts
                    current.remove(ts)
                    break
            if not sheet:
                sheet = cls(worker=worker)
            sheet.document_date = day
            sheet.letterhead = letterhead
            sheet.calculate()
            sheet.save()

        # cleanup no longer valid timesheets
        for sheet in current:
            sheet.delete()


class Proposal(Document):

    class Meta(Document.Meta):
        verbose_name = _("Proposal")
        verbose_name_plural = _("Proposals")

    letterhead = models.ForeignKey('document.Letterhead', related_name="proposal_documents", on_delete=models.PROTECT)

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

    letterhead = models.ForeignKey('document.Letterhead', related_name="invoice_documents", on_delete=models.PROTECT)

    invoice_no = models.CharField(_("Invoice No."), max_length=30, unique=True)
    project = models.ForeignKey("project.Project", related_name="invoices", on_delete=models.CASCADE)
    parent = models.ForeignKey("self", related_name="invoices", null=True, on_delete=models.SET_NULL)

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

    letterhead = models.ForeignKey('document.Letterhead', related_name="adjustment_documents", on_delete=models.PROTECT)
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

    letterhead = models.ForeignKey('document.Letterhead', related_name="payment_documents", on_delete=models.PROTECT)
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
    letterhead = models.ForeignKey('document.Letterhead', related_name="refund_documents", on_delete=models.PROTECT)
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
    name = models.CharField(_('Name'), max_length=512)
    pdf = models.FileField(_('Letterhead PDF'), upload_to='letterhead', max_length=100)
    file = models.ForeignKey('document.FileAttachment', null=True, on_delete=models.SET_NULL)

    mm = "mm"
    cm = "cm"
    inch = "inch"
    DOCUMENT_UNIT = (
        (mm, "mm"),
        (cm, "cm"),
        (inch, "inch")
    )
    document_unit = models.CharField(_('Document Unit'), max_length=5, choices=DOCUMENT_UNIT, default=mm)

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
    orientation = models.CharField(_('Orientation'), max_length=15, choices=ORIENTATION, default=PORTRAIT)

    debug = models.BooleanField(_("Debug Mode"), default=True)

    FONTS = tuple((font, font) for font in font_families)

    font = models.CharField(_('Font'), max_length=15, choices=FONTS, default=FONTS[0][0])

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


class Attachment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    project = models.ForeignKey('project.Project', null=True, related_name="+", on_delete=models.CASCADE)
    file = models.ForeignKey('document.FileAttachment', null=True, related_name="+", on_delete=models.SET_NULL)

    class Meta:
        ordering = 'head__uploaded',


class FileAttachment(models.Model):
    attachment = models.ForeignKey(Attachment, on_delete=models.CASCADE)
    file = models.FileField(_('File'), upload_to='attachments', max_length=512)
    worker = models.ForeignKey('company.Worker', related_name="+", on_delete=models.PROTECT)
    uploaded = models.DateTimeField(_('Created'), auto_now_add=True)

    class Meta:
        ordering = 'uploaded',
