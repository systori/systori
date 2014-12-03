from django.db import models
from django.utils.translation import ugettext_lazy as _


class Document(models.Model):
    INVOICE = "invoice"
    PROPOSAL = "proposal"
    REPORT = "report"
    DOCUMENT_TYPE = (
        (PROPOSAL, _("Proposal")),
        (INVOICE, _("Invoice")),
        (REPORT, _("Report"))
    )
    project = models.ForeignKey("project.Project", related_name="document")
    description = models.TextField(_("Proposal Description"), blank=True, null=True)
    doctype = models.CharField(max_length=128, choices=DOCUMENT_TYPE, default=PROPOSAL)
    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")

    def add_task(self, task):
        DocumentItem.objects.create(document=self, task=task)

class DocumentItem(models.Model):
    document = models.ForeignKey("Document", related_name="items")
    task = models.ForeignKey("task.Task")