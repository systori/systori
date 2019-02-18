import pusher
import os
from django.conf import settings
from unittest.mock import Mock

if not settings.TESTING:
    pusher_client = pusher.Pusher(
        app_id=os.environ.get("PUSHER_APP_ID", ""),
        key=os.environ.get("PUSHER_KEY", ""),
        secret=os.environ.get("PUSHER_SECRET", ""),
        cluster='eu',
        ssl=True
    )
else:
    pusher_client = Mock()
