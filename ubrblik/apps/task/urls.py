from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from ..user.authorization import office_auth
from .views import *

urlpatterns = patterns('',
  url(r'^create-job$', office_auth(JobCreate.as_view()), name='job.create'),
  url(r'^job-(?P<pk>\d+)$', office_auth(JobView.as_view()), name='job.view'),
  url(r'^job-(?P<pk>\d+)/tasks$', office_auth(TaskEditor.as_view()), name='tasks'),
  url(r'^job-(?P<pk>\d+)/transition/(?P<transition>\w+)$', office_auth(JobTransition.as_view()), name='job.transition'),
  url(r'^job-(?P<pk>\d+)/estimate/(?P<action>\w+)$', office_auth(JobEstimateModification.as_view()), name='job.estimate'),
  url(r'^job-(?P<pk>\d+)/edit$', office_auth(JobUpdate.as_view()), name='job.edit'),
  url(r'^job-(?P<pk>\d+)/delete$', office_auth(JobDelete.as_view()), name='job.delete'),
)