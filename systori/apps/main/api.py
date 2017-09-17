from django.conf.urls import url
from rest_framework import views, status, renderers, parsers
from rest_framework.response import Response
from django.http import Http404
from ..user.permissions import HasStaffAccess
from ..user.authorization import field_auth
from django.utils.timezone import now
from datetime import timedelta
from .models import Note


class PlainTextRenderer(renderers.BaseRenderer):
    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, media_type=None, renderer_context=None):
        if data:
            return data.encode(self.charset)
        else:
            pass


class PlainTextParser(parsers.BaseParser):
    """
    Plain text parser.
    """
    media_type = 'text/plain'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Simply return a string representing the body of the request.
        """
        return stream.read()


class NoteDetail(views.APIView):
    renderer_classes = (PlainTextRenderer,)
    parser_classes = (PlainTextParser,)
    permission_classes = (HasStaffAccess,)

    def get_object(self, pk):
        try:
            return Note.objects.get(pk=pk)
        except Note.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        note = self.get_object(pk=pk)
        return Response(note.text)

    def put(self, request, pk, format=None):
        note = self.get_object(pk=pk)
        note.created = now()
        note.text = request.data.decode("utf-8")
        note.save()
        return Response(note.text)

    def delete(self, request, pk, format=None):
        note = self.get_object(pk=pk)
        if note.created > now() - timedelta(hours=2) and request.user == note.worker.user:
            note.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


urlpatterns = [
    url(r'^note/(?P<pk>\d+)$', NoteDetail.as_view(), name='api.note.get'),
    url(r'^note/(?P<pk>\d+)/delete$', NoteDetail.as_view(), name='api.note.delete'),
    url(r'^note/(?P<pk>\d+)/update$', NoteDetail.as_view(), name='api.note.update'),
]