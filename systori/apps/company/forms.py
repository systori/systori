import os.path
from django.forms import ModelForm
from django.conf import settings
from django.core.files.uploadedfile import File
from django.utils.translation import ugettext_lazy as _

from systori.apps.project.models import Project
from systori.apps.accounting.workflow import create_chart_of_accounts
from systori.apps.document.models import DocumentSettings
from systori.apps.document.letterhead_utils import clean_letterhead_pdf

from .models import Company, Worker


class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = 'name', 'schema', 'timezone', 'is_jobsite_required'
        labels = {
            'schema': _('Sub-Domain'),
        }
        help_texts = {
            'name': _('Full legal name of your company.'),
            'schema': _(
                'Short and simple version of your company name used in URLs. '
                'May only contain lowercase letters, digits and underscores. '
                'Must start with a letter. Cannot be changed later.')
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if self.instance.schema:
            self.fields['schema'].disabled = True

    def save(self, commit=True):
        adding = self.instance._state.adding
        company = super().save(commit)
        if adding:
            company.activate()
            Worker.objects.create(
                company=company,
                user=self.user,
                is_owner=True
            )
            Project.objects.create(
                name="Template Project",
                is_template=True
            )
            create_chart_of_accounts()
            demo_letterhead = os.path.join(settings.MEDIA_ROOT, 'demo_letterhead.pdf')
            letterhead = clean_letterhead_pdf(File(open(demo_letterhead, 'rb')), save=True)
            DocumentSettings.objects.create(
                proposal_letterhead=letterhead,
                invoice_letterhead=letterhead,
                evidence_letterhead=letterhead,
                itemized_letterhead=letterhead,
                timesheet_letterhead=letterhead
            )
        return company
