from django.http import HttpResponse

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from systori.apps.main.swagger_schema import SwaggerSchema
from systori.apps.project.models import Project
from systori.apps.user.permissions import HasStaffAccess

from systori.apps.document.serializers import (
    DocumentTemplateSerializer,
    TimesheetSerializer,
    ProposalSerializer,
    ProposalPDFOptionsSerializer,
    PaymentSerializer,
    InvoiceSerializer,
    AdjustmentSerializer,
    RefundSerializer,
)
from systori.apps.document.models import (
    DocumentTemplate,
    Timesheet,
    Proposal,
    Payment,
    Invoice,
    Adjustment,
    Refund,
)
from systori.apps.document.type.proposal import ProposalRenderer

PDF_RESPONSE = openapi.Response("PDF", openapi.Schema("PDF", type=openapi.TYPE_FILE))


class DocumentTemplateModelViewSet(ModelViewSet):
    queryset = DocumentTemplate.objects.all()
    serializer_class = DocumentTemplateSerializer
    permission_classes = (HasStaffAccess,)
    basename = "documenttemplate"

    @action(methods=["get"], detail=True, url_path="project-(?P<project_pk>\d+)")
    def for_project(self, request, pk, project_pk):
        project = Project.objects.get(id=project_pk)
        template = self.get_object()
        rendered = template.render(project)
        return Response(rendered)


class TimesheetModelViewSet(ModelViewSet):
    queryset = Timesheet.objects.all()
    serializer_class = TimesheetSerializer
    permission_classes = (HasStaffAccess,)


class ProposalModelViewSet(ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = (HasStaffAccess,)

    @swagger_auto_schema(
        method="GET",
        auto_schema=SwaggerSchema,
        query_serializer=ProposalPDFOptionsSerializer,
        responses={200: PDF_RESPONSE},
        operation_id="document_render_proposal_pdf",
        produces=["application/pdf"],
    )
    @action(methods=["get"], detail=True)
    def render_pdf(self, request, pk=None, *args, **kwargs):
        query_params = (request.query_params or {}).copy()
        query_params["format"] = query_params.get(
            "format", self.kwargs.get("format", None)
        )
        serializer = ProposalPDFOptionsSerializer(data=query_params)
        serializer.is_valid(raise_exception=True)

        json = self.get_object().json
        letterhead = self.get_object().letterhead
        invalid_options = ["download"]
        options = serializer.validated_data.copy()
        for invalid_option in invalid_options:
            options.pop(invalid_option, None)
        renderer = ProposalRenderer(json, letterhead, **options)
        pdf = renderer.pdf

        response = HttpResponse(pdf, content_type="application/pdf")
        pdf_format = serializer.validated_data["format"]
        filename = f"proposal-{pk}-{pdf_format}.pdf".lower()
        if serializer.validated_data["download"]:
            content_disposition = "attachment; filename=%s" % filename
        else:
            content_disposition = "inline; filename=%s" % filename

        response["Content-Disposition"] = content_disposition
        return response


class PaymentModelViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (HasStaffAccess,)


class InvoiceModelViewSet(ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = (HasStaffAccess,)


class AdjustmentModelViewSet(ModelViewSet):
    queryset = Adjustment.objects.all()
    serializer_class = AdjustmentSerializer
    permission_classes = (HasStaffAccess,)


class RefundModelViewSet(ModelViewSet):
    queryset = Refund.objects.all()
    serializer_class = RefundSerializer
    permission_classes = (HasStaffAccess,)
