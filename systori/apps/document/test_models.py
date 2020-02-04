from decimal import Decimal
from datetime import datetime, timedelta
from django.test import TestCase
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.translation import activate

from ..company.factories import CompanyFactory
from ..user.factories import UserFactory
from ..project.factories import ProjectFactory, JobSiteFactory
from ..task.factories import JobFactory, GroupFactory, TaskFactory, LineItemFactory
from ..directory.factories import ContactFactory

from ..timetracking.models import Timer
from systori.lib.accounting.tools import Amount

from . import type as pdf_type
from .models import Proposal, Invoice, Timesheet
from .factories import LetterheadFactory, DocumentTemplateFactory


class ProposalTests(TestCase):
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

    def test_status_new(self):
        d = Proposal.objects.create(project=self.project, letterhead=self.letterhead)
        self.assertEquals("New", d.get_status_display())
        self.assertEquals(
            ["Send"], [t.custom["label"] for t in d.get_available_status_transitions()]
        )

    def test_status_sent(self):
        d = Proposal.objects.create(project=self.project, letterhead=self.letterhead)
        d.send()
        d.save()
        d = Proposal.objects.get(pk=d.pk)
        self.assertEquals("Sent", d.get_status_display())
        # TODO: for some reason result of get_available_status_transitions() is not consistently sorted
        labels = [str(t.custom["label"]) for t in d.get_available_status_transitions()]
        labels.sort()
        self.assertEquals(["Approve", "Decline"], labels)

    def test_serialize(self):
        proposal = Proposal.objects.create(
            project=self.project, letterhead=self.letterhead
        )
        proposal.json = {"jobs": [{"job": self.job}], "add_terms": False}
        pdf_type.proposal.serialize(proposal)
        self.maxDiff = None
        self.assertEqual(
            {
                "add_terms": False,
                "jobs": [
                    {
                        "tasks": [],
                        "groups": [
                            {
                                "group.id": 2,
                                "code": "01.01",
                                "name": self.group.name,
                                "description": "",
                                "estimate": Decimal("0.0000"),
                                "groups": [],
                                "tasks": [
                                    {
                                        "task.id": 1,
                                        "code": "01.01.001",
                                        "name": self.task.name,
                                        "description": "",
                                        "is_provisional": False,
                                        "variant_group": 0,
                                        "variant_serial": 0,
                                        "qty": Decimal("0.0000"),
                                        "unit": "",
                                        "price": Decimal("0.0000"),
                                        "estimate": Decimal("0.0000"),
                                        "lineitems": [
                                            {
                                                "lineitem.id": 1,
                                                "name": self.lineitem.name,
                                                "price": Decimal("0.0000"),
                                                "estimate": Decimal("0.0000"),
                                                "qty": Decimal("0.0000"),
                                                "unit": "",
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
            proposal.json,
        )


class InvoiceTests(TestCase):
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

    def test_serialize(self):
        invoice = Invoice.objects.create(
            project=self.project, letterhead=self.letterhead
        )
        invoice.json = {"jobs": [{"job": self.job}], "add_terms": False}
        pdf_type.invoice.serialize(invoice)
        self.maxDiff = None
        self.assertEqual(
            {
                "jobs": [
                    {
                        "tasks": [],
                        "groups": [
                            {
                                "group.id": 2,
                                "code": "01.01",
                                "name": self.group.name,
                                "description": "",
                                "progress": Decimal("0.00"),
                                "estimate": Decimal("0.00"),
                                "tasks": [
                                    {
                                        "task.id": 1,
                                        "code": "01.01.001",
                                        "name": self.task.name,
                                        "description": "",
                                        "is_provisional": False,
                                        "variant_group": 0,
                                        "variant_serial": 0,
                                        "qty": Decimal("0.0000"),
                                        "complete": Decimal("0.000"),
                                        "unit": "",
                                        "price": Decimal("0.0000"),
                                        "progress": Decimal("0.00"),
                                        "estimate": Decimal("0.00"),
                                        "lineitems": [
                                            {
                                                "lineitem.id": 1,
                                                "name": self.lineitem.name,
                                                "qty": Decimal("0.000"),
                                                "unit": "",
                                                "price": Decimal("0.00"),
                                                "estimate": Decimal("0.00"),
                                                "expended": Decimal("0.00"),
                                                "progress": Decimal("0.00"),
                                            }
                                        ],
                                    }
                                ],
                                "groups": [],
                            }
                        ],
                    }
                ],
                "add_terms": False,
                "debit": Amount.zero(),
                "invoiced": Amount.zero(),
                "paid": Amount.zero(),
                "unpaid": Amount.zero(),
                "payments": [],
                "job_debits": {},
            },
            invoice.json,
        )


class DocumentTemplateTests(TestCase):
    def setUp(self):
        CompanyFactory()
        self.project = ProjectFactory()
        self.jobsite = JobSiteFactory(project=self.project)
        ContactFactory(
            first_name="Ludwig",
            last_name="von Mises",
            project=self.project,
            is_billable=True,
        )
        self.letterhead = LetterheadFactory()

    def test_render_english_tpl(self):
        activate("en")
        d = DocumentTemplateFactory(
            header="Dear [lastname]", footer="Thanks [firstname]!"
        )
        r = d.render(self.project)
        self.assertEqual("Dear von Mises", r["header"])
        self.assertEqual("Thanks Ludwig!", r["footer"])

    def test_render_german_tpl(self):
        activate("de")
        d = DocumentTemplateFactory(
            header="Dear [Nachname]",
            footer="Thanks [Vorname]!",
            document_type="invoice",
        )
        r = d.render(self.project)
        self.assertEqual("Dear von Mises", r["header"])
        self.assertEqual("Thanks Ludwig!", r["footer"])

    def test_render_sample_tpl(self):
        activate("en")
        d = DocumentTemplateFactory(
            header="Dear [lastname]",
            footer="Thanks [firstname]!",
            document_type="invoice",
        )
        r = d.render()
        self.assertEqual("Dear Smith", r["header"])
        self.assertEqual("Thanks John!", r["footer"])

    def test_render_all_available_english_tpl(self):
        activate("en")
        d = DocumentTemplateFactory(
            header="Dear [salutation] [firstname] [lastname] [name]",
            footer="Bye [today] [today +14] [today +21] [jobsite] !",
            document_type="invoice",
        )
        r = d.render()
        self.assertEqual("Dear Mr John Smith Mr John Smith", r["header"])
        today = datetime.today()
        self.assertEqual(f"Bye {date_format(today)} {date_format(today+timedelta(14))} {date_format(today+timedelta(21))} Jobsite (Examplestreet No 2, 12345 Examplecity) !", r["footer"])

    def test_render_all_available_german_tpl(self):
        activate("de")
        self.project = None
        d = DocumentTemplateFactory(
            header="Dear [Anrede] [Vorname] [Nachname] [Name]",
            footer="Bye [heute] [heute +14] [heute +21] [Einsatzort] !",
            document_type="invoice",
        )
        r = d.render()
        self.assertEqual("Dear Herr Max Mustermann Herr Max Mustermann", r["header"])
        today = datetime.today()
        self.assertEqual(f"Bye {date_format(today)} {date_format(today+timedelta(14))} {date_format(today+timedelta(21))} Baustelle (Musterstraße 2, 12345 Musterstadt) !", r["footer"])

class TimesheetTests(TestCase):
    def setUp(self):
        self.worker = UserFactory(company=CompanyFactory()).access.first()
        self.letterhead = LetterheadFactory()

    def sheet(self, dt):
        def hrs(secs):
            return secs / 60

        sheet = Timesheet(
            document_date=dt, worker=self.worker, letterhead=self.letterhead
        ).calculate()

        rows = [
            [],  # days
            [],  # work
            [],  # vacation
            [],  # sick
            [],  # paid leave
            [],  # unpaid leave
            [],  # compensation
            [],  # overtime
        ]
        for day in range(sheet.json["total_days"]):
            col = [
                sheet.json["work"][day],
                sheet.json["vacation"][day],
                sheet.json["sick"][day],
                sheet.json["paid_leave"][day],
                sheet.json["unpaid_leave"][day],
                sheet.json["compensation"][day],
                sheet.json["overtime"][day],
            ]
            if any(col):
                rows[0].append(day + 1)
                for row_idx in range(len(col)):
                    rows[row_idx + 1].append(hrs(col[row_idx]))
        rows[0].append("T")  # total column
        rows[1].append(hrs(sheet.json["work_total"]))
        rows[2].append(hrs(sheet.json["vacation_total"]))
        rows[3].append(hrs(sheet.json["sick_total"]))
        rows[4].append(hrs(sheet.json["paid_leave_total"]))
        rows[5].append(hrs(sheet.json["unpaid_leave_total"]))
        rows[6].append(hrs(sheet.json["compensation_total"]))
        rows[7].append(hrs(sheet.json["overtime_total"]))
        rows.append(
            [
                hrs(sheet.json["overtime_transferred"]),
                hrs(sheet.json["overtime_net"]),
                hrs(sheet.json["overtime_balance"]),
            ]
        )
        rows.append(
            [
                hrs(sheet.json["vacation_transferred"]),
                hrs(sheet.json["vacation_added"]),
                hrs(sheet.json["vacation_balance"]),
            ]
        )
        return rows

    def timer(self, start_date, end_hour, kind=Timer.WORK):
        Timer.objects.create(
            worker=self.worker,
            started=start_date.replace(tzinfo=timezone.utc),
            stopped=start_date.replace(hour=end_hour, tzinfo=timezone.utc),
            kind=kind,
        )

    def test_no_timers(self):
        january = datetime(2017, 1, 18, 9)
        self.assertEqual(
            self.sheet(january),
            [
                ["T"],  # days
                [0.0],  # work
                [0.0],  # vacation
                [0.0],  # sick
                [0.0],  # paid leave
                [0.0],  # unpaid leave
                [0.0],  # compensation
                [0.0],  # overtime
                # transferred, net, balance overtime
                [0.0, 0.0, 0.0],
                # transferred, added, balance vacation
                [0.0, 20.0, 20.0],
            ],
        )

    def test_simple_overtime(self):
        january = datetime(2017, 1, 18, 9)
        self.timer(january, 18)
        self.assertEqual(
            self.sheet(january),
            [
                [18, "T"],  # days
                [9.0, 9.0],  # work
                [0.0, 0.0],  # vacation
                [0.0, 0.0],  # sick
                [0.0, 0.0],  # paid leave
                [0.0, 0.0],  # unpaid leave
                [8.0, 8.0],  # compensation
                [1.0, 1.0],  # overtime
                # transferred, net, balance overtime
                [0.0, 1.0, 1.0],
                # transferred, added, balance vacation
                [0.0, 20.0, 20.0],
            ],
        )

    def test_paid_leave(self):
        january = datetime(2017, 1, 18, 9)
        self.timer(january, 16)

        expected = [
            [18, "T"],  # days
            [7.0, 7.0],  # work
            [0.0, 0.0],  # vacation
            [0.0, 0.0],  # sick
            [1.0, 1.0],  # paid leave
            [0.0, 0.0],  # unpaid leave
            [8.0, 8.0],  # compensation
            [0.0, 0.0],  # overtime
            # transferred, net, balance overtime
            [0.0, -1.0, -1.0],
            # transferred, added, balance vacation
            [0.0, 20.0, 20.0],
        ]

        # Automatically applied paid_leave
        self.assertEqual(self.sheet(january), expected)

        # Manually applied paid_leave, should be same result
        self.timer(january.replace(hour=16), 17, Timer.PAID_LEAVE)
        self.assertEqual(self.sheet(january), expected)

    def test_full_work_day_plus_extra_manual_paid_leave(self):
        january = datetime(2017, 1, 18, 9)
        self.timer(january, 17)  # full work day
        self.timer(january.replace(hour=17), 19, Timer.PAID_LEAVE)
        # because paid_leave is manually set it takes us over 8hrs compensation
        self.assertEqual(
            self.sheet(january),
            [
                [18, "T"],  # days
                [8.0, 8.0],  # work
                [0.0, 0.0],  # vacation
                [0.0, 0.0],  # sick
                [2.0, 2.0],  # paid leave
                [0.0, 0.0],  # unpaid leave
                [10.0, 10.0],  # compensation
                [0.0, 0.0],  # overtime
                # transferred, net, balance overtime
                [0.0, -2.0, -2.0],
                # transferred, added, balance vacation
                [0.0, 20.0, 20.0],
            ],
        )

    def test_partial_work_day_plus_extra_manual_paid_leave(self):
        january = datetime(2017, 1, 18, 9)
        self.timer(january, 16)  # 7hr work day
        self.timer(
            january.replace(hour=16), 19, Timer.PAID_LEAVE
        )  # 3hr manual paid leave
        # because paid_leave is manually set it takes us over 8hrs compensation
        self.assertEqual(
            self.sheet(january),
            [
                [18, "T"],  # days
                [7.0, 7.0],  # work
                [0.0, 0.0],  # vacation
                [0.0, 0.0],  # sick
                [3.0, 3.0],  # paid leave
                [0.0, 0.0],  # unpaid leave
                [10.0, 10.0],  # compensation
                [0.0, 0.0],  # overtime
                # transferred, net, balance overtime
                [0.0, -3.0, -3.0],
                # transferred, added, balance vacation
                [0.0, 20.0, 20.0],
            ],
        )

    def test_overtime_and_paid_leave(self):
        january = datetime(2017, 1, 18, 9)
        self.timer(january, 16)  # auto paid_leave will be applied
        self.timer(january.replace(day=19), 18)  # overtime generated
        self.assertEqual(
            self.sheet(january),
            [
                [18, 19, "T"],  # days
                [7.0, 9.0, 16.0],  # work
                [0.0, 0.0, 0.0],  # vacation
                [0.0, 0.0, 0.0],  # sick
                [1.0, 0.0, 1.0],  # paid leave
                [0.0, 0.0, 0.0],  # unpaid leave
                [8.0, 8.0, 16.0],  # compensation
                [0.0, 1.0, 1.0],  # overtime
                # transferred, net, balance overtime
                [0.0, 0.0, 0.0],
                # transferred, added, balance vacation
                [0.0, 20.0, 20.0],
            ],
        )

    def test_unpaid_leave(self):
        january = datetime(2017, 1, 18, 9)
        self.timer(january, 16)
        self.timer(january.replace(hour=16), 17, Timer.UNPAID_LEAVE)
        # unpaid_leave prevents automatic overtime and paid_leave
        self.assertEqual(
            self.sheet(january),
            [
                [18, "T"],  # days
                [7.0, 7.0],  # work
                [0.0, 0.0],  # vacation
                [0.0, 0.0],  # sick
                [0.0, 0.0],  # paid leave
                [1.0, 1.0],  # unpaid leave
                [7.0, 7.0],  # compensation
                [0.0, 0.0],  # overtime
                # transferred, net, balance overtime
                [0.0, 0.0, 0.0],
                # transferred, added, balance vacation
                [0.0, 20.0, 20.0],
            ],
        )

    def test_long_day(self):
        january = datetime(2017, 1, 18, 9)
        self.timer(january, 11)  # 2hr of work
        self.timer(january.replace(hour=11), 13, Timer.VACATION)  # quick 2hr vacation
        self.timer(january.replace(hour=13), 15, Timer.SICK)  # sick for 2hr
        self.timer(
            january.replace(hour=15), 16, Timer.UNPAID_LEAVE
        )  # 1hr of unpaid leave
        # should get 1hr automatic paid_leave
        self.assertEqual(
            self.sheet(january),
            [
                [18, "T"],  # days
                [2.0, 2.0],  # work
                [2.0, 2.0],  # vacation
                [2.0, 2.0],  # sick
                [1.0, 1.0],  # paid leave
                [1.0, 1.0],  # unpaid leave
                [7.0, 7.0],  # compensation
                [0.0, 0.0],  # overtime
                # transferred, net, balance overtime
                [0.0, -1.0, -1.0],
                # transferred, added, balance vacation
                [0.0, 20.0, 18.0],
            ],
        )

    def test_vacation_with_paid_leave(self):
        january = datetime(2017, 1, 18, 9)
        self.timer(january, 17, Timer.VACATION)
        self.timer(january.replace(day=19), 13, Timer.VACATION)
        # second day of vacation is half-day, worker gets paid_leave for it
        self.assertEqual(
            self.sheet(january),
            [
                [18, 19, "T"],  # days
                [0.0, 0.0, 0.0],  # work
                [8.0, 4.0, 12.0],  # vacation
                [0.0, 0.0, 0.0],  # sick
                [0.0, 4.0, 4.0],  # paid leave
                [0.0, 0.0, 0.0],  # unpaid leave
                [8.0, 8.0, 16.0],  # compensation
                [0.0, 0.0, 0.0],  # overtime
                # transferred, net, balance overtime
                [0.0, -4.0, -4.0],
                # transferred, added, balance vacation
                [0.0, 20.0, 8.0],
            ],
        )

    def test_previous_vacation_and_overtime_transfer(self):
        january = datetime(2017, 1, 18, 9)
        self.timer(january, 18)
        self.timer(january.replace(day=19), 17, Timer.VACATION)
        Timesheet(
            document_date=january, worker=self.worker, letterhead=self.letterhead
        ).calculate().save()

        february = datetime(2017, 2, 6, 9)
        self.timer(february, 18)
        self.assertEqual(
            self.sheet(february),
            [
                [6, "T"],  # days
                [9.0, 9.0],  # work
                [0.0, 0.0],  # vacation
                [0.0, 0.0],  # sick
                [0.0, 0.0],  # paid leave
                [0.0, 0.0],  # unpaid leave
                [8.0, 8.0],  # compensation
                [1.0, 1.0],  # overtime
                # transferred, net, balance overtime
                [1.0, 1.0, 2.0],
                # transferred, added, balance vacation
                [12.0, 20.0, 32.0],
            ],
        )
