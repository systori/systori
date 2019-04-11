from rest_framework.viewsets import ModelViewSet

from systori.apps.user.permissions import HasStaffAccess, IsOwnerOrReadOnly
from systori.apps.main.models import Note
from systori.apps.main.serializers import NoteSerializer


class NoteModelViewSet(ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = (HasStaffAccess, IsOwnerOrReadOnly)
