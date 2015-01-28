from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
  url(r'^create-job$', login_required(JobCreate.as_view()), name='job.create'),
  url(r'^job-(?P<pk>\d+)$', login_required(JobView.as_view()), name='job.view'),
  url(r'^job-(?P<pk>\d+)/tasks$', login_required(TaskEditor.as_view()), name='tasks'),
  url(r'^job-(?P<pk>\d+)/transition/(?P<transition>\w+)$', login_required(JobTransition.as_view()), name='job.transition'),
  url(r'^job-(?P<pk>\d+)/estimate/(?P<action>\w+)$', login_required(JobEstimateModification.as_view()), name='job.estimate'),
  url(r'^job-(?P<pk>\d+)/edit$', login_required(JobUpdate.as_view()), name='job.edit'),
  url(r'^job-(?P<pk>\d+)/delete$', login_required(JobDelete.as_view()), name='job.delete'),
)