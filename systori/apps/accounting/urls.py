from django.conf.urls import patterns, url
from ..user.authorization import office_auth
from .views import *

urlpatterns = patterns('',
  url(r'^project-(?P<project_pk>\d+)/create-payment$', office_auth(PaymentCreate.as_view()), name='payment.create'),
)