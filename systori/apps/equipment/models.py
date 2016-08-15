from decimal import Decimal
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
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
    active = models.BooleanField(_('active'), default=True)
    name = models.CharField(_("Name"), max_length=255)
    manufacturer = models.CharField(_("Manufacturer"), max_length=255)

    purchase_date = models.DateField(_("Purchase Date"), blank=True, null=True)
    purchase_price = models.DecimalField(_("Purchase Price"), max_digits=14, decimal_places=2, default=Decimal(0))

    # Vehicle specific fields
    license_plate = models.CharField(_('license plate'), max_length=10, blank=True)
    number_of_seats = models.IntegerField(_('number of seats'), default=2)
    icon = models.ImageField(_('Icon'), blank=True)
    fuel = models.CharField(_('fuel'), max_length=255, choices=FUEL_CHOICES, default=DIESEL)
    last_refueling_stop = models.DateTimeField(_('last refueling stop'), blank=True, null=True)

    @cached_property
    def mileage(self):
        refuelingstop = self.refuelingstop_set.aggregate(
            m=models.Max('mileage')
        ).get('m', Decimal(0))
        defect = self.defect_set.aggregate(
            m=models.Max('mileage')
        ).get('m', Decimal(0))
        if not defect or refuelingstop > defect:
            return refuelingstop
        else:
            return defect

    @cached_property
    def average_consumption(self):
        consumption = self.refuelingstop_set.aggregate(
            average_consumption=models.Avg('average_consumption')
        ).get('average_consumption')
        if consumption:
            return round(consumption, 2)
        else:
            return _("unknown")

    def __str__(self):
        return self.name


class RefuelingStop(models.Model):

    class Meta:
        verbose_name = _('refueling stop')
        verbose_name_plural = _('refueling stops')

    equipment = models.ForeignKey(Equipment, verbose_name=_('equipment'))
    datetime = models.DateTimeField(default=timezone.now, db_index=True)
    mileage = models.DecimalField(_('mileage'), max_digits=8, decimal_places=2)
    distance = models.DecimalField(_('distance'), max_digits=6, decimal_places=2, blank=True, null=True)
    liters = models.DecimalField(_('refueled liters'), max_digits=5, decimal_places=2, default=Decimal(0))
    price_per_liter = models.DecimalField(_('price per liter'), max_digits=6, decimal_places=3)
    average_consumption = models.DecimalField(_('average consumption'), max_digits=5, decimal_places=2,
                                              null=True, blank=True)
    cascade = False
    update_younger = False

    def __str__(self):
        return '{}: {} {} {} {} {}'.format(self.id, _date(self.datetime), self.liters, _('l'), self.mileage, _('km'))

    @cached_property
    def older_refueling_stop(self):
        older_refueling_stop = RefuelingStop.objects.filter(
            equipment_id=self.equipment.id,
            mileage__lt=self.mileage
        ).exclude(id=self.id).order_by('-mileage').first()
        return older_refueling_stop

    @cached_property
    def younger_refueling_stop(self):
        younger_refueling_stop = RefuelingStop.objects.filter(
            equipment_id=self.equipment.id,
            mileage__gt=self.mileage
        ).exclude(id=self.id).order_by('mileage').first()
        return younger_refueling_stop

    def save(self, *args, **kwargs):
        # Update last_refueling_stop in equipment object/table
        if self.equipment and (not self.equipment.last_refueling_stop or not self.younger_refueling_stop):
            self.equipment.last_refueling_stop = self.datetime
            self.equipment.save()
        # Save average consumption
        if self.equipment:
            self.calc_average_consumption()
        super(RefuelingStop, self).save(*args, **kwargs)

    def calc_average_consumption(self):
        if self.older_refueling_stop is None:
            last_mileage = Decimal(0)
        else:
            last_mileage = self.older_refueling_stop.mileage
        new_distance = self.mileage - last_mileage
        if self.distance is not new_distance:
            self.update_younger = True
            self.distance = new_distance
        self.average_consumption = round(self.liters/self.distance*100, 2)
        if self.younger_refueling_stop is not None and self.update_younger:
            self.cascade = True

# todo: change flags to UI provided flag in case it's needed

@receiver(post_save, sender=RefuelingStop)
def calc_average_consumption_cascade(sender, **kwargs):
    refueling_stop = kwargs.get('instance')
    if refueling_stop.cascade:
        refueling_stop.younger_refueling_stop.save()


class Defect(models.Model):

    class Meta:
        verbose_name = _('defect')
        verbose_name_plural = _('defects')

    equipment = models.ForeignKey(Equipment, verbose_name=_('equipment'))
    date = models.DateField(_('date'), default=timezone.now)
    mileage = models.IntegerField(_('mileage'))
    description = models.TextField(_('description'))
    repaired = models.BooleanField(_('repaired'))
    contractor = models.CharField(_('contractor'), max_length=100, blank=True)
    cost = models.DecimalField(_("cost"), max_digits=14, decimal_places=4, default=Decimal(0))

    def __str__(self):
        if self.repaired:
            _repaired = _('repaired')
        else:
            _repaired = _('not repaired')
        return u"%s %s" % (_date(self.date), _repaired)