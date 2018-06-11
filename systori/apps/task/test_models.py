import datetime
from django.test import TestCase
from django.utils.translation import activate
from django.contrib.postgres.search import SearchRank, SearchQuery

from ..project.models import Project
from ..project.factories import ProjectFactory
from ..company.factories import CompanyFactory
from ..document.factories import ProposalFactory, LetterheadFactory

from .factories import JobFactory, GroupFactory, TaskFactory, LineItemFactory
from .models import Job, Group, Task


class CalculationTests(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.project = ProjectFactory()
        self.job = JobFactory(project=self.project)
        self.group = GroupFactory(parent=self.job)

    def check_totals(self, estimate=0, progress=0, is_billable=False, num_queries=10):

        with self.assertNumQueries(num_queries):
            job = Job.objects.get(id=self.job.id)
            self.assertEqual(job.estimate, estimate)
            self.assertEqual(job.progress, progress)
            self.assertEqual(job.is_billable, is_billable)

        with self.assertNumQueries(1):
            job = Job.objects.with_is_billable().get(id=self.job.id)
            self.assertEqual(job.is_billable, is_billable)

        with self.assertNumQueries(1):
            job = Job.objects.with_totals().get(id=self.job.id)
            self.assertEqual(job.estimate, estimate)
            self.assertEqual(job.progress, progress)

        with self.assertNumQueries(1):
            project = Project.objects.with_totals().get(id=self.project.id)
            self.assertEqual(project.estimate, estimate)
            self.assertEqual(project.progress, progress)

    def test_task_zero(self):
        task = TaskFactory(group=self.group)
        self.assertEqual(task.total, 0)
        self.assertEqual(task.progress, 0)
        self.assertEqual(self.group.estimate, 0)
        self.assertEqual(self.group.progress, 0)
        self.check_totals()

    def test_task_with_progress(self):
        task = TaskFactory(group=self.group, qty=5, complete=3, price=8)
        self.assertTrue(task.is_billable)
        self.assertEqual(task.progress, 24)
        self.assertEqual(task.complete_percent, 60)
        self.check_totals(0, 24, True)

    def test_blank_task_price_difference(self):
        """ To prevent regression, used to throw:
            TypeError: unsupported operand type(s) for -: 'float' and 'decimal.Decimal'
        """
        task = Task(group=self.group)  # type: Task
        self.assertEqual(task.price_difference, 0)

    def test_task_price_difference(self):
        task = TaskFactory(group=self.job, price=0)  # type: Task
        LineItemFactory(task=task, total=10)
        self.assertTrue(task.price_difference, 2)

    def test_task_estimate_determination(self):
        task = TaskFactory(group=self.group, total=99)
        self.assertEqual(task.include_estimate, True)
        self.check_totals(99)

    def test_task_estimate_determination_is_provisional(self):
        task = TaskFactory(group=self.group, is_provisional=True, total=99)
        self.assertEqual(task.include_estimate, False)
        self.check_totals(0)

    def test_task_estimate_determination_variants(self):
        task = TaskFactory(group=self.group, variant_group=1, total=99)
        self.assertEqual(task.include_estimate, True)
        self.check_totals(99)
        task.variant_serial = 1
        task.save()
        self.assertEqual(task.include_estimate, False)
        self.check_totals(0)

    def test_task_progress_unaffected_by_task_states(self):
        """ Progress from completion is always counted regardless of is_provisional or variant serial."""
        task = TaskFactory(group=self.job, complete=2, price=10)
        self.assertEqual(task.progress, 20)
        self.check_totals(0, 20, True)

        task.is_provisional = True
        task.save()
        self.assertEqual(task.progress, 20)
        self.check_totals(0, 20, True)

        task.variant_group = 1
        task.variant_serial = 1
        task.save()
        self.assertEqual(task.progress, 20)
        self.check_totals(0, 20, True)

    def test_complete_percent(self):
        # Division by zero
        self.assertEqual(
            TaskFactory(group=self.job, complete=10, qty=0).complete_percent, 0
        )
        # Complete greater than qty
        self.assertEqual(
            TaskFactory(group=self.job, complete=10, qty=5).complete_percent, 200
        )
        # 100% rounding
        self.assertEqual(
            TaskFactory(group=self.job, complete=99.99, qty=100).complete_percent, 100
        )
        self.assertEqual(
            TaskFactory(group=self.job, complete=100.01, qty=100).complete_percent, 100
        )

    def test_group_with_tasks(self):
        TaskFactory(group=self.group, total=7)
        TaskFactory(group=self.group, total=8)
        self.check_totals(15)

    def test_multiple_subgroups(self):
        TaskFactory(group=self.group, total=7)
        group = GroupFactory(parent=self.job)
        TaskFactory(group=group, total=8)
        self.assertEqual(7, self.group.estimate)
        self.assertEqual(8, group.estimate)
        job = Job.objects.with_totals().get(pk=self.job)
        self.assertEqual(15, job.estimate)


class TestJobTransitions(TestCase):
    def setUp(self):
        activate("en")
        self.company = CompanyFactory()
        self.project = ProjectFactory()
        self.job = JobFactory(project=self.project)
        self.letterhead = LetterheadFactory()

    def test_job_draft(self):
        self.assertEquals("Draft", self.job.get_status_display())

    def test_job_proposed(self):
        proposal = ProposalFactory(project=self.project, letterhead=self.letterhead)
        proposal.jobs.add(self.job)
        self.job.refresh_from_db()
        self.assertEquals("Proposed", self.job.get_status_display())

    def test_job_approved(self):
        proposal = ProposalFactory(project=self.project, letterhead=self.letterhead)
        proposal.jobs.add(self.job)
        proposal.send()
        proposal.approve()
        self.job.refresh_from_db()
        self.assertEquals("Approved", self.job.get_status_display())

    def test_job_declined(self):
        proposal = ProposalFactory(project=self.project, letterhead=self.letterhead)
        proposal.jobs.add(self.job)
        self.job.refresh_from_db()
        self.assertEquals("Proposed", self.job.get_status_display())
        proposal.send()
        proposal.decline()
        self.job.refresh_from_db()
        self.assertEquals("Draft", self.job.get_status_display())

    def test_job_after_proposal_deleted(self):
        proposal = ProposalFactory(project=self.project, letterhead=self.letterhead)
        proposal.jobs.add(self.job)
        self.job.refresh_from_db()
        self.assertEquals("Proposed", self.job.get_status_display())
        proposal.delete()
        self.job.refresh_from_db()
        self.assertEquals("Draft", self.job.get_status_display())


class CodeFormattingTests(TestCase):
    def setUp(self):
        CompanyFactory()

    def test_job_code(self):
        project = ProjectFactory(structure="0.0")
        self.assertEqual(JobFactory(project=project).code, "1")
        self.assertEqual(JobFactory(project=project).code, "2")
        project = ProjectFactory(structure="000.0")
        self.assertEqual(JobFactory(project=project).code, "001")
        self.assertEqual(JobFactory(project=project).code, "002")

    def test_group_code(self):
        job = JobFactory(project=ProjectFactory(structure="0.000.00.0"))
        group = GroupFactory(parent=job)
        self.assertEqual(group.code, "1.001")
        self.assertEqual(GroupFactory(parent=group).code, "1.001.01")
        self.assertEqual(GroupFactory(parent=group).code, "1.001.02")
        group = GroupFactory(parent=job)
        self.assertEqual(GroupFactory(parent=group).code, "1.002.01")
        self.assertEqual(GroupFactory(parent=group).code, "1.002.02")

    def test_job_direct_tasks_code(self):
        """ Tasks are attached directly to the job. """
        job = JobFactory(project=ProjectFactory(structure="00.000"))
        task = TaskFactory(group=job)
        self.assertEqual(task.code, "01.001")

    def test_blank_group_task_code(self):
        """ One of the groups in the hierarchy is blank. """
        job = JobFactory(project=ProjectFactory(structure="00.00.000"))
        group = GroupFactory(name="", parent=job)
        task = TaskFactory(group=group)
        self.assertEqual(task.code, "01._.001")

    def test_complex_groups_task_code(self):
        """ A more comprehensive test case. """
        job = JobFactory(project=ProjectFactory(structure="0.00.00.0000"))
        group1 = GroupFactory(parent=job)
        GroupFactory(parent=group1)
        GroupFactory(parent=group1)
        group2 = GroupFactory(parent=group1)
        TaskFactory(group=group2)
        task = TaskFactory(group=group2)
        self.assertEqual(task.code, "1.01.03.0002")


class CloningTests(TestCase):
    def setUp(self):
        CompanyFactory()

    def test_clone(self):
        job = JobFactory(project=ProjectFactory())
        group = GroupFactory(name="my group", parent=job)
        group = GroupFactory(name="my subgroup", parent=group)
        task = TaskFactory(
            group=group,
            name="running task",
            qty=7,
            complete=7,
            status=Task.RUNNING,
            started_on=datetime.date.today(),
            completed_on=datetime.date.today(),
        )
        LineItemFactory(task=task)
        TaskFactory(group=group)
        TaskFactory(group=group)

        new_job = JobFactory(project=ProjectFactory())
        self.assertEqual(new_job.groups.count(), 0)
        self.assertEqual(new_job.all_groups.count(), 1)  # Job itself is a Group
        self.assertEqual(new_job.all_tasks.count(), 0)
        self.assertEqual(new_job.all_lineitems.count(), 0)

        job.clone_to(new_job)

        self.assertEqual(new_job.groups.count(), 1)
        self.assertEqual(new_job.all_groups.count(), 3)
        self.assertEqual(new_job.all_tasks.count(), 3)
        self.assertEqual(new_job.all_lineitems.count(), 1)

        new_group = new_job.groups.first().groups.first()
        self.assertEqual(new_group.tasks.count(), 3)
        self.assertEqual(group.name, new_group.name)
        self.assertNotEqual(group.pk, new_group.pk)

        new_task = new_group.tasks.first()
        self.assertEqual(new_task.name, "running task")
        self.assertEqual(new_task.complete, 0)
        self.assertEqual(new_task.status, "")
        self.assertIsNone(new_task.started_on)
        self.assertIsNone(new_task.completed_on)

        # TODO: Test what happens when heterogeneous structured objects
        #       are cloned, cloning should either truncate the larger
        #       structure or pad a smaller structure to make it fit.
        # TODO: Test that correction lineitems don't get copied.

    def test_clone_without_group(self):
        job = JobFactory(project=ProjectFactory(structure="01.01"))
        task = TaskFactory(
            group=job,
            name="running task",
            qty=7,
            complete=7,
            status=Task.RUNNING,
            started_on=datetime.date.today(),
            completed_on=datetime.date.today(),
        )
        LineItemFactory(task=task)

        new_job = JobFactory(project=ProjectFactory(structure="01.01"))
        self.assertEqual(new_job.tasks.count(), 0)

        job.clone_to(new_job)
        self.assertEqual(new_job.tasks.count(), 1)


class GroupTests(TestCase):
    def setUp(self):
        CompanyFactory()

    def test_factory_no_groups_to_generate_for_job(self):
        project = ProjectFactory(structure="0.0")
        job = JobFactory(project=project)
        self.assertEqual(job.all_groups.count(), 1)
        job = JobFactory(project=project, generate_groups=True)
        self.assertEqual(job.all_groups.count(), 1)

    def test_factory_two_subgroups_generated_from_job(self):
        project = ProjectFactory(structure="0.0.0.0")
        job = JobFactory(project=project)
        self.assertEqual(job.all_groups.count(), 1)
        job = JobFactory(project=project, generate_groups=True)
        self.assertEqual(job.all_groups.count(), 3)
        self.assertEqual(job.root.pk, 2)
        self.assertEqual(job.groups.first().pk, 3)
        self.assertEqual(job.groups.first().groups.first().pk, 4)

    def test_prefetching(self):
        project = ProjectFactory(structure="0.00.00.00.00.0000")
        job = JobFactory(project=project, generate_groups=True)  # type: Job
        leaf = job.groups.first().groups.first().groups.first().groups.first()
        LineItemFactory(name="first lineitem", task=TaskFactory(group=leaf))
        LineItemFactory(name="second lineitem", task=TaskFactory(group=leaf))
        LineItemFactory(name="third lineitem", task=TaskFactory(group=leaf))
        job.groups.first().clone_to(job, 2)
        job.groups.first().clone_to(job, 3)

        def traverse_children(group, depth=0):
            if depth == 4:
                for task in group.tasks.all():
                    for lineitem in task.lineitems.all():
                        return lineitem
                return

            result = None
            for subgroup in group.groups.all():
                result = traverse_children(subgroup, depth + 1)

            return result

        # no prefetch
        with self.assertNumQueries(17):
            self.assertIsNotNone(traverse_children(Job.objects.get(pk=job.pk)))

        # with prefetch
        with self.assertNumQueries(7):
            self.assertIsNotNone(
                traverse_children(Job.objects.with_hierarchy(project).get(pk=job.pk))
            )


class AutoCompleteSearchTest(TestCase):
    def setUp(self):

        CompanyFactory()

        en_names = ["one", "two", "three", "four"]
        de_names = ["eins", "zwei", "drei", "vier"]
        uk_names = ["один", "два", "три", "чотири"]
        ro_names = ["unu", "doi", "trei", "patru"]

        def add_names(group, names, depth=0):
            for subgroup in group.groups.all():
                subgroup.name = names[depth]
                subgroup.save()
                add_names(subgroup, names, depth + 1)

        project1 = ProjectFactory(structure="01.001", with_job=True)
        self.job = job = project1.jobs.first()
        [TaskFactory(total=i, name=en_names[i], group=job) for i in range(4)]
        [
            TaskFactory(
                total=i + 10, name=" ".join([en_names[i], de_names[i]]), group=job
            )
            for i in range(4)
        ]
        [
            TaskFactory(
                total=i + 20,
                name=" ".join([en_names[i], de_names[i], uk_names[i]]),
                group=job,
            )
            for i in range(4)
        ]

        project2 = ProjectFactory(structure="01.01.001", with_job=True)
        add_names(project2.jobs.first(), ro_names)
        project3 = ProjectFactory(structure="01.01.01.001", with_job=True)
        add_names(project3.jobs.first(), uk_names)
        project4 = ProjectFactory(structure="01.01.01.01.001", with_job=True)
        add_names(project4.jobs.first(), de_names)
        project5 = ProjectFactory(structure="01.01.01.01.01.001", with_job=True)
        add_names(project5.jobs.first(), en_names)

        long_text = "Voranstrich aus Bitumenlösung, Untergrund Beton, einschl. " "Aufkantungen, wie Attika, Schächte und Fundamente."
        TaskFactory(
            group=self.job, total=31, name="aus Bitumenlösung", description=long_text
        )
        TaskFactory(
            group=self.job, total=32, name="Schächte und", description=long_text
        )

    def test_available_groups(self):
        def available(depth):
            return list(
                Group.objects.groups_with_remaining_depth(depth).values_list(
                    "name", flat=True
                )
            )

        self.assertEqual(available(0), ["unu", "два", "drei", "four"])
        self.assertEqual(available(1), ["один", "zwei", "three"])
        self.assertEqual(available(2), ["eins", "two"])
        self.assertEqual(available(3), ["one"])

    def test_group_text_search(self):
        def search(depth, terms):
            return list(
                Group.objects.groups_with_remaining_depth(depth)
                .search(terms)
                .values_list("match_name", flat=True)
            )

        self.assertEqual(search(0, "unu"), ["<b>unu</b>"])
        self.assertEqual(search(0, "doi"), [])
        self.assertEqual(search(1, "один"), ["<b>один</b>"])
        self.assertEqual(search(1, "два"), [])
        self.assertEqual(search(2, "eins"), ["<b>eins</b>"])
        self.assertEqual(search(3, "one"), ["<b>one</b>"])
        self.assertEqual(search(3, "two"), [])

    def test_task_text_search(self):

        schacht = Task.objects.search("schacht").values_list("name", "match_name")
        self.assertEqual(schacht.count(), 2)
        self.assertEqual(
            list(schacht),
            [
                ("Schächte und", "<b>Schächte</b> und"),
                ("aus Bitumenlösung", "aus Bitumenlösung"),
            ],
        )

        bitumenlos = Task.objects.search("bitumenlos").values_list("name", "match_name")
        self.assertEqual(bitumenlos.count(), 2)
        self.assertEqual(
            list(bitumenlos),
            [
                ("aus Bitumenlösung", "aus <b>Bitumenlösung</b>"),
                ("Schächte und", "Schächte und"),
            ],
        )
