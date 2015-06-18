from django.contrib import admin
from .models import Project, JobSite


class ProjectAdmin(admin.ModelAdmin):
    pass


class JobSiteAdmin(admin.ModelAdmin):
    pass


admin.site.register(Project, ProjectAdmin)
admin.site.register(JobSite, JobSiteAdmin)
