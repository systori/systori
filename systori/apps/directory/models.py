from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class Contact(models.Model):
    projects = models.ManyToManyField('project.Project', through='ProjectContact', related_name="contacts")

    business = models.CharField(_("Business"), max_length=512, blank=True)

    salutation = models.CharField(_("Salutation"), max_length=512, blank=True)
    first_name = models.CharField(_("First Name"), max_length=512, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=512, blank=True)

    phone = models.CharField(_("Phone"), max_length=512, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    website = models.URLField(_("Website"), blank=True)

    address = models.CharField(_("Address"), max_length=512, blank=True)
    postal_code = models.CharField(_("Postal Code"), max_length=512, blank=True)
    city = models.CharField(_("City"), max_length=512, blank=True)
    country = models.CharField(_("Country"), max_length=512, default=settings.DEFAULT_COUNTRY)

    is_address_label_generated = models.BooleanField(_("auto-generate address label"), default=True)
    address_label = models.TextField(_("Address Label"), blank=True)

    notes = models.TextField(_("Notes"), blank=True)

    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class ProjectContact(models.Model):
    CUSTOMER = "customer"
    CONTRACTOR = "contractor"
    SUPPLIER = "supplier"
    ARCHITECT = "architect"
    OTHER = "other"
    ASSOCIATION_TYPE = (
        (CUSTOMER, _("Customer")),
        (CONTRACTOR, _("Contractor")),
        (SUPPLIER, _("Supplier")),
        (ARCHITECT, _("Architect")),
        (OTHER, _("Other")),
    )
    association = models.CharField(_('Association'), max_length=128, choices=ASSOCIATION_TYPE, default=CUSTOMER)
    is_billable = models.BooleanField(_('Is Billable?'), default=False)

    project = models.ForeignKey("project.Project", related_name="project_contacts")
    contact = models.ForeignKey(Contact, related_name="project_contacts")

    notes = models.TextField(_("Notes"), blank=True)

    class Meta:
        verbose_name = _("Project Contact")
        verbose_name_plural = _("Project Contacts")
        ordering = ['association', 'id']

    def save(self, **kwargs):
        if self.is_billable:
            self.project.project_contacts.update(is_billable=False)
        return super(ProjectContact, self).save(**kwargs)