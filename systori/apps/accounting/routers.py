from rest_framework.routers import SimpleRouter
from systori.apps.accounting.api import (
    AccountModelViewSet,
    EntryModelViewSet,
    TransactionModelViewSet,
)

router = SimpleRouter()
router.register(r"account", AccountModelViewSet)
router.register(r"entry", EntryModelViewSet)
router.register(r"transaction", TransactionModelViewSet)

urlpatterns = router.urls
