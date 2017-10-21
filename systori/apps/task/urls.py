from django.conf.urls import url
from ..user.authorization import office_auth
from .views import *

urlpatterns = [
    url(r'^create-job$', office_auth(JobCreate.as_view()), name='job.create'),
    url(r'^import-job$', office_auth(JobImport.as_view()), name='job.import'),
    url(r'^paste-job$', office_auth(JobPaste.as_view()), name='job.paste'),
    url(r'^job-(?P<pk>\d+)/editor$', office_auth(JobEditor.as_view()), name='job.editor'),
    url(r'^job-(?P<pk>\d+)/progress$', office_auth(JobProgress.as_view()), name='job.progress'),
    url(r'^job-(?P<pk>\d+)/delete$', office_auth(JobDelete.as_view()), name='job.delete'),
    url(r'^job-(?P<pk>\d+)/copy$', office_auth(JobCopy.as_view()), name='job.copy'),
]
