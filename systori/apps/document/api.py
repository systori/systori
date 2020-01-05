from django.shortcuts import get_object_or_404
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
        # method="GET",
        method="POST",
        auto_schema=SwaggerSchema,
        request_body=ProposalPDFOptionsSerializer,
        # query_serializer=ProposalPDFOptionsSerializer,
        responses={200: PDF_RESPONSE},
        operation_id="document_download_proposal_pdf",
        # Required for api generator but adding this header produces error:
        # "Could not satisfy the request Accept header."
        produces=["application/pdf"],
    )
    # Having a GET request would be ideal, but since the query parameters are part of the url
    # Django never matches urls like download_pdf/?with_lineitem to this method
    # Also query parameters could be provided in any order. so writing a url_path regex would be a pain
    # @action(methods=["GET"], detail=True)
    @action(methods=["POST"], detail=True)
    def download_pdf(self, request, pk=None):
        pdf = None
        serializer = ProposalPDFOptionsSerializer(data=request.data)
        serializer.is_valid()

        json = self.get_object().json
        letterhead = self.get_object().letterhead
        renderer = ProposalRenderer(json, letterhead, **serializer.validated_data)
        pdf = renderer.pdf
        # The drf's Response(pdf, content_type="application/pdf")
        # Returns result in application/json even though application/pdf is provided
        # This fails because a PDF cannot be encoded in json
        return HttpResponse(pdf, content_type="application/pdf")


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
