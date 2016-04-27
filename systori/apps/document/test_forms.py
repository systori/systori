from ..accounting.test_workflow import A
from ..accounting.test_forms import TestForm
from .forms import ProposalForm, ProposalFormSet
from .models import Proposal


class ProposalFormTests(TestForm):
    model = Proposal
    form = ProposalForm
    form_set = ProposalFormSet

    def test_simple_valid(self):
        form = self.make_form({
            'document_date': '2015-01-01',
            'title': 'Proposal #1',
            'header': 'hi',
            'footer': 'bye',
            'job-0-job_id': self.job.id,
            'job-0-is_attached': 'False',
            'job-1-job_id': self.job2.id,
            'job-1-is_attached': 'True',
        })
        self.assert_all_forms_valid(form)
        self.assertEqual(1, len(form.formset.get_json_rows()))

        form.save()

        self.assertEqual(1, len(form.instance.jobs.all()))
        self.assertEqual(1, len(form.instance.json['jobs']))
        self.assertEqual('hi', form.instance.json['header'])
        self.assertEqual('bye', form.instance.json['footer'])

    def test_no_jobs_selected(self):
        form = self.make_form({
            'title': 'Proposal #1',
            'header': 'header',
            'footer': 'footer',
            'job-0-job_id': self.job.id,
            'job-0-is_attached': 'False',
            'job-1-job_id': self.job2.id,
            'job-1-is_attached': 'False',
        })
        self.assertFalse(form.formset.is_valid())
        self.assertIn('At least one job must be selected.',
                      form.formset.non_form_errors())

    def test_corrupted_form_job_list(self):
        # change order of the jobs
        form = self.make_form({
            'title': 'Proposal #1',
            'header': 'header',
            'footer': 'footer',
            'job-0-job_id': self.job2.id,
            'job-0-is_attached': 'False',
            'job-1-job_id': self.job.id,
            'job-1-is_attached': 'False',
        })
        self.assertFalse(form.formset.is_valid())
        self.assertIn('Form has become invalid due to external changes to the jobs list.',
                      form.formset.non_form_errors())
