from channels import route, route_class
from channels.staticfiles import StaticFilesConsumer
from systori.apps.main.consumers import NotesConsumer

channel_routing = [
    route('http.request', StaticFilesConsumer()),
    route_class(NotesConsumer, path=r"^/notes"),
]