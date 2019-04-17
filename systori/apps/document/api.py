from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

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
