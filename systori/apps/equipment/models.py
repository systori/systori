from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.template.defaultfilters import date as date_filter


class Equipment(models.Model):
    GASOLINE = 'gasoline'
    PREMIUM_GASOLINE = 'premium_gasoline'
    DIESEL = 'diesel'
    PREMIUM_DIESEL = 'premium_diesel'
    ELECTRIC = 'electric'

    FUEL_CHOICES = (
        (GASOLINE, _('gasoline')),
        (PREMIUM_GASOLINE, _('premium gasoline')),
        (DIESEL, _('diesel')),
        (PREMIUM_DIESEL, _('premium diesel')),
        (ELECTRIC, _('electric'))
    )

    active = models.BooleanField(_('active'), default=True)
    name = models.CharField(_("Name"), max_length=255)
    manufacturer = models.CharField(_("Manufacturer"), max_length=255)

    # Vehicle specific fields
    license_plate = models.CharField(_('license plate'), max_length=10, blank=True)
    number_of_seats = models.IntegerField(_('number of seats'), default=2)
    icon = models.ImageField(_('Icon'), blank=True)
    fuel = models.CharField(_('fuel'), max_length=255, choices=FUEL_CHOICES, default=DIESEL)
    last_refueling_stop = models.DateTimeField(_('last refueling stop'), blank=True, null=True)

    @cached_property
    def mileage(self):
        refuelingstop = self.refuelingstop_set.aggregate(
            max_mileage=models.Max('mileage')
        ).get('max_mileage', Decimal(0))
        maintenance = self.maintenance_set.aggregate(
            max_mileage=models.Max('mileage')
        ).get('max_mileage', Decimal(0))
        if not maintenance or refuelingstop > maintenance:
            return refuelingstop
        else:
            return maintenance

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
        if self.license_plate:
            return '{} - {}P - {}'.format(self.license_plate, self.number_of_seats, self.name)
        return "{}".format(self.name)


class RefuelingStop(models.Model):

    equipment = models.ForeignKey(Equipment, verbose_name=_('equipment'), on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=timezone.now, db_index=True)
    mileage = models.DecimalField(_('mileage'), max_digits=9, decimal_places=2,
                                  validators=[MinValueValidator(Decimal('0.01'))])
    distance = models.DecimalField(_('distance'), max_digits=9, decimal_places=2, blank=True, null=True,
                                   validators = [MinValueValidator(Decimal('0.01'))])
    liters = models.DecimalField(_('refueled liters'), max_digits=5, decimal_places=2, default=Decimal(0),
                                 validators=[MinValueValidator(Decimal('0.01'))])
    price_per_liter = models.DecimalField(_('price per liter'), max_digits=6, decimal_places=3,
                                          validators=[MinValueValidator(Decimal('0.001'))])
    average_consumption = models.DecimalField(_('average consumption'), max_digits=6, decimal_places=2,
                                              null=True, blank=True)

    def __str__(self):
        return '{}: {} {} {} {} {}'.format(self.id, date_filter(self.datetime), self.liters, _('l'), self.mileage, _('km'))

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
        # Save average consumption
        if self.equipment:
            self.calc_average_consumption()
            # Update last_refueling_stop in equipment object/table
            if not self.equipment.last_refueling_stop or not self.younger_refueling_stop:
                self.equipment.last_refueling_stop = self.datetime
                self.equipment.save()
        super(RefuelingStop, self).save(*args, **kwargs)

    def calc_average_consumption(self):
        if self.older_refueling_stop is None:
            last_mileage = Decimal(0)
        else:
            last_mileage = self.older_refueling_stop.mileage
        self.distance = self.mileage - last_mileage
        self.average_consumption = round(self.liters/self.distance*100, 2)


# The cascade_true Flag is set in the UpdateView and it's only set once to prevent unlimited recursive calls
# therefor a try except block is needed to catch the expected AttributeError
@receiver(post_save, sender=RefuelingStop)
def calc_average_consumption_cascade(sender, instance, **kwargs):
    try:
        if instance.cascade_save and instance.younger_refueling_stop is not None:
            instance.younger_refueling_stop.save()
    except AttributeError:
        pass


class Maintenance(models.Model):

    equipment = models.ForeignKey(Equipment, verbose_name=_('equipment'), on_delete=models.CASCADE)
    date = models.DateField(_('date'), default=timezone.now)
    mileage = models.DecimalField(_('mileage'), max_digits=9, decimal_places=2,
                                  validators=[MinValueValidator(Decimal('0.01'))])
    description = models.TextField(_('description'))
    contractor = models.CharField(_('contractor'), max_length=100, blank=True)
    cost = models.DecimalField(_("cost"), max_digits=14, decimal_places=4, default=Decimal(0),
                               validators=[MinValueValidator(Decimal('0.01'))])

    def __str__(self):
        return "{}: {}".format(date_filter(self.date), self.cost)