from ..user.authorization import office_auth
from django.conf.urls import url

from . import api_views

urlpatterns = [
    url(r'^api/(?P<project_pk>\d+)/document-template/(?P<template_pk>\d+)?$',
        office_auth(api_views.DocumentTemplateView.as_view()), name='api.document.template'),
]
