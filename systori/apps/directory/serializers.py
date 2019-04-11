from rest_framework.serializers import ModelSerializer

from systori.apps.directory.models import Contact, ProjectContact


class ContactSerializer(ModelSerializer):
    class Meta:
        model = Contact
        fields = "__all__"


class ProjectContactSerializer(ModelSerializer):
    class Meta:
        model = ProjectContact
        fields = "__all__"
