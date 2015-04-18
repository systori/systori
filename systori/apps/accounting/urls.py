from django.conf.urls import patterns, url
from ..user.authorization import office_auth
from .views import *

urlpatterns = patterns('',
    url(r'^project-(?P<project_pk>\d+)/create-payment$', office_auth(PaymentCreate.as_view()), name='payment.create'),

    url(r'^accounts$', office_auth(AccountList.as_view()), name='accounts'),
    url(r'^account-(?P<pk>\d+)$', office_auth(AccountView.as_view()), name='account.view'),
    url(r'^account-(?P<pk>\d+)/edit$', office_auth(AccountUpdate.as_view()), name='account.edit'),

    url(r'^create-bank-account$', office_auth(BankAccountCreate.as_view()), name='account.create'),
    url(r'^account-(?P<pk>\d+)/delete$', office_auth(BankAccountDelete.as_view()), name='account.delete'),
)