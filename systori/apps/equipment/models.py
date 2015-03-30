from django.db import models
from django.utils.translation import ugettext_lazy as _


class Equipment(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    manufacturer = models.CharField(_("Manufacturer"), max_length=255)

    purchase_date = models.DateField(_("Purchase Date"), blank=True, null=True)
    purchase_price = models.DecimalField(_("Purchase Price"), max_digits=14,
                                         decimal_places=2, default=0.0)

    def __str__(self):
        return self.name
