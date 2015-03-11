from django.forms import ModelForm
from .models import Project, JobSite

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'job_zfill', 'taskgroup_zfill', 'task_zfill', 'job_offset']

class JobSiteForm(ModelForm):
    class Meta:
        model = JobSite
        fields = ['name', 'address', 'postal_code', 'city']