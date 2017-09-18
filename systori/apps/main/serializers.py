from django.utils.timezone import now
from rest_framework import serializers
from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(read_only=True)
    worker = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Note
        fields = ('pk', 'project',
                  'worker', 'text', 'created')
