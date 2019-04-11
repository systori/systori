from rest_framework.viewsets import ModelViewSet

from systori.apps.user.permissions import HasOwnerAccess
from systori.apps.accounting.models import Account, Entry, Transaction
from systori.apps.accounting.serializers import (
    AccountSerializer,
    EntrySerializer,
    TransactionSerializer,
)


class AccountModelViewSet(ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = HasOwnerAccess


class EntryModelViewSet(ModelViewSet):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer
    permission_classes = HasOwnerAccess


class TransactionModelViewSet(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = HasOwnerAccess
