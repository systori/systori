from collections import namedtuple
from django.db import models
from django.utils.translation import ugettext_lazy as _

"""
Document represents a work-in-progress model for a physical document.

Workflow is something like this:

1. User creates a new Document object (either Invoice, Proposal, Report, etc).

2. They will associate Tasks with this document. At this point the tasks might
   change due to other factors in the system (workers marking tasks as done).

3. When user is satisfied with the document and have verified that the tasks
   look correct they must generate a PDF.

4. Once a PDF is generated they can no longer edit the document. They can easily
   duplicate the document and start a new one.

Rationale:

Because a Document represents references to live Tasks (which can change due to other
factors) it would be confusing to leave a document editable after it has been verified
and generated. By locking editing and generating a PDF we have created a snap shot at a
point in time where the user was satisfied with the state of all associated Tasks.
"""

class Status(namedtuple('Status', ['name', 'label'])):
    def __eq__(self, other):
        return self.name == other

class Document(models.Model):

    project = models.ForeignKey("project.Project", related_name="document")
    description = models.TextField(_("Proposal Description"), blank=True, null=True)
    pdf = models.FileField()

    PROPOSAL = "proposal"
    INVOICE = "invoice"
    DOCUMENT_TYPE = (
        (PROPOSAL, _("Proposal")),
        (INVOICE, _("Invoice")),
    )
    doctype = models.CharField(max_length=128, choices=DOCUMENT_TYPE, default=PROPOSAL)

    DRAFT = Status("draft", _("Draft"))
    READY = Status("ready", _("Ready"))
    SENT = Status("sent", _("Sent"))
    APPROVED = Status("approved", _("Approved"))
    PAID = Status("paid", _("Paid"))
    CANCELED = Status("canceled", _("Canceled"))

    WORKFLOW = {
      PROPOSAL: [READY, SENT, APPROVED, CANCELED],
      INVOICE: [READY, SENT, PAID, CANCELED]
    }

    STATUS_TYPE = (DRAFT, READY, SENT, APPROVED, PAID, CANCELED)

    status = models.CharField(max_length=128, choices=STATUS_TYPE, default=DRAFT)

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")