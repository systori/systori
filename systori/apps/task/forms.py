from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from bootstrap import DateWidget

from ..accounting.models import create_account_for_job
from ..company.models import Company, Worker
from ..project.models import Project
from .models import Job, ProgressReport, ExpendReport


class JobTemplateCreateForm(forms.ModelForm):

    class Meta:
        model = Job
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True

    def save(self, commit=True):
        job = super().save(commit)
        job.job = job
        job.account = create_account_for_job(job)
        job.save()
        return job


class JobCreateForm(forms.ModelForm):

    job_template = forms.ModelChoiceField(
        label=_('Job Template'),
        queryset=Job.objects.filter(project__is_template=True),
        required=False
    )

    class Meta:
        model = Job
        fields = ['name', 'description', 'job_template']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True

    def save(self, commit=True):
        job = super().save(commit)
        job.job = job
        job.account = create_account_for_job(job)
        if self.cleaned_data['job_template']:
            tmpl = self.cleaned_data['job_template']
            tmpl.clone_to(job)
        job.save()
        return job


class JobProgressForm(forms.ModelForm):

    status_complete = forms.BooleanField(
        label=_("Set job status to 'Completed'."),
        initial=False, required=False
    )
    progress_onehundred = forms.BooleanField(
        label=_("Set 100% progress for all unfinished tasks/lineitems."),
        initial=False, required=False,
        help_text=_("Does not affect tasks/lineitems already at 100%.")
    )
    progress_date = forms.DateField(
        label=_("Progress Date"), required=False, initial=timezone.now, widget=DateWidget,
        help_text=_("Used as the date on which each task/lineitem achieved 100% progress.")
    )
    progress_worker = forms.ModelChoiceField(
        label=_("Progress Worker"), required=False, queryset=Worker.objects.none(),
        help_text=_("Worker to associate with progress reports.")
    )
    comment = forms.CharField(
        label=_("Progress Comment"), widget=forms.Textarea, required=False,
        help_text=_("Used as the comment for each task/lineitem progress report.")
    )

    class Meta:
        model = Job
        fields = ['status_complete', 'progress_onehundred', 'progress_date', 'progress_worker', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['progress_worker'].queryset = Company.active().active_workers()

    def clean(self):
        if not any([self.cleaned_data['status_complete'], self.cleaned_data['progress_onehundred']]):
            self.add_error(None, _('At least one option is required.'))
        if self.cleaned_data['progress_onehundred']:
            for field in ['progress_date', 'progress_worker', 'comment']:
                if not self.cleaned_data[field]:
                    self.add_error(field, _('Required when setting progress to 100%.'))

    def save(self, commit=True):
        job = self.instance
        if self.cleaned_data['status_complete']:
            job.complete()
        if self.cleaned_data['progress_onehundred']:
            for task in job.all_tasks.all():

                if not task.include_estimate:
                    continue

                if task.is_time_and_materials:
                    for li in task.lineitems.all():
                        if li.qty is not None and li.expended < li.qty:
                            li.expended = li.qty
                            li.save()
                            ExpendReport.objects.create(
                                worker=self.cleaned_data['progress_worker'],
                                lineitem=li,
                                expended=li.expended,
                                comment=self.cleaned_data['comment']
                            )
                else:
                    if task.complete < task.qty:
                        task.complete = task.qty
                        task.save()
                        ProgressReport.objects.create(
                            worker=self.cleaned_data['progress_worker'],
                            task=task,
                            complete=task.complete,
                            comment=self.cleaned_data['comment']
                        )
        return super().save(commit)


class JobCopyForm(forms.Form):
    project_id = forms.IntegerField(disabled=True, widget=forms.HiddenInput())
    job_id = forms.IntegerField()

    def clean_job_id(self):
        job = Job.objects.get(id=self.cleaned_data.get("job_id"))
        project = Project.objects.get(id=self.cleaned_data.get("project_id"))
        if not project.can_receive_job(job):
            raise forms.ValidationError(
                "The Job you're trying to import has an incompatible depth with the current project.",
                code='invalid',
            )
        return job.id