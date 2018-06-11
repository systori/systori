from django.conf.urls import url

from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.urlpatterns import format_suffix_patterns

from ..user.permissions import HasStaffAccess
from .models import Note
from .serializers import NoteSerializer
from .permissions import IsOwnerOrReadOnly


class NoteDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = (HasStaffAccess, IsOwnerOrReadOnly)
    queryset = Note.objects.all()
    serializer_class = NoteSerializer


urlpatterns = [url(r"^note/(?P<pk>\d+)$", NoteDetail.as_view(), name="note.api")]

urlpatterns = format_suffix_patterns(urlpatterns)
