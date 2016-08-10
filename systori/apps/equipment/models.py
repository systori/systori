from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import date as _date

GASOLINE = 'gasoline'
DIESEL = 'diesel'
ELECTRIC = 'electric'

FUEL_CHOICES = (
    (GASOLINE, _('gasoline')),
    (DIESEL, _('diesel')),
    (ELECTRIC, _('electric'))
)


class Equipment(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    manufacturer = models.CharField(_("Manufacturer"), max_length=255)

    purchase_date = models.DateField(_("Purchase Date"), blank=True, null=True)
    purchase_price = models.DecimalField(_("Purchase Price"), max_digits=14, decimal_places=2, default=0.0)

    # Vehicle specific fields
    license_plate = models.CharField(_('license plate'), max_length=10, blank=True)
    number_of_seats = models.IntegerField(_('number of seats'), default=2)
    icon = models.ImageField(_('Icon'), blank=True)
    fuel = models.CharField(_('fuel'), max_length=100, choices=FUEL_CHOICES, default=DIESEL)
    last_refueling_stop = models.DateField(_('last refueling stop'), blank=True, editable=False)

    @property
    def mileage(self):
        refuelingstop = self.refuelingstop_set.aggregate(
            m=models.Max('mileage')
        ).get('m', 0)
        defect = self.defect_set.aggregate(
            m=models.Max('mileage')
        ).get('m', 0)
        if refuelingstop > defect:
            return refuelingstop
        else:
            return defect

    mileage.short_description = _('mileage')

    @property
    def average_consumption(self):
        consumption = self.refuelingstop_set.aggregate(
            average_consumption=models.Avg('average_consumption')
        ).get('average_consumption')
        if consumption:
            return round(consumption, 2)
        else:
            return _("unknown")

    average_consumption.short_description = _('average consumption')

    def __str__(self):
        return self.name


class RefuelingStop(models.Model):

    class Meta:
        verbose_name = _('refueling stop')
        verbose_name_plural = _('refueling stops')

    vehicle = models.ForeignKey(Equipment, verbose_name=_('vehicle'))
    datetime = models.DateTimeField(blank=True, null=True, db_index=True)
    mileage = models.IntegerField(_('mileage'))
    liters = models.DecimalField(_('refueled liters'), max_digits=4, decimal_places=2, default=0.0)
    price_per_liter = models.FloatField(_('price per liter'))
    average_consumption = models.FloatField(_('average consumption'), null=True, blank=True, editable=False)

    def __str__(self):
        return u"%s %s %s" % (_date(self.date), self.liters, _('liters'))

    def save(self, *args, **kwargs):
        # Update last_refueling_stop in vehicle object/table
        if self.vehicle and (self.vehicle.last_refueling_stop is None \
        or self.vehicle.last_refueling_stop < self.date):
            self.vehicle.last_refueling_stop = self.date
            self.vehicle.save()
        # Save average consumption
        if self.vehicle:
            self.average_consumption = self.calc_average_consumption()
        super(RefuelingStop, self).save(*args, **kwargs)

    @property
    def average_consumption(self):
        if not (self.vehicle and self.date and self.mileage and self.liters):
            return "unknow"
        older_refueling_stops = RefuelingStop.objects.filter(
            vehicle_id=self.vehicle.id,
            date__lt=self.date
        ).order_by('-date')
        if older_refueling_stops.count() == 0:
            return None
        else:
            last_mileage = older_refueling_stops[0].mileage
        distance = self.mileage - last_mileage
        return round((self.liters * 100) / distance, 2)


class Defect(models.Model):

    class Meta:
        verbose_name = _('defect')
        verbose_name_plural = _('defects')

    vehicle = models.ForeignKey(Equipment, verbose_name=_('vehicle'))
    date = models.DateField(_('date'))
    mileage = models.IntegerField(_('mileage'))
    description = models.TextField(_('description'))
    repaired = models.BooleanField(_('repaired'))
    contractor = models.CharField(_('contractor'), max_length=100)
    cost = models.DecimalField(_("cost"), max_digits=14, decimal_places=4, default=0.0)

    def __unicode__(self):
        if self.repaired:
            _repaired = _('repaired')
        else:
            _repaired = _('not repaired')
        return u"%s %s" % (_date(self.date), _repaired)