from datetime import timedelta, date, datetime
from decimal import Decimal
from freezegun import freeze_time
from django.urls import reverse
from django.utils.translation import get_language
from django.utils.timezone import localtime, now
from django.utils.formats import date_format

from rest_framework import status

from systori.lib.testing import ClientTestCase

from systori.apps.document.api import ProposalModelViewSet
from systori.apps.project.factories import *
from systori.apps.document.factories import *
from systori.apps.directory.factories import *
from systori.apps.task.factories import *


class DocumentTemplateApiTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.contact = ContactFactory(
            salutation="Mr",
            first_name="Ben",
            last_name="Schmidt",
            project=self.project,
            is_billable=True,
        )

    def test_english_variables(self):
        self.user.language = "en"
        self.user.save()
        doc = DocumentTemplateFactory(
            header="this is a [firstname] test [today]",
            footer="thx and goodbye [today +14]",
        )
        response = self.client.get(
            reverse(
                "documenttemplate-for-project",
                kwargs={"pk": doc.pk, "project_pk": self.project.pk},
            ),
            format="json",
        )
        date_now = localtime(now()).date()
        self.assertDictEqual(
            {
                "header": "this is a Ben test {}".format(
                    date_format(date_now, use_l10n=True)
                ),
                "footer": "thx and goodbye {}".format(
                    date_format(date_now + timedelta(14), use_l10n=True)
                ),
            },
            response.data,
        )

    def test_german_variables(self):
        self.user.language = "de"
        self.user.save()
        doc = DocumentTemplateFactory(
            header="this is a [Anrede] [Vorname] [Nachname] [Name] test [heute]",
            footer="thx and goodbye [heute +14] and [heute +21]",
        )
        response = self.client.get(
            reverse(
                "documenttemplate-for-project",
                kwargs={"pk": doc.pk, "project_pk": self.project.pk},
            ),
            format="json",
        )
        date_now = localtime(now()).date()
        self.assertDictEqual(
            {
                "header": "this is a Mr Ben Schmidt Mr Ben Schmidt test {}".format(
                    date_format(date_now, use_l10n=True)
                ),
                "footer": "thx and goodbye {} and {}".format(
                    date_format(date_now + timedelta(14), use_l10n=True),
                    date_format(date_now + timedelta(21), use_l10n=True),
                ),
            },
            response.data,
        )


class ProposalApiTest(ClientTestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.jobsite = JobSiteFactory(project=self.project)
        self.billable_contact = ContactFactory(
            salutation="Mr",
            first_name="Billable",
            last_name="Contact",
            project=self.project,
            is_billable=True,
        )
        self.non_billable_contact = ContactFactory(
            salutation="Mr",
            first_name="Non-Billable",
            last_name="Contact",
            project=self.project,
            is_billable=False,
        )
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

    @freeze_time(datetime(2020, 1, 1))
    def test_can_create_proposal(self):
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

        response = self.client.post(
            f"/api/document/proposal/",
            {
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
            },
            format="json",
        )
        self.assertEquals(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertDictEqual(
            {
                "created_on": "2020-01-01T01:00:00+01:00",
                "document_date": "2019-12-31",
                "notes": None,
                "id": 1,
                "project_id": 2,
                "jobs": [1],
                "status": "new",
                "json": {
                    "title": "test proposal",
                    "header": "test header",
                    "footer": "test footer",
                    "show_project_id": True,
                    "add_terms": False,
                    "doc_template": None,
                },
                "letterhead": 1,
                "billable_contact": {
                    "id": 1,
                    "business": "",
                    "salutation": "Mr",
                    "first_name": "Billable",
                    "last_name": "Contact",
                    "phone": "",
                    "email": "",
                    "website": "",
                    "address": "",
                    "postal_code": "",
                    "city": "",
                    "country": "Deutschland",
                    "is_address_label_generated": True,
                    "address_label": "",
                    "notes": "",
                    "projects": [2],
                },
                "estimate_total": {"net": "5.00", "gross": "5.95", "tax": "0.95"},
            },
            response.json(),
            response.json(),
        )

        proposals = Proposal.objects.all()
        self.assertEqual(len(proposals), 1)
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
                        "estimate": {"net": "5.00", "gross": "5.95", "tax": "0.95"},
                        "is_attached": True,
                        "job.id": 1,
                    }
                ],
                "estimate_total": {"net": "5.00", "gross": "5.95", "tax": "0.95"},
                "created_on": "2020-01-01T00:00:00Z",
                "document_date": "2019-12-31",
                "notes": None,
                "project_id": 2,
            },
            proposals.first().json,
            proposals.first().json,
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

        response = self.client.patch(
            f"/api/document/proposal/{proposal.id}/",
            {
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
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertDictEqual(
            {
                "created_on": "2020-01-01T01:00:00+01:00",
                "document_date": "2019-12-31",
                "notes": "Some notes",
                "id": 1,
                "project_id": 2,
                "jobs": [1],
                "status": "new",
                "json": {
                    "title": "test proposal",
                    "header": "test header",
                    "footer": "test footer",
                    "show_project_id": True,
                    "add_terms": False,
                    "doc_template": None,
                },
                "letterhead": 1,
                "billable_contact": {
                    "id": 1,
                    "business": "",
                    "salutation": "Mr",
                    "first_name": "Billable",
                    "last_name": "Contact",
                    "phone": "",
                    "email": "",
                    "website": "",
                    "address": "",
                    "postal_code": "",
                    "city": "",
                    "country": "Deutschland",
                    "is_address_label_generated": True,
                    "address_label": "",
                    "notes": "",
                    "projects": [2],
                },
                "estimate_total": {"net": "5.00", "gross": "5.95", "tax": "0.95"},
            },
            response.json(),
            response.json(),
        )
        saved_json = Proposal.objects.first().json
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
            saved_json,
            saved_json,
        )
