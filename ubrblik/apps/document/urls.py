from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
  url(r'^project-(?P<project_pk>\d+)/create-proposal$', login_required(ProposalCreate.as_view()), name='proposal.create'),
  url(r'^project-(?P<project_pk>\d+)/proposal-(?P<pk>\d+)$', login_required(ProposalView.as_view()), name='proposal.view'),
  url(r'^project-(?P<project_pk>\d+)/proposal-(?P<format>(email|print))-(?P<pk>\d+).pdf$', login_required(ProposalPDF.as_view()), name='proposal.pdf'),
  url(r'^project-(?P<project_pk>\d+)/proposal-(?P<pk>\d+)/transition/(?P<transition>\w+)$', login_required(ProposalTransition.as_view()), name='proposal.transition'),
  url(r'^project-(?P<project_pk>\d+)/proposal-(?P<pk>\d+)/delete$', login_required(ProposalDelete.as_view()), name='proposal.delete'),

  url(r'^project-(?P<project_pk>\d+)/create-invoice$', login_required(InvoiceCreate.as_view()), name='invoice.create'),
  url(r'^project-(?P<project_pk>\d+)/invoice-(?P<pk>\d+)$', login_required(InvoiceView.as_view()), name='invoice.view'),
  url(r'^project-(?P<project_pk>\d+)/invoice-(?P<pk>\d+).pdf$', login_required(InvoicePDF.as_view()), name='invoice.pdf'),
  url(r'^project-(?P<project_pk>\d+)/invoice-(?P<pk>\d+)/transition/(?P<transition>\w+)$', login_required(InvoiceTransition.as_view()), name='invoice.transition'),
  url(r'^project-(?P<project_pk>\d+)/invoice-(?P<pk>\d+)/delete$', login_required(InvoiceDelete.as_view()), name='invoice.delete'),

  url(r'^templates/create-document-template$', login_required(DocumentTemplateCreate.as_view()), name='document-template.create'),
  url(r'^templates/document-template-(?P<pk>\d+)$', login_required(DocumentTemplateView.as_view()), name='document-template.view'),
  url(r'^templates/document-template-(?P<pk>\d+)/edit$', login_required(DocumentTemplateUpdate.as_view()), name='document-template.edit'),
  url(r'^templates/document-template-(?P<pk>\d+)/delete$', login_required(DocumentTemplateDelete.as_view()), name='document-template.delete'),
)
