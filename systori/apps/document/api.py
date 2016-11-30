from django.conf.urls import url
from rest_framework import views
from rest_framework.response import Response
from ..project.models import Project
from ..user.permissions import HasStaffAccess

from .models import DocumentTemplate


class DocumentTemplateView(views.APIView):
    permissions = (HasStaffAccess,)

    def get(self, request, project_pk=None, template_pk=None, **kwargs):
        project = Project.objects.get(id=project_pk)
        template = DocumentTemplate.objects.get(id=template_pk)
        rendered = template.render(project)
        return Response(rendered)


urlpatterns = [
    url(r'^document-template/project-(?P<project_pk>\d+)/template-(?P<template_pk>\d+)?$',
        DocumentTemplateView.as_view(), name='api.document.template'),
]
