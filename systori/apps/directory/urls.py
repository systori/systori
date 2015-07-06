from django.conf.urls import patterns, url
from ..user.authorization import office_auth
from .views import DirectoryList
from .views import ContactView, ContactCreate, ContactUpdate, ContactDelete
from .views import ProjectContactSetBillable, ProjectContactAdd, ProjectContactCreate, ProjectContactRemove

urlpatterns = patterns('',
    url(r'^directory$', office_auth(DirectoryList.as_view()), name='directory'),

    url(r'^create-contact$', office_auth(ContactCreate.as_view()), name='contact.create'),
    url(r'^contact-(?P<pk>\d+)$', office_auth(ContactView.as_view()), name='contact.view'),
    url(r'^contact-(?P<pk>\d+)/edit$', office_auth(ContactUpdate.as_view()), name='contact.edit'),
    url(r'^contact-(?P<pk>\d+)/delete$', office_auth(ContactDelete.as_view()), name='contact.delete'),

    url(r'^project-(?P<project_pk>\d+)/contact/add$', office_auth(ProjectContactAdd.as_view()), name='project.contact.add'),
    url(r'^project-(?P<project_pk>\d+)/contact/create$', office_auth(ProjectContactCreate.as_view()), name='project.contact.create'),
    url(r'^project-(?P<project_pk>\d+)/contact-(?P<pk>\d+)/remove$', office_auth(ProjectContactRemove.as_view()), name='project.contact.remove'),
    url(r'^project-(?P<project_pk>\d+)/contact-(?P<pk>\d+)/billable$', office_auth(ProjectContactSetBillable.as_view()), name='project.contact.billable'),
)
