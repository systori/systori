from mistune import markdown
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _


class Note(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    project = models.ForeignKey(
        "project.Project", related_name="+", on_delete=models.CASCADE
    )

    worker = models.ForeignKey(
        "company.Worker", related_name="notes", on_delete=models.PROTECT
    )
    text = models.TextField(_("Text"))
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        ordering = ("created",)

    @property
    def html(self):
        return markdown(self.text)
