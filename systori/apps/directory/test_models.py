from django.test import TestCase
from ..company.models import Company
from ..project.models import *
from .models import *


def create_contact_data(self):
    self.company = Company.objects.create(schema="test", name="Test")
    self.company.activate()
    self.project = Project.objects.create(name="my project")
    self.contact = Contact.objects.create(first_name="Ludwig", last_name="von Mises")


class ContactProjectTests(TestCase):
    def setUp(self):
        create_contact_data(self)

    def test_no_association(self):
        self.assertEquals(0, len(self.contact.projects.all()))
        self.assertEquals(0, len(self.contact.project_contacts.all()))
        self.assertEquals(0, len(self.project.contacts.all()))
        self.assertEquals(0, len(self.project.project_contacts.all()))

    def test_customer_association(self):
        ProjectContact.objects.create(
            project=self.project,
            contact=self.contact,
            association=ProjectContact.CUSTOMER,
        )
        self.assertEquals(1, len(self.contact.projects.all()))
        self.assertEquals(1, len(self.project.contacts.all()))
        pc = ProjectContact.objects.get(project=self.project)
        self.assertEquals(ProjectContact.CUSTOMER, pc.association)


class BillableContactTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(schema="test", name="Test")
        self.company.activate()
        self.project = Project.objects.create(name="my project")
        self.pc1 = ProjectContact.objects.create(
            project=self.project,
            contact=Contact.objects.create(first_name="A 1", last_name="B 1"),
        )
        self.pc2 = ProjectContact.objects.create(
            project=self.project,
            contact=Contact.objects.create(first_name="A 2", last_name="B 2"),
        )

    def test_no_billable_set(self):
        self.assertEqual(
            0, self.project.project_contacts.filter(is_billable=True).count()
        )

    def test_billable_set(self):
        self.pc1.is_billable = True
        self.pc1.save()
        self.assertEqual(
            1, self.project.project_contacts.filter(is_billable=True).count()
        )

    def test_only_one_contact_can_be_billable(self):
        self.pc1.is_billable = True
        self.pc1.save()
        self.assertEqual(
            1, self.project.project_contacts.filter(is_billable=True).count()
        )
        self.assertEqual(
            self.pc1, self.project.project_contacts.filter(is_billable=True).get()
        )

        self.pc2.is_billable = True
        self.pc2.save()
        self.assertEqual(
            1, self.project.project_contacts.filter(is_billable=True).count()
        )
        self.assertEqual(
            self.pc2, self.project.project_contacts.filter(is_billable=True).get()
        )
