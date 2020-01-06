from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _

import rest_framework.serializers as serializers
from drf_yasg.utils import swagger_serializer_method
from rest_framework.serializers import ModelSerializer

from systori.apps.directory.serializers import ContactSerializer
from systori.apps.document.models import (
    Adjustment,
    Document,
    DocumentSettings,
    DocumentTemplate,
    Invoice,
    Letterhead,
    Payment,
    Proposal,
    Refund,
    Timesheet,
)
from systori.lib.accounting.tools import AmountSerializer, Amount
from systori.apps.accounting.constants import TAX_RATE
from systori.apps.project.models import Project
from systori.apps.task import flutter_serializers


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


class ProposalJsonBaseClass:
    """
    Adds an additional field called <model-name>.id e.g. `job.id`

    """

    def to_representation(self, instance):
        #  pylint: disable=no-member
        ret = super().to_representation(instance)

        meta = getattr(self, "Meta")
        if not meta or not ret.get("pk", None):
            return ret

        model_name = meta.model.__name__
        ret[f"{model_name.lower()}.id"] = ret["pk"]

        return ret


class ProposalJsonLineItemSerializer(
    ProposalJsonBaseClass, flutter_serializers.LineItemSerializer
):
    class Meta(flutter_serializers.LineItemSerializer.Meta):
        pass


class ProposalJsonTaskSerializer(
    ProposalJsonBaseClass, flutter_serializers.TaskSerializer
):
    lineitems = ProposalJsonLineItemSerializer(many=True, required=True)

    class Meta(flutter_serializers.TaskSerializer.Meta):
        pass


class ProposalJsonGroupSerializer(
    ProposalJsonBaseClass, flutter_serializers.GroupSerializer
):
    tasks = ProposalJsonTaskSerializer(many=True, required=False)

    class Meta(flutter_serializers.GroupSerializer.Meta):
        pass


class ProposalJsonJobSerializer(
    ProposalJsonBaseClass, flutter_serializers.JobSerializer
):
    is_attached = serializers.SerializerMethodField(required=False)
    groups = ProposalJsonGroupSerializer(many=True, required=False)
    tasks = ProposalJsonTaskSerializer(many=True, required=False)

    class Meta(flutter_serializers.JobSerializer.Meta):
        fields = flutter_serializers.JobSerializer.Meta.fields + ["is_attached"]

    def __init__(self, proposal: Proposal = None, is_attached: bool = None, **kwargs):

        self.proposal = proposal
        self.is_attached = is_attached
        super().__init__(**kwargs)

    @swagger_serializer_method(serializer_or_field=serializers.BooleanField)
    def get_is_attached(self, job):
        assert self.proposal is not None or self.is_attached is not None
        return self.is_attached or job in self.proposal.jobs.all()


class ProposalJSONSerializer(serializers.Serializer):

    title = serializers.CharField(required=True)
    header = serializers.CharField(required=True)
    footer = serializers.CharField(required=True)
    show_project_id = serializers.BooleanField(required=False, default=False)
    add_terms = serializers.BooleanField(required=False, default=False)
    doc_template = serializers.IntegerField(
        allow_null=True, required=False, help_text="Document template id"
    )

    class Meta:
        fields = [
            "title",
            "header",
            "footer",
            "show_project_id",
            "add_terms",
            "doc_template",
        ]


class ProposalSerializer(DocumentSerializer):
    letterhead = serializers.PrimaryKeyRelatedField(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        required=True, queryset=Project.objects, source="project"
    )
    json = ProposalJSONSerializer(
        required=True, help_text="Extra Meta data for this proposal"
    )
    estimate_total = serializers.SerializerMethodField()

    billable_contact = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = DocumentSerializer.Meta.fields + [
            "id",
            "project_id",
            "jobs",
            "status",
            "json",
            "letterhead",
            "billable_contact",
            "estimate_total",
        ]

    def create_json(self, validated_data=None):
        """ 
        Creates initial json object based on validated_data
        *Should Run before proposal is created*
        """
        assert validated_data is not None

        json = validated_data["json"]

        # additional json fields that include contact details
        billable_contact_fields = [
            "business",
            "salutation",
            "first_name",
            "last_name",
            "address",
            "postal_code",
            "city",
            "address_label",
        ]

        project = validated_data["project"]
        billable_contact = self._get_billable_contact_from_project(project)

        for field in billable_contact_fields:
            json[field] = billable_contact[field]

        jobs = validated_data["jobs"]

        json["jobs"] = ProposalJsonJobSerializer(
            is_attached=True, instance=jobs, many=True
        ).data

        json["estimate_total"] = AmountSerializer(
            instance=ProposalSerializer.calculate_estimate(jobs)
        ).data

        return json

    def update_json(self, proposal, validated_data):
        """
        Creates json object for given [proposal] and applies any updates to it via [validated_data]
        *Run after [proposal] has been updated to create proper json*
        """

        validated_data["project"] = proposal.project
        validated_data["jobs"] = validated_data.get("jobs", proposal.jobs.all())

        json = self.create_json(validated_data)

        model_fields = ["created_on", "document_date", "notes"]

        for field in model_fields:
            attr = self.fields[field].get_attribute(proposal)
            json[field] = attr

        json["project_id"] = proposal.project.id

        return json

    def _get_billable_contact_from_project(self, project):
        contact = None

        if isinstance(project, Project):
            contact = project.billable_contact.contact

        return ContactSerializer(instance=contact).data if contact else None

    @swagger_serializer_method(serializer_or_field=ContactSerializer)
    def get_billable_contact(self, proposal):
        contact = None

        if isinstance(proposal, Proposal):
            contact = self._get_billable_contact_from_project(proposal.project)
        elif isinstance(proposal, dict):
            contact = self._get_billable_contact_from_project(proposal["project"])

        return contact

    @staticmethod
    def calculate_estimate(jobs):
        estimate_total = Amount.zero()
        for job in jobs:
            estimate_total += Amount.from_net(job.estimate, TAX_RATE)
        return estimate_total

    @swagger_serializer_method(serializer_or_field=AmountSerializer)
    def get_estimate_total(self, proposal):
        return AmountSerializer(
            instance=ProposalSerializer.calculate_estimate(proposal.jobs.all())
        ).data

    def create(self, validated_data):

        doc_settings = DocumentSettings.get_for_language(get_language())
        validated_data["letterhead"] = doc_settings.proposal_letterhead

        json = self.create_json(validated_data)
        validated_data.pop("json")
        instance = super().create(validated_data)
        validated_data["json"] = json
        return self.update(instance, validated_data)

    def update(self, proposal, validated_data):
        doc_settings = DocumentSettings.get_for_language(get_language())
        proposal.letterhead = doc_settings.proposal_letterhead

        json = validated_data.pop("json", {})
        updated = super().update(proposal, validated_data)
        validated_data["json"] = json
        json = self.update_json(updated, validated_data)
        updated.json = json
        updated.save()
        return updated


class ProposalPDFOptionsSerializer(serializers.Serializer):

    with_lineitems = serializers.BooleanField(
        help_text="With linetitems", default=False
    )
    only_groups = serializers.BooleanField(
        help_text="Only include groups", default=False
    )
    only_task_names = serializers.BooleanField(
        help_text="Only include task names", default=False
    )
    download = serializers.BooleanField(
        help_text="Whether to instruct the client to download instead of viewing inline",
        default=True,
    )

    EMAIL = "email"
    PRINT = "print"

    FORMAT_CHOICES = ((EMAIL, _("email")), (PRINT, _("print")))
    format = serializers.ChoiceField(
        help_text="PDF format to render", choices=FORMAT_CHOICES, required=True
    )
    technical_listing = serializers.BooleanField(
        help_text="Whether this is a technical listing", default=False
    )

    class Meta:
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
