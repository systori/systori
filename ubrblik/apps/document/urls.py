from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
  url(r'^create-proposal$', login_required(ProposalCreate.as_view()), name='proposal.create'),
  url(r'^proposal-(?P<pk>\d+)$', login_required(ProposalView.as_view()), name='proposal.view'),
  url(r'^proposal-(?P<pk>\d+).pdf$', login_required(ProposalPDF.as_view()), name='proposal.pdf'),
  url(r'^proposal-(?P<pk>\d+)/transition/(?P<transition>\w+)$', login_required(ProposalTransition.as_view()), name='proposal.transition'),
  url(r'^proposal-(?P<pk>\d+)/delete$', login_required(ProposalDelete.as_view()), name='proposal.delete'),

  url(r'^create-invoice$', login_required(InvoiceCreate.as_view()), name='invoice.create'),
  url(r'^invoice-(?P<pk>\d+)$', login_required(InvoiceView.as_view()), name='invoice.view'),
  url(r'^invoice-(?P<pk>\d+).pdf$', login_required(InvoicePDF.as_view()), name='invoice.pdf'),
  url(r'^invoice-(?P<pk>\d+)/transition/(?P<transition>\w+)$', login_required(InvoiceTransition.as_view()), name='invoice.transition'),
  url(r'^invoice-(?P<pk>\d+)/delete$', login_required(InvoiceDelete.as_view()), name='invoice.delete'),
)