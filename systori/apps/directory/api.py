from rest_framework.viewsets import ModelViewSet

from systori.apps.user.permissions import HasStaffAccess
from systori.apps.directory.models import Contact, ProjectContact
from systori.apps.directory.serializers import (
    ContactSerializer,
    ProjectContactSerializer,
)


class ContactModelViewSet(ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = (HasStaffAccess,)


class ProjectContactModelViewSet(ModelViewSet):
    queryset = ProjectContact.objects.all()
    serializer_class = ProjectContactSerializer
    permission_classes = (HasStaffAccess,)
