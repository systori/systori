# from channels import route, route_class
# from channels.staticfiles import StaticFilesConsumer
# from systori.apps.main.consumers import NotesConsumer
#
# channel_routing = [
#     route('http.request', StaticFilesConsumer()),
#     route_class(NotesConsumer, path=r"^/notes"),
# ]

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import systori.apps.main.routing


application = ProtocolTypeRouter({
    # (http->django views are added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            systori.apps.main.routing.websocket_urlpatterns
        )
    ),
})
