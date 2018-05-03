from django.conf.urls import url
from systori.apps.main import consumers

websocket_urlpatterns = [
    url(r'^ws/notes/$', consumers.NotesConsumer),
]