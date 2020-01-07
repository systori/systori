from datetime import date, datetime
from decimal import Decimal

from freezegun import freeze_time
from django.test import TestCase
from django.utils.translation import activate

from systori.apps.company.factories import CompanyFactory
from systori.apps.user.factories import UserFactory

import systori.apps.document.models as models
import systori.apps.document.serializers as serializers

from systori.apps.project.factories import *
from systori.apps.document.factories import *
from systori.apps.directory.factories import *
from systori.apps.task.factories import *

from systori.lib.testing import ClientTestCase


class ProposalJsonJobSerializerTest(TestCase):
    def setUp(self):
        activate("en")
        CompanyFactory()
        self.project = ProjectFactory()
        ContactFactory(project=self.project)
        self.letterhead = LetterheadFactory()
        self.job = JobFactory(project=self.project)
        self.group = GroupFactory(parent=self.job)
        self.task = TaskFactory(group=self.group)
        self.lineitem = LineItemFactory(task=self.task)

    def test_can_serialize_single_non_attached_job(self):
        proposal = models.Proposal.objects.create(
            project=self.project, letterhead=self.letterhead
        )

        self.maxDiff = None
        job_serializer = serializers.ProposalJsonJobSerializer(
            proposal=proposal, instance=self.job
        )

        self.assertDictEqual(
            {
                "pk": 1,
                "job.id": 1,
                "name": self.job.name,
                "code": "01",
                "description": "",
                "groups": [
                    {
                        "pk": 2,
                        "group.id": 2,
                        "name": self.group.name,
                        "code": "01.01",
                        "description": "",
                        "order": 1,
                        "groups": [],
                        "tasks": [
                            {
                                "pk": 1,
                                "task.id": 1,
                                "code": "01.01.001",
                                "name": self.task.name,
                                "description": "",
                                "order": 1,
                                "qty": "0.000",
                                "qty_equation": "",
                                "unit": "",
                                "price": "0.00",
                                "price_equation": "",
                                "total": "0.00",
                                "total_equation": "",
                                "estimate": "0.00",
                                "variant_group": 0,
                                "variant_serial": 0,
                                "is_provisional": False,
                                "parent": 2,
                                "lineitems": [
                                    {
                                        "pk": 1,
                                        "lineitem.id": 1,
                                        "token": None,
                                        "name": self.lineitem.name,
                                        "order": 1,
                                        "qty": "0.000",
                                        "qty_equation": "",
                                        "unit": "",
                                        "price": "0.00",
                                        "price_equation": "",
                                        "total": "0.00",
                                        "total_equation": "",
                                        "estimate": "0.00",
                                        "is_hidden": False,
                                        "lineitem_type": "other",
                                    }
                                ],
                            }
                        ],
                        "parent": 1,
                        "job": 1,
                        "estimate": "0.00",
                    }
                ],
                "tasks": [],
                "order": 1,
                "status": "draft",
                "estimate": {"net": "0.00", "gross": "0.00", "tax": "0.00"},
                "is_attached": False,
                "job.id": 1,
            },
            job_serializer.data,
            job_serializer.data,
        )

    def test_can_serialize_single_attached_job(self):
        proposal = models.Proposal.objects.create(
            project=self.project, letterhead=self.letterhead
        )
        proposal.jobs.add(self.job)
        self.maxDiff = None
        job_serializer = serializers.ProposalJsonJobSerializer(
            proposal=proposal, instance=self.job
        )

        self.assertDictEqual(
            {
                "pk": 1,
                "job.id": 1,
                "name": self.job.name,
                "code": "01",
                "description": "",
                "groups": [
                    {
                        "pk": 2,
                        "group.id": 2,
                        "name": self.group.name,
                        "code": "01.01",
                        "description": "",
                        "order": 1,
                        "groups": [],
                        "tasks": [
                            {
                                "pk": 1,
                                "task.id": 1,
                                "code": "01.01.001",
                                "name": self.task.name,
                                "description": "",
                                "order": 1,
                                "qty": "0.000",
                                "qty_equation": "",
                                "unit": "",
                                "price": "0.00",
                                "price_equation": "",
                                "total": "0.00",
                                "total_equation": "",
                                "estimate": "0.00",
                                "variant_group": 0,
                                "variant_serial": 0,
                                "is_provisional": False,
                                "parent": 2,
                                "lineitems": [
                                    {
                                        "pk": 1,
                                        "lineitem.id": 1,
                                        "token": None,
                                        "name": self.lineitem.name,
                                        "order": 1,
                                        "qty": "0.000",
                                        "qty_equation": "",
                                        "unit": "",
                                        "price": "0.00",
                                        "price_equation": "",
                                        "total": "0.00",
                                        "total_equation": "",
                                        "estimate": "0.00",
                                        "is_hidden": False,
                                        "lineitem_type": "other",
                                    }
                                ],
                            }
                        ],
                        "parent": 1,
                        "job": 1,
                        "estimate": "0.00",
                    }
                ],
                "tasks": [],
                "order": 1,
                "status": "draft",
                "estimate": {"net": "0.00", "gross": "0.00", "tax": "0.00"},
                "is_attached": True,
                "job.id": 1,
            },
            job_serializer.data,
            job_serializer.data,
        )


class ProposalSerializerTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        letterhead_pdf = os.path.join(
            settings.BASE_DIR, "apps/document/test_data/letterhead.pdf"
        )
        letterhead = Letterhead.objects.create(
            name="Test Letterhead", letterhead_pdf=letterhead_pdf
        )
        DocumentSettings.objects.create(
            language="en",
            evidence_letterhead=letterhead,
            proposal_letterhead=letterhead,
            invoice_letterhead=letterhead,
        )
        doc_settings = DocumentSettings.objects.first()
        self.letterhead = doc_settings.proposal_letterhead
        self.billable_contact = ContactFactory(
            salutation="Mr",
            first_name="Billable",
            last_name="Contact",
            project=self.project,
            is_billable=True,
        )

    @freeze_time(datetime(2020, 1, 1))
    def test_can_create_proposal(self):
        job = JobFactory(project=self.project, name="Test job")
        serializer = serializers.ProposalSerializer(
            data={
                "json": {
                    "title": "test proposal",
                    "header": "test header",
                    "footer": "test footer",
                    "add_terms": False,
                    "show_project_id": True,
                    "doc_template": None,
                },
                "jobs": [job.id],
                "project_id": self.project.pk,
                "document_date": "2019-12-31",
                "notes": None,
            }
        )
        serializer.is_valid()
        serializer.save()

        proposal = models.Proposal.objects.first()
        self.assertEqual(proposal.jobs.first().id, 1)
        saved_json = proposal.json
        self.assertDictEqual(
            {
                "title": "test proposal",
                "header": "test header",
                "footer": "test footer",
                "show_project_id": True,
                "add_terms": False,
                "doc_template": None,
                "business": "",
                "salutation": "Mr",
                "first_name": "Billable",
                "last_name": "Contact",
                "address": "",
                "postal_code": "",
                "city": "",
                "address_label": "",
                "jobs": [
                    {
                        "pk": 1,
                        "name": "Test job",
                        "code": "01",
                        "description": "",
                        "groups": [],
                        "tasks": [],
                        "order": 1,
                        "status": "proposed",
                        "estimate": {"net": "0.00", "gross": "0.00", "tax": "0.00"},
                        "is_attached": True,
                        "job.id": 1,
                    }
                ],
                "estimate_total": {"net": "0.00", "gross": "0.00", "tax": "0.00"},
                "created_on": "2020-01-01T00:00:00Z",
                "document_date": "2019-12-31",
                "notes": None,
                "project_id": 2,
            },
            saved_json,
            saved_json,
        )

    @freeze_time(datetime(2020, 1, 1))
    def test_can_update_proposal(self):
        job = JobFactory(project=self.project, name="Test job")
        task = TaskFactory(
            name="abc",
            qty=Decimal(1),
            price=Decimal(5),
            total=Decimal(5),
            job=job,
            group=job,
        )
        lineitem = LineItemFactory(
            task=task, name="item 1", qty=Decimal(1), price=Decimal(5), total=Decimal(5)
        )
        proposal = ProposalFactory(
            letterhead=self.letterhead,
            project=self.project,
            document_date=date(2019, 12, 31),
        )
        proposal.jobs.add(job)

        self.assertDictEqual({}, proposal.json, proposal.json)
        serializer = serializers.ProposalSerializer(
            instance=proposal,
            data={
                "json": {
                    "title": "test proposal",
                    "header": "test header",
                    "footer": "test footer",
                    "add_terms": False,
                    "show_project_id": True,
                    "doc_template": None,
                },
                "notes": "Some notes",
            },
            partial=True,
        )
        serializer.is_valid()
        serializer.save()

        proposal = Proposal.objects.first()
        self.assertDictEqual(
            {
                "title": "test proposal",
                "header": "test header",
                "footer": "test footer",
                "show_project_id": True,
                "add_terms": False,
                "doc_template": None,
                "business": "",
                "salutation": "Mr",
                "first_name": "Billable",
                "last_name": "Contact",
                "address": "",
                "postal_code": "",
                "city": "",
                "address_label": "",
                "jobs": [
                    {
                        "pk": 1,
                        "name": "Test job",
                        "code": "01",
                        "description": "",
                        "groups": [],
                        "tasks": [
                            {
                                "pk": 1,
                                "code": "01.001",
                                "name": "abc",
                                "description": "",
                                "order": 1,
                                "qty": "1.000",
                                "qty_equation": "",
                                "unit": "",
                                "price": "5.00",
                                "price_equation": "",
                                "total": "5.00",
                                "total_equation": "",
                                "estimate": "5.00",
                                "variant_group": 0,
                                "variant_serial": 0,
                                "is_provisional": False,
                                "parent": 1,
                                "lineitems": [
                                    {
                                        "pk": 1,
                                        "token": None,
                                        "name": "item 1",
                                        "order": 1,
                                        "qty": "1.000",
                                        "qty_equation": "",
                                        "unit": "",
                                        "price": "5.00",
                                        "price_equation": "",
                                        "total": "5.00",
                                        "total_equation": "",
                                        "estimate": "5.00",
                                        "is_hidden": False,
                                        "lineitem_type": "other",
                                        "lineitem.id": 1,
                                    }
                                ],
                                "task.id": 1,
                            }
                        ],
                        "order": 1,
                        "status": "proposed",
                        "estimate": {"net": "5.00", "gross": "5.95", "tax": "0.95"},
                        "is_attached": True,
                        "job.id": 1,
                    }
                ],
                "estimate_total": {"net": "5.00", "gross": "5.95", "tax": "0.95"},
                "created_on": "2020-01-01T00:00:00Z",
                "document_date": "2019-12-31",
                "notes": "Some notes",
                "project_id": 2,
            },
            proposal.json,
            proposal.json,
        )
