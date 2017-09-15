from django.forms import ModelForm
from django.forms.widgets import Textarea
from .models import Note


class NoteForm(ModelForm):

    class Meta:
        model = Note
        fields = 'text',
        widgets = {
            'text': Textarea(attrs={
                'id': 'note-input',
                'style': 'width: 100%; resize: none; border: 1px dotted grey;'
            }),
        }
