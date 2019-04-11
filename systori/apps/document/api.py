from django.conf.urls import url
from rest_framework import views
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from systori.apps.project.models import Project
from systori.apps.user.permissions import HasStaffAccess

from systori.apps.document.serializers import (
    DocumentTemplateSerializer,
    TimesheetSerializer,
    ProposalSerializer,
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


class DocumentTemplateModelViewSet(ModelViewSet):
    queryset = DocumentTemplate.objects.all()
    serializer_class = DocumentTemplateSerializer
    permission_classes = (HasStaffAccess,)


class DocumentTemplateView(views.APIView):
    permissions = (HasStaffAccess,)

    def get(self, request, project_pk=None, template_pk=None, **kwargs):
        project = Project.objects.get(id=project_pk)
        template = DocumentTemplate.objects.get(id=template_pk)
        rendered = template.render(project)
        return Response(rendered)


urlpatterns = [
    url(
        r"^document-template/project-(?P<project_pk>\d+)/template-(?P<template_pk>\d+)?$",
        DocumentTemplateView.as_view(),
        name="api.document.template",
    )
]


class TimesheetModelViewSet(ModelViewSet):
    queryset = Timesheet.objects.all()
    serializer_class = TimesheetSerializer
    permission_classes = (HasStaffAccess,)


class ProposalModelViewSet(ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = (HasStaffAccess,)


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
