from django.conf.urls import patterns, url
from ..user.authorization import office_auth
from .views import *


urlpatterns = patterns('',
  url(r'^project-(?P<project_pk>\d+)/create-proposal$', office_auth(ProposalCreate.as_view()), name='proposal.create'),
  url(r'^project-(?P<project_pk>\d+)/proposal-(?P<pk>\d+)$', office_auth(ProposalView.as_view()), name='proposal.view'),
  url(r'^project-(?P<project_pk>\d+)/proposal-(?P<format>(email|print))-(?P<pk>\d+).pdf$', office_auth(ProposalPDF.as_view()), name='proposal.pdf'),
  url(r'^project-(?P<project_pk>\d+)/proposal-(?P<pk>\d+)/transition/(?P<transition>\w+)$', office_auth(ProposalTransition.as_view()), name='proposal.transition'),
  url(r'^project-(?P<project_pk>\d+)/proposal-(?P<pk>\d+)/delete$', office_auth(ProposalDelete.as_view()), name='proposal.delete'),

  url(r'^project-(?P<project_pk>\d+)/create-invoice$', office_auth(InvoiceCreate.as_view()), name='invoice.create'),
  url(r'^project-(?P<project_pk>\d+)/invoice-(?P<pk>\d+)$', office_auth(InvoiceView.as_view()), name='invoice.view'),
  url(r'^project-(?P<project_pk>\d+)/invoice-(?P<pk>\d+).pdf$', office_auth(InvoicePDF.as_view()), name='invoice.pdf'),
  url(r'^project-(?P<project_pk>\d+)/invoice-(?P<pk>\d+)/transition/(?P<transition>\w+)$', office_auth(InvoiceTransition.as_view()), name='invoice.transition'),
  url(r'^project-(?P<project_pk>\d+)/invoice-(?P<pk>\d+)/delete$', office_auth(InvoiceDelete.as_view()), name='invoice.delete'),

  url(r'^templates/create-document-template$', office_auth(DocumentTemplateCreate.as_view()), name='document-template.create'),
  url(r'^templates/document-template-(?P<pk>\d+)$', office_auth(DocumentTemplateView.as_view()), name='document-template.view'),
  url(r'^templates/document-template-(?P<pk>\d+)/edit$', office_auth(DocumentTemplateUpdate.as_view()), name='document-template.edit'),
  url(r'^templates/document-template-(?P<pk>\d+)/delete$', office_auth(DocumentTemplateDelete.as_view()), name='document-template.delete'),
)