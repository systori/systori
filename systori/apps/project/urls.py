from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from ..user.authorization import office_auth
from .views import ProjectList, ProjectView, ProjectCreate, ProjectImport, ProjectUpdate, ProjectDelete
from .views import ProjectPlanning, TemplatesView
from .views import JobSiteCreate, JobSiteUpdate, JobSiteDelete
from ..accounting.views import PaymentCreate, PaymentDelete


urlpatterns = patterns('',

    url(r'^projects$', office_auth(ProjectList.as_view()), name='projects'),
    url(r'^create-project$', office_auth(ProjectCreate.as_view()), name='project.create'),
    url(r'^import-project$', office_auth(ProjectImport.as_view()), name='project.import'),
    url(r'^project-(?P<pk>\d+)$', office_auth(ProjectView.as_view()), name='project.view'),
    url(r'^project-(?P<pk>\d+)/edit$', office_auth(ProjectUpdate.as_view()), name='project.edit'),
    url(r'^project-(?P<pk>\d+)/plan$', office_auth(ProjectPlanning.as_view()), name='project.plan'),
    url(r'^project-(?P<pk>\d+)/delete$', office_auth(ProjectDelete.as_view()), name='project.delete'),
    url(r'^templates$', office_auth(TemplatesView.as_view()), name='templates'),

    url(r'^project-(?P<project_pk>\d+)/create-jobsite$', office_auth(JobSiteCreate.as_view()), name='jobsite.create'),
    url(r'^project-(?P<project_pk>\d+)/jobsite-(?P<pk>\d+)/edit$', office_auth(JobSiteUpdate.as_view()), name='jobsite.edit'),
    url(r'^project-(?P<project_pk>\d+)/jobsite-(?P<pk>\d+)/delete$', office_auth(JobSiteDelete.as_view()), name='jobsite.delete'),

    url(r'^project-(?P<project_pk>\d+)/create-payment$', office_auth(PaymentCreate.as_view()), name='payment.create'),
    url(r'^project-(?P<project_pk>\d+)/payment-(?P<pk>\d+)/delete$', office_auth(PaymentDelete.as_view()), name='payment.delete'),
)
