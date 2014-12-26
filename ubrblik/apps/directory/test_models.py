from django.test import TestCase
from django.contrib.auth import get_user_model
from ..project.models import *
from .models import *


class ContactProjectTests(TestCase):

    def setUp(self):
        self.project = Project.objects.create(name="my project")
        self.contact = Contact.objects.create(first_name="A", last_name="B")

    def test_no_association(self):
        self.assertEquals(0, len(self.contact.projects.all()))
        self.assertEquals(0, len(self.contact.project_contacts.all()))
        self.assertEquals(0, len(self.project.contacts.all()))
        self.assertEquals(0, len(self.project.project_contacts.all()))

    def test_customer_association(self):
        ProjectContact.objects.create(project=self.project, contact=self.contact, association=ProjectContact.CUSTOMER)
        self.assertEquals(1, len(self.contact.projects.all()))
        self.assertEquals(1, len(self.project.contacts.all()))
        pc = ProjectContact.objects.get(project=self.project)
        self.assertEquals(ProjectContact.CUSTOMER, pc.association)