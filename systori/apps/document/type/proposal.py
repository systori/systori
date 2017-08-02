import os
from datetime import date
from itertools import chain

from django.conf import settings
from django.utils.formats import date_format
from django.utils.translation import ugettext as _
from django.template.loader import get_template, render_to_string

from bericht.pdf import PDFStreamer
from bericht.html import HTMLParser, CSS

from systori.lib.templatetags.customformatting import money


class ProposalRenderer:

    def __init__(self, proposal, letterhead, with_lineitems, only_groups, only_task_names, format):
        self.proposal = proposal
        self.letterhead = letterhead
        self.with_lineitems = with_lineitems
        self.only_groups = only_groups
        self.only_task_names = only_task_names
        self.format = format

        # cache template lookups
        self.header_html = get_template('document/proposal/header.html')
        self.task_html = get_template('document/proposal/task.html')
        self.group_html = get_template('document/proposal/group.html')
        self.subtotal_html = get_template('document/proposal/subtotal.html')
        self.footer_html = get_template('document/proposal/footer.html')

    @property
    def pdf(self):
        return PDFStreamer(
            HTMLParser(self.generate(), CSS(self.css)),
            os.path.join(
                settings.MEDIA_ROOT,
                self.letterhead.letterhead_pdf.name
            ) if self.format == 'email' else None
        )

    @property
    def html(self):
        return ''.join(chain(
            ('<style>', self.css, '</style>'),
            self.generate()
        ))

    @property
    def css(self):
        return render_to_string('document/proposal/proposal.css', {
            'letterhead': self.letterhead,
            'format': self.format,
        })

    def generate(self):
        proposal = self.proposal

        proposal_date = date_format(date(*map(int, proposal['document_date'].split('-'))), use_l10n=True)

        proposal['doc_date'] = proposal_date
        proposal['longest_code'] = '01.01.01.01'
        proposal['longest_amount'] = '1.000,00'
        proposal['longest_unit'] = 'unit'
        proposal['longest_price'] = '00.000,00'
        proposal['longest_total'] = '000.000,00'

        yield self.header_html.render(proposal)

        for job in proposal['jobs']:
            yield from self.render_group(job, 0)

        for job in proposal['jobs']:
            for group in job.get('groups', []):
                yield self.subtotal_html.render(group)

        yield self.footer_html.render(proposal)

    def render_group(self, group, depth):

        kwargs = {
            'bold_name': depth <= 2,
            'show_description': depth <= 2 or not self.only_task_names,
        }
        kwargs.update(group)

        yield self.group_html.render(kwargs)

        if not self.only_groups:
            for task in group.get('tasks', []):
                yield self.render_task(task)

        for subgroup in group.get('groups', []):
            yield from self.render_group(subgroup, depth+1)

        if not group.get('groups', []) and group.get('tasks', []):
            total_kwargs = {'offset': True}
            total_kwargs.update(group)
            yield self.subtotal_html.render(total_kwargs)

    def render_task(self, task):

        kwargs = {
            'task_name': task['name'],
            'task_total': money(task['estimate']),
            'show_description': not self.only_task_names,
        }
        kwargs.update(task)

        if task['is_provisional']:
            kwargs['task_total'] = _('Optional')

        if task.get('variant_group'):
            if task['variant_serial'] == 0:
                kwargs['task_name'] = _('Variant {}.0: {}').format(task['variant_group'], kwargs['task_name'])
            else:
                kwargs['task_name'] = _('Variant {}.{}: {} - Alternative for Variant {}.0').format(
                    task['variant_group'], task['variant_serial'], kwargs['task_name'], task['variant_group'])
                kwargs['task_total'] = _('Alternative')

        return self.task_html.render(kwargs)


def serialize(proposal):

    if proposal.json['add_terms']:
        pass  # TODO: Calculate the terms.

    for job_data in proposal.json['jobs']:
        job_obj = job_data.pop('job')
        job_data['groups'] = []
        job_data['tasks'] = []
        _serialize(job_data, job_obj)


def _serialize(data, parent):

    for group in parent.groups.all():
        group_dict = {
            'group.id': group.id,
            'code': group.code,
            'name': group.name,
            'description': group.description,
            'estimate': group.estimate,
            'tasks': [],
            'groups': []
        }
        data['groups'].append(group_dict)
        _serialize(group_dict, group)

    for task in parent.tasks.all():

        task_dict = {
            'task.id': task.id,
            'code': task.code,
            'name': task.name,
            'description': task.description,
            'is_provisional': task.is_provisional,
            'variant_group': task.variant_group,
            'variant_serial': task.variant_serial,
            'qty': task.qty,
            'unit': task.unit,
            'price': task.price,
            'estimate': task.total,
            'lineitems': []
        }
        data['tasks'].append(task_dict)

        for lineitem in task.lineitems.all():
            lineitem_dict = {
                'lineitem.id': lineitem.id,
                'name': lineitem.name,
                'qty': lineitem.qty,
                'unit': lineitem.unit,
                'price': lineitem.price,
                'estimate': lineitem.total,
            }
            task_dict['lineitems'].append(lineitem_dict)
