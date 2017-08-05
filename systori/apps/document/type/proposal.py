import os
from datetime import date
from itertools import chain

from django.conf import settings
from django.utils.formats import date_format
from django.utils.translation import ugettext as _
from django.template.loader import get_template, render_to_string

from bericht.pdf import PDFStreamer
from bericht.html import HTMLParser, CSS

from systori.lib.accounting.tools import Amount
from systori.lib.templatetags.customformatting import money, ubrdecimal


class ProposalRowIterator:

    def __init__(self, render):
        self.render = render

    def __iter__(self):
        for job in self.render.proposal['jobs']:
            yield from self.iterate_group(job, 0)

        for job in self.render.proposal['jobs']:
            for group in job.get('groups', []):
                yield self.render.subtotal_html, {
                    'offset': False,
                    'code': group['code'],
                    'name': group['name'],
                    'total': money(group['estimate'])
                }

    def iterate_group(self, group, depth):

        yield self.render.group_html, {
            'code': group['code'],
            'name': group['name'],
            'bold_name': depth <= 2,
            'description': group['description'],
            'show_description': depth <= 2 or not self.render.only_task_names,
        }

        if not self.render.only_groups:
            for task in group.get('tasks', []):
                task_context = self.get_task_context(task)
                yield self.render.group_html, task_context
                if task['qty'] is not None:
                    yield self.render.lineitem_html, {
                        'name': '',
                        'qty': ubrdecimal(task['qty']),
                        'unit': task['unit'],
                        'price': money(task['price']),
                        'total': task_context['total'],
                    }
                else:
                    for lineitem in task['lineitems']:
                        yield self.render.lineitem_html, {
                            'name': lineitem['name'],
                            'qty': ubrdecimal(lineitem['qty']),
                            'unit': lineitem['unit'],
                            'price': money(lineitem['price']),
                            'total': money(lineitem['estimate']),
                        }

        for subgroup in group.get('groups', []):
            yield from self.iterate_group(subgroup, depth+1)

        if not group.get('groups', []) and group.get('tasks', []):
            total = group['estimate']
            if isinstance(group['estimate'], Amount):
                total = group['estimate'].net
            yield self.render.subtotal_html, {
                'offset': True,
                'code': group['code'],
                'name': group['name'],
                'total': money(total)
            }

    def get_task_context(self, task):

        kwargs = {
            'code': task['code'],
            'name': task['name'],
            'bold_name': False,
            'total': money(task['estimate']),
            'description': task['description'],
            'show_description': not self.render.only_task_names,
        }

        if task['is_provisional']:
            kwargs['total'] = _('Optional')

        if task.get('variant_group'):
            if task['variant_serial'] == 0:
                kwargs['name'] = _('Variant {}.0: {}').format(task['variant_group'], task['name'])
            else:
                kwargs['name'] = _('Variant {}.{}: {} - Alternative for Variant {}.0').format(
                    task['variant_group'], task['variant_serial'], task['name'], task['variant_group']
                )
                kwargs['total'] = _('Alternative')

        return kwargs


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
        self.group_html = get_template('document/proposal/group.html')
        self.subtotal_html = get_template('document/proposal/subtotal.html')
        self.itemized_html = get_template('document/proposal/itemized.html')
        self.lineitem_html = get_template('document/proposal/lineitem.html')
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

        maximums = {
            'code': '',
            'qty': '',
            'unit': '',
            'price': '',
            'total': ''
        }

        rows = ProposalRowIterator(self)

        for template, context in rows:
            for key, value in maximums.items():
                context_value = context.get(key, '')
                if len(context_value) > len(value):
                    maximums[key] = context_value

        proposal = {
            'doc_date': date_format(date(*map(int, self.proposal['document_date'].split('-'))), use_l10n=True)
        }
        proposal.update({
            'longest_'+key: value for key, value in maximums.items()
        })
        proposal.update(self.proposal)

        yield self.header_html.render(proposal)

        for template, context in rows:
            yield template.render(context)

        yield self.footer_html.render(proposal)

        if self.with_lineitems:
            yield from self.render_lineitems(proposal)

    def render_lineitems(self, proposal):

        def add_task(job, task):
            yield self.itemized_html.render({
                'job': job,
                'task': task,
                'longest_amount': '1.000,00',
                'longest_unit': 'unit',
                'longest_price': '00.000,00',
                'longest_total': '000.000,00'
            })

        def traverse(job, parent):
            for group in parent.get('groups', []):
                yield from traverse(job, group)

            for task in parent['tasks']:
                yield from add_task(job, task)

        for job in proposal['jobs']:

            for group in job.get('groups', []):
                yield from traverse(job, group)

            for task in job.get('tasks', []):
                yield from add_task(job, task)


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
