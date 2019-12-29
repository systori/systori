import rest_framework.serializers as serializers
from drf_yasg.utils import swagger_serializer_method
from rest_framework.fields import JSONField
from rest_framework.serializers import ModelSerializer

from systori.apps.directory.serializers import ContactSerializer
from systori.apps.document.models import (
    Adjustment,
    Document,
    DocumentTemplate,
    Invoice,
    Letterhead,
    Payment,
    Proposal,
    Refund,
    Timesheet,
)
from systori.lib.accounting.tools import JSONEncoder


class AmountSerializer(serializers.Serializer):
    net = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    gross = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    tax = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)

    class Meta:
        fields = ["net", "gross", "tax"]


class DocumentSerializer(serializers.ModelSerializer):
    document_date = serializers.DateField(required=True)

    class Meta:
        model = Document
        fields = ["created_on", "document_date", "notes"]


class DocumentTemplateSerializer(ModelSerializer):
    class Meta:
        model = DocumentTemplate
        fields = "__all__"


class TimesheetSerializer(ModelSerializer):
    class Meta:
        model = Timesheet
        fields = "__all__"


class LetterheadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Letterhead
        fields = "__all__"


class ProposalJobSerializer(serializers.Serializer):
    pk = serializers.IntegerField(required=True, source="job.id")
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=False)
    code = serializers.CharField(required=True)
    estimate = AmountSerializer(required=True)
    is_attached = serializers.BooleanField(required=False)

    class Meta:
        fields = "__all__"


class ProposalSerializer(DocumentSerializer):
    json = JSONField(encoder=JSONEncoder, required=False, binary=True)
    letterhead = LetterheadSerializer(required=False)
    estimate_total = AmountSerializer(required=False, source="json.estimate_total")
    # jobs = ProposalJobSerializer(many=True, source="json.jobs")
    title = serializers.CharField(required=True, source="json.title")
    header = serializers.CharField(required=True, source="json.header")
    footer = serializers.CharField(required=True, source="json.footer")
    show_project_id = serializers.BooleanField(
        required=True, source="json.show_project_id"
    )
    add_terms = serializers.BooleanField(required=True, source="json.add_terms")
    billable_contact = serializers.SerializerMethodField()
    doc_template = serializers.IntegerField(
        required=False, source="json.doc_template", help_text="Document template id"
    )

    class Meta:
        model = Proposal
        fields = DocumentSerializer.Meta.fields + [
            "id",
            "title",
            "billable_contact",
            "header",
            "footer",
            "show_project_id",
            "doc_template",
            "add_terms",
            "letterhead",
            "project",
            "jobs",
            "status",
            "estimate_total",
            "json",
        ]

    @swagger_serializer_method(serializer_or_field=ContactSerializer)
    def get_billable_contact(self, proposal):
        return ContactSerializer(
            instance=proposal.project.billable_contact.contact
        ).data


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
