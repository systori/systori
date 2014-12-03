from django.db import models
from django.utils.translation import ugettext_lazy as _


class Proposal(models.Model):
    project = models.ForeignKey("project.Project", related_name="proposals")
    description = models.TextField(_("Proposal Description"), blank=True, null=True)
    class Meta:
        verbose_name = _("Proposal")
        verbose_name_plural = _("Proposals")


class Estimate(models.Model):
    is_template = models.BooleanField(default=False)
    proposal = models.ForeignKey("Proposal", related_name="estimates")
    class Meta:
        verbose_name = _("Estimate")
        verbose_name_plural = _("Estimates")


class Unit(models.Model):
    name = models.CharField(_('Name'), max_length=128)


class LineItemType(models.Model):
    name = models.CharField(_('Name'), max_length=128)


class LineItem(models.Model):
    estimate = models.ForeignKey("Estimate", related_name="lineitems")
    value = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.ForeignKey("Unit")
    itemtype = models.ForeignKey("LineItemType")
    class Meta:
        verbose_name = _("Line Item")
        verbose_name_plural = _("Line Items")
