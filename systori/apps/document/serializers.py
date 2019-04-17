from rest_framework.serializers import ModelSerializer

from systori.apps.document.models import (
    DocumentTemplate,
    Timesheet,
    Proposal,
    Payment,
    Invoice,
    Adjustment,
    Refund,
)


class DocumentTemplateSerializer(ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = "__all__"


class TimesheetSerializer(ModelSerializer):
    class Meta:
        model = Timesheet
        fields = "__all__"


class ProposalSerializer(ModelSerializer):
    class Meta:
        model = Proposal
        fields = "__all__"


class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class InvoiceSerializer(ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"


class AdjustmentSerializer(ModelSerializer):
    class Meta:
        model = Adjustment
        fields = "__all__"


class RefundSerializer(ModelSerializer):
    class Meta:
        model = Refund
        fields = "__all__"
