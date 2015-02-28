from django.forms import ModelForm
from .models import Project

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'job_zfill', 'taskgroup_zfill', 'task_zfill', 'job_offset',
                  'address', 'postal_code', 'city']
