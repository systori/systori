from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from .views import TaskEditor, TaskPDF

urlpatterns = patterns('',
  url(r'^job-(?P<pk>\d+)/tasks$', login_required(TaskEditor.as_view()), name='tasks'),
  url(r'^job-(?P<pk>\d+)/tasks.pdf$', login_required(TaskPDF.as_view()), name='taskpdf'),
)