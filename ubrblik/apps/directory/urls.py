from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from .views import DirectoryList
from .views import ContactView, ContactCreate, ContactUpdate, ContactDelete
from .views import ProjectContactAdd, ProjectContactCreate, ProjectContactRemove

urlpatterns = patterns('',
  url(r'^directory$', login_required(DirectoryList.as_view()), name='directory'),

  url(r'^create-contact$', login_required(ContactCreate.as_view()), name='contact.create'),
  url(r'^contact-(?P<pk>\d+)$', login_required(ContactView.as_view()), name='contact.view'),
  url(r'^contact-(?P<pk>\d+)/edit$', login_required(ContactUpdate.as_view()), name='contact.edit'),
  url(r'^contact-(?P<pk>\d+)/delete$', login_required(ContactDelete.as_view()), name='contact.delete'),

  url(r'^project-(?P<project_pk>\d+)/contact/add$', login_required(ProjectContactAdd.as_view()), name='project.contact.add'),
  url(r'^project-(?P<project_pk>\d+)/contact/create$', login_required(ProjectContactCreate.as_view()), name='project.contact.create'),
  url(r'^project-(?P<project_pk>\d+)/contact-(?P<pk>\d+)/remove$', login_required(ProjectContactRemove.as_view()), name='project.contact.remove'),
)