import os
import mimetypes
from datetime import datetime, date
from dateutil.rrule import rrule, MONTHLY
from calendar import monthrange
from collections import OrderedDict, namedtuple

from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.views.generic import View, ListView, FormView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from django.forms.fields import DateField
from django.db.models.functions import ExtractYear

from systori.lib.accounting.tools import Amount
from ..project.models import Project, Job
from ..timetracking.models import Timer
from ..accounting.constants import TAX_RATE
from .models import Proposal, Invoice, Adjustment, Payment, Refund, Timesheet
from .models import DocumentTemplate, Letterhead, DocumentSettings
from .models import Attachment, FileAttachment
from .forms import ProposalForm, InvoiceForm, AdjustmentForm, PaymentForm, RefundForm
from .forms import LetterheadCreateForm, LetterheadUpdateForm, DocumentSettingsForm
from .forms import TimesheetForm, TimesheetListFilterForm
from .utils import get_weekday_names_numbers_and_mondays
from . import type as pdf_type


def monthdelta(date, delta):
    m, y = (date.month + delta) % 12, date.year + (date.month + delta - 1) // 12
    if not m:
        m = 12
    d = min(date.day, monthrange(y, m)[1])
    return date.replace(day=d, month=m, year=y)


class BaseDocumentViewMixin:
    def get_form_kwargs(self):
        kwargs = {"jobs": self.request.project.jobs.prefetch_related("account")}

        if not self.object:
            self.object = self.model(project=self.request.project)
            self.object.json["jobs"] = []

        kwargs["instance"] = self.object

        kwargs["initial"] = {}
        for field in self.form_class._meta.fields:
            if field in self.object.json:
                form_field = self.form_class.base_fields[field]
                if isinstance(form_field, DateField):
                    kwargs["initial"][field] = form_field.clean(self.object.json[field])
                else:
                    kwargs["initial"][field] = self.object.json[field]

        if self.request.method == "POST":
            kwargs["data"] = self.request.POST.copy()

        return kwargs

    def get_success_url(self):
        return self.request.project.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["TAX_RATE"] = TAX_RATE
        return context

    def get_form(self):
        # document forms are very expensive to create
        if not hasattr(self, "_cached_form"):
            self._cached_form = super().get_form()
        return self._cached_form


class AccountingDocumentViewMixin(BaseDocumentViewMixin):
    def get_queryset(self):
        return self.model.objects.prefetch_related("transaction").all()


class DeleteViewMixin(DeleteView):
    def get_success_url(self):
        return self.request.project.get_absolute_url()


class InvoiceViewMixin(AccountingDocumentViewMixin):
    model = Invoice
    form_class = InvoiceForm
    template_name = "accounting/invoice_form.html"


class InvoiceCreate(InvoiceViewMixin, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if "previous_pk" in self.kwargs:
            previous = Invoice.objects.get(id=self.kwargs["previous_pk"])
            self.object.parent = previous.parent if previous.parent else previous
            # copy basic values from previous invoice
            for field in [
                "title",
                "header",
                "footer",
                "add_terms",
                "vesting_start",
                "vesting_end",
            ]:
                kwargs["initial"][field] = previous.json[field]
            # copy the list of jobs
            self.object.json["jobs"] = [
                {"job.id": debit["job.id"], "is_invoiced": True}
                for debit in previous.json["jobs"]
            ]
        return kwargs


class InvoiceUpdate(InvoiceViewMixin, UpdateView):
    pass


class InvoiceTransition(SingleObjectMixin, View):
    model = Invoice

    def get(self, request, *args, **kwargs):
        doc = self.get_object()

        transition = None
        for t in doc.get_available_status_transitions():
            if t.name == kwargs["transition"]:
                transition = t
                break

        if transition:
            getattr(doc, transition.name)()
            doc.save()

        return HttpResponseRedirect(reverse("project.view", args=[doc.project.id]))


class InvoiceDelete(DeleteViewMixin):
    model = Invoice
    template_name = "accounting/invoice_confirm_delete.html"


class AdjustmentViewMixin(AccountingDocumentViewMixin):
    model = Adjustment
    form_class = AdjustmentForm
    template_name = "accounting/adjustment_form.html"


class AdjustmentCreate(AdjustmentViewMixin, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if "invoice_pk" in self.kwargs:
            invoice = Invoice.objects.get(id=self.kwargs["invoice_pk"])
            self.object.invoice = invoice
            kwargs["instance"].json["jobs"] = [
                {
                    "job.id": job["job.id"],
                    "invoiced": job["debit"],
                    "corrected": job["debit"],
                }
                for job in invoice.json["jobs"]
            ]
        return kwargs


class AdjustmentUpdate(AdjustmentViewMixin, UpdateView):
    pass


class AdjustmentDelete(DeleteViewMixin):
    model = Adjustment
    template_name = "accounting/adjustment_confirm_delete.html"


class PaymentViewMixin(AccountingDocumentViewMixin):
    model = Payment
    form_class = PaymentForm
    template_name = "accounting/payment_form.html"


class PaymentCreate(PaymentViewMixin, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if "invoice_pk" in self.kwargs:
            invoice = Invoice.objects.get(id=self.kwargs["invoice_pk"])
            self.object.invoice = invoice
            kwargs["initial"].update(
                {"payment": invoice.json.get("corrected", invoice.json["debit"]).gross}
            )
            kwargs["instance"].json["jobs"] = [
                {
                    "job.id": job["job.id"],
                    "invoiced": job.get("corrected", job["debit"]),
                    "split": job.get("corrected", job["debit"]),
                }
                for job in invoice.json["jobs"]
            ]
        return kwargs


class PaymentUpdate(PaymentViewMixin, UpdateView):
    pass


class PaymentDelete(DeleteViewMixin):
    model = Payment
    template_name = "accounting/payment_confirm_delete.html"


class RefundViewMixin(AccountingDocumentViewMixin):
    model = Refund
    form_class = RefundForm
    template_name = "accounting/refund_form.html"


class RefundCreate(RefundViewMixin, CreateView):
    pass


class RefundUpdate(RefundViewMixin, UpdateView):
    pass


class RefundDelete(DeleteViewMixin):
    model = Refund
    template_name = "accounting/refund_confirm_delete.html"


TimesheetMonth = namedtuple(
    "TimesheetMonth", ("date", "can_generate", "count", "timesheets")
)


class TimesheetsList(FormView):
    template_name = "document/timesheets_list.html"
    form_class = TimesheetListFilterForm
    success_url = "."

    def form_valid(self, form, **kwargs):
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]
        context = self.get_context_data(start_date, end_date, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, start_date=None, end_date=None, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        if not start_date:
            first_year, first_month = (
                Timesheet.objects.first().document_date.year,
                Timesheet.objects.first().document_date.month,
            )
            start_date = date(first_year, first_month, 1)
            start_date = monthdelta(today, -2)
            start_date.replace(day=1)
        if not end_date:
            end_date = today
        selected_months = [
            dt for dt in rrule(MONTHLY, dtstart=start_date, until=end_date)
        ]
        months = []
        for dt in reversed(selected_months):
            months.append(
                TimesheetMonth(
                    date(dt.year, dt.month, 1),
                    can_generate=(
                        (dt.month == today.month or dt.month == today.month - 1)
                        and Timer.objects.month(dt.year, dt.month).exists()
                    ),
                    count=Timesheet.objects.period(dt.year, dt.month).count(),
                    timesheets=Timesheet.objects.select_related("worker__user")
                    .period(dt.year, dt.month)
                    .all(),
                )
            )
        context["months"] = months
        return context


class TimesheetUpdate(UpdateView):
    model = Timesheet
    form_class = TimesheetForm
    template_name = "document/timesheet_form.html"

    def get_initial(self):
        return {key: self.object.json[key] for key in Timesheet.initial.keys()}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lookup = dict(Timer.KIND_CHOICES)
        lookup.update(
            {
                "payables": _("Total"),
                "overtime": _("Overtime"),
                "compensation": _("Compensation"),
            }
        )
        json = self.object.json
        (
            context["daynames"],
            context["daynumbers"],
            context["mondays"],
        ) = get_weekday_names_numbers_and_mondays(
            json["first_weekday"], json["total_days"], False
        )
        context["rows"] = [
            (t, lookup[t], json[t], json[t + "_total"])
            for t in [
                "work",
                "vacation",
                "sick",
                "public_holiday",
                "paid_leave",
                "unpaid_leave",
                "payables",
                "overtime",
                "compensation",
            ]
        ]
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        saved = False
        if form.is_valid():
            form.save()
            saved = True
        return self.render_to_response(self.get_context_data(saved=saved, form=form))


class TimesheetsGenerateView(View):
    def get(self, request, *args, **kwargs):
        year, month = int(kwargs["year"]), int(kwargs["month"])
        doc_date = timezone.localdate()
        if (doc_date.year, doc_date.month) != (year, month):
            doc_date = date(year, month, monthrange(year, month)[1])
        Timesheet.generate(doc_date)
        return HttpResponseRedirect(reverse("timesheets"))


class InvoiceList(ListView):
    model = Invoice
    template_name = "accounting/invoice_list.html"

    def get(self, request, *args, **kwargs):
        self.status_filter = self.kwargs.get("status_filter", "all")
        self.selected_year = self.kwargs.get("selected_year", datetime.now().year)
        return super().get(self, request, *args, **kwargs)

    def get_queryset(self, model=model, get_years=None):
        qs = (
            model.objects.prefetch_related("project")
            .prefetch_related("parent")
            .order_by("-document_date", "invoice_no")
        )

        if get_years:  # dedicated query
            return (
                qs.annotate(year=ExtractYear("document_date"))
                .order_by("-year")
                .distinct("year")
                .values("year")
            )  # from new to old years

        if self.status_filter == "draft":
            qs = qs.filter(status="draft")
        elif self.status_filter == "sent":
            qs = qs.filter(status="sent")
        elif self.status_filter == "paid":
            qs = qs.filter(status="paid")
        elif self.status_filter == "all":
            pass  # qs can stay as it is
        else:
            raise ValueError(f"can't match status_filter with: {self.status_filter}")

        return qs.filter(document_date__gte=date(int(self.selected_year), 1, 1)).filter(
            document_date__lte=date(int(self.selected_year), 12, 31)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_filter"] = self.status_filter
        context["selected_year"] = self.selected_year

        years = self.get_queryset(get_years=True)
        qs = self.get_queryset()

        context["years"] = [year["year"] for year in years]
        context["invoice_count"] = qs.count()

        months = OrderedDict()
        for invoice in qs:
            doc_date = date(invoice.document_date.year, invoice.document_date.month, 1)
            month = months.setdefault(
                doc_date, {"invoices": [], "debit": Amount.zero()}
            )
            month["debit"] += invoice.json["debit"]
            month["invoices"].append(invoice)

        context["invoice_groups"] = months

        return context


class DocumentRenderView(SingleObjectMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(self.pdf(), content_type="application/pdf")

    def pdf(self):
        raise NotImplementedError


class TimesheetsListPDF(DocumentRenderView):
    def pdf(self):
        year, month = int(self.kwargs["year"]), int(self.kwargs["month"])
        queryset = Timesheet.objects.period(year, month)
        letterhead = DocumentSettings.objects.first().timesheet_letterhead
        renderer = pdf_type.timesheet.TimesheetRenderer(queryset, letterhead)
        return renderer.pdf


class TimesheetPDF(DocumentRenderView):
    model = Timesheet

    def pdf(self):
        letterhead = DocumentSettings.objects.first().timesheet_letterhead
        renderer = pdf_type.timesheet.TimesheetRenderer([self.get_object()], letterhead)
        return renderer.pdf


class InvoicePDF(DocumentRenderView):
    model = Invoice

    def pdf(self):
        json = self.get_object().json
        letterhead = self.get_object().letterhead
        payment_details = self.request.GET.get("payment_details", False)
        renderer = pdf_type.invoice.InvoiceRenderer(
            json, letterhead, payment_details, self.kwargs["format"]
        )
        return renderer.pdf


class InvoiceHTML(SingleObjectMixin, View):
    model = Invoice

    def get(self, request, *args, **kwargs):
        json = self.get_object().json
        letterhead = self.get_object().letterhead
        payment_details = self.request.GET.get("payment_details", False)
        renderer = pdf_type.invoice.InvoiceRenderer(
            json, letterhead, payment_details, None
        )
        return HttpResponse(renderer.html)


class AdjustmentPDF(DocumentRenderView):
    model = Adjustment

    def pdf(self):
        json = self.get_object().json
        letterhead = self.get_object().letterhead
        return pdf_type.adjustment.render(json, letterhead, self.kwargs["format"])


class PaymentPDF(DocumentRenderView):
    model = Payment

    def pdf(self):
        json = self.get_object().json
        letterhead = self.get_object().letterhead
        return pdf_type.payment.render(json, letterhead, self.kwargs["format"])


class RefundPDF(DocumentRenderView):
    model = Refund

    def pdf(self):
        json = self.get_object().json
        letterhead = self.get_object().letterhead
        return pdf_type.refund.render(json, letterhead, self.kwargs["format"])


class ProposalPDF(DocumentRenderView):
    model = Proposal

    def pdf(self):
        json = self.get_object().json
        letterhead = self.get_object().letterhead
        with_lineitems = self.request.GET.get("with_lineitems", False)
        only_groups = self.request.GET.get("only_groups", False)
        only_task_names = self.request.GET.get("only_task_names", False)
        technical_listing = self.request.GET.get("technical_listing", False)
        renderer = pdf_type.proposal.ProposalRenderer(
            json,
            letterhead,
            with_lineitems,
            only_groups,
            only_task_names,
            technical_listing,
            self.kwargs["format"],
        )
        return renderer.pdf


class ProposalHTML(SingleObjectMixin, View):
    model = Proposal

    def get(self, request, *args, **kwargs):
        json = self.get_object().json
        letterhead = self.get_object().letterhead
        with_lineitems = self.request.GET.get("with_lineitems", False)
        only_groups = self.request.GET.get("only_groups", False)
        only_task_names = self.request.GET.get("only_task_names", False)
        technical_listing = self.request.GET.get("technical_listing", False)
        renderer = pdf_type.proposal.ProposalRenderer(
            json,
            letterhead,
            with_lineitems,
            only_groups,
            only_task_names,
            technical_listing,
            None,
        )
        return HttpResponse(renderer.html)


class ProposalViewMixin(BaseDocumentViewMixin):
    model = Proposal
    form_class = ProposalForm


class ProposalCreate(ProposalViewMixin, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"].json["jobs"] = []
        previous_proposal = self.model.objects.filter(
            project=self.request.project
        ).last()
        if previous_proposal:
            for field in ["title", "header", "footer", "add_terms"]:
                kwargs["initial"][field] = previous_proposal.json[field]
        return kwargs


class ProposalUpdate(ProposalViewMixin, UpdateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.object
        return kwargs


class ProposalTransition(SingleObjectMixin, View):
    model = Proposal

    def get(self, request, *args, **kwargs):
        doc = self.get_object()

        transition = None
        for t in doc.get_available_status_transitions():
            if t.name == kwargs["transition"]:
                transition = t
                break

        if transition:
            getattr(doc, transition.name)()
            doc.save()

        return HttpResponseRedirect(reverse("project.view", args=[doc.project.id]))


class ProposalDelete(DeleteView):
    model = Proposal

    def get_success_url(self):
        return reverse("project.view", args=[self.object.project.id])


# Evidence


class ProjectEvidenceHTML(SingleObjectMixin, View):
    model = Project

    def get(self, request, *args, **kwargs):
        doc_settings = DocumentSettings.get_for_language(get_language())
        letterhead = doc_settings.evidence_letterhead
        renderer = pdf_type.evidence.EvidenceRenderer(self.request.project, letterhead)
        return HttpResponse(renderer.html)


class ProjectEvidencePDF(DocumentRenderView):
    model = Project

    def pdf(self):
        doc_settings = DocumentSettings.get_for_language(get_language())
        letterhead = doc_settings.evidence_letterhead
        renderer = pdf_type.evidence.EvidenceRenderer(self.request.project, letterhead)
        return renderer.pdf


class JobEvidencePDF(DocumentRenderView):
    model = Job

    def pdf(self):
        doc_settings = DocumentSettings.get_for_language(get_language())
        letterhead = doc_settings.evidence_letterhead
        renderer = pdf_type.evidence.EvidenceRenderer(
            self.model.objects.get(id=self.kwargs.get("job_pk")), letterhead
        )
        return renderer.pdf


class JobEvidenceHTML(SingleObjectMixin, View):
    model = Job

    def get(self, request, *args, **kwargs):
        doc_settings = DocumentSettings.get_for_language(get_language())
        letterhead = doc_settings.evidence_letterhead
        renderer = pdf_type.evidence.EvidenceRenderer(
            self.model.objects.get(id=self.kwargs.get("job_pk")), letterhead
        )
        return HttpResponse(renderer.html)


# Itemized List


class ItemizedListingPDF(DocumentRenderView):
    model = Project

    def pdf(self):
        doc_settings = DocumentSettings.get_for_language(get_language())
        letterhead = doc_settings.itemized_letterhead
        return pdf_type.itemized_listing.render(
            self.request.project, letterhead, self.kwargs["format"]
        )


# Document Template


class DocumentTemplateView(DetailView):
    model = DocumentTemplate


class DocumentTemplateCreate(CreateView):
    model = DocumentTemplate
    fields = "__all__"
    success_url = reverse_lazy("templates")


class DocumentTemplateUpdate(UpdateView):
    model = DocumentTemplate
    fields = "__all__"
    success_url = reverse_lazy("templates")


class DocumentTemplateDelete(DeleteView):
    model = DocumentTemplate
    success_url = reverse_lazy("templates")


# Letterhead


class LetterheadCreate(CreateView):
    form_class = LetterheadCreateForm
    model = Letterhead

    def get_success_url(self):
        return reverse("letterhead.update", args=[self.object.id])


class LetterheadUpdate(UpdateView):
    model = Letterhead
    form_class = LetterheadUpdateForm

    def get_success_url(self):
        return reverse("letterhead.update", args=[self.object.id])


class LetterheadDelete(DeleteView):
    model = Letterhead
    success_url = reverse_lazy("templates")


# Document Settings


class DocumentSettingsCreate(CreateView):
    model = DocumentSettings
    form_class = DocumentSettingsForm
    success_url = reverse_lazy("templates")


class DocumentSettingsUpdate(UpdateView):
    model = DocumentSettings
    form_class = DocumentSettingsForm
    success_url = reverse_lazy("templates")


class DocumentSettingsDelete(DeleteView):
    model = DocumentSettings
    success_url = reverse_lazy("templates")


# Attachments


class UploadAttachment(SingleObjectMixin, View):
    def post(self, request, *args, **kwargs):
        task = self.get_object()
        if request.FILES:
            attachment = Attachment.objects.create(
                project=request.project, content_object=task
            )
            file = FileAttachment.objects.create(
                attachment=attachment,
                file=request.FILES["attachment"],
                worker=self.request.worker,
            )
            attachment.current = file
            attachment.save()
        return HttpResponseRedirect(self.request.POST["redirect"])


class DownloadAttachment(SingleObjectMixin, View):
    model = Attachment

    def get(self, request, *args, **kwargs):
        attachment = self.get_object()
        file_attachment = attachment.current
        filename = os.path.basename(file_attachment.file.name)
        response = HttpResponse(
            file_attachment.file, content_type=mimetypes.guess_type(filename)[0]
        )
        # response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
