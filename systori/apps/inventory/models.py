from decimal import Decimal

from django.db import models
from django.utils.translation import ugettext_lazy as _


class MaterialType(models.Model):
    name = models.CharField(_("Name"), max_length=512)
    price = models.DecimalField(_("Price"), max_digits=14, decimal_places=4, default=Decimal('0.00'))


class Material(models.Model):
    material_type = models.ForeignKey(MaterialType, null=True, related_name="materials", on_delete=models.SET_NULL)
    name = models.CharField(_("Name"), max_length=512)
