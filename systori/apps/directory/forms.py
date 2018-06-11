from django.forms import ModelForm, ValidationError
from .models import Contact, ProjectContact
from django.utils.translation import ugettext_lazy as _


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        exclude = ["projects"]

    def clean(self):
        cleaned_data = super(ContactForm, self).clean()
        business = cleaned_data.get("business")
        last_name = cleaned_data.get("last_name")

        if not business and not last_name:
            msg = _("You must provide either a company or last name.")
            self.add_error("business", msg)
            self.add_error("last_name", msg)


class ProjectContactForm(ModelForm):
    class Meta:
        model = ProjectContact
        fields = ["association", "is_billable"]
