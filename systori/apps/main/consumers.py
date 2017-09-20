from channels.generic.websockets import JsonWebsocketConsumer


class NotesConsumer(JsonWebsocketConsumer):
    http_user = True
    strict_ordering = True
    groups = ['notes']
