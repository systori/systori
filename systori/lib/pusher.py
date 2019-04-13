import pusher
import os
from django.conf import settings
from unittest.mock import Mock

if not settings.TESTING:
    pusher_client = pusher.Pusher(
        app_id=os.environ.get("PUSHER_APP_ID", "123456"),
        key=os.environ.get("PUSHER_KEY", "0123456abcdefghijklm"),
        secret=os.environ.get("PUSHER_SECRET", "0123456abcdefghijklm"),
        cluster="eu",
        ssl=True,
    )
else:
    pusher_client = Mock()
