from django.db import models
from django.utils.translation import ugettext_lazy as _
#from systori.lib.db import LtreeField


class Equipment(models.Model):
    uses_count = models.PositiveIntegerField(_("Uses count"), default=0)
    name = models.CharField(_("Name"), max_length=30)

    purchasing_date = models.DateField(_("Purchasing Date"), blank=True, null=True)
    purchasing_price = models.DateField(_("Purchasing Price"), blank=True, null=True)

    #type = LtreeField()
    manufacturer = models.CharField(_("Manufacturer"), max_length=255)

    def get_info(self):
        return "{} - {}".format(self.manufacturer, self.name)


class Vehicle(Equipment):
    license_plate = models.CharField(_("License Plate"), max_length=20)

    def get_info(self):
        return "{}".format(self.license_plate)
