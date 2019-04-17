from rest_framework.serializers import ModelSerializer

from systori.apps.accounting.models import Account, Entry, Transaction


class AccountSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"


class EntrySerializer(ModelSerializer):
    class Meta:
        model = Entry
        fields = "__all__"


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
