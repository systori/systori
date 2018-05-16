import os
from itertools import chain

from django.conf import settings
from django.template.loader import get_template, render_to_string
from django.utils.translation import ugettext as _

from bericht.pdf import PDFStreamer
from bericht.html import HTMLParser, CSS

from systori.lib.accounting.tools import Amount
from systori.lib.templatetags.customformatting import money, ubrdecimal
from .base import BaseRowIterator, parse_date


class ProposalRowIterator(BaseRowIterator):

    def iterate_tasks(self, group):
        if not self.render.only_groups:
            yield from super().iterate_tasks(group)

    def get_group_context(self, group, depth, **kwargs):
        return super().get_group_context(
            group, depth, show_description=depth <= 2, **kwargs
        )

    def get_task_context(self, task, **kwargs):
        total = money(task['estimate'])
        if task['is_provisional']:
            total = _('Optional')
        elif task.get('variant_group') and task['variant_serial'] != 0:
            total = _('Alternative')
        return super().get_task_context(
            task, qty=ubrdecimal(task['qty']), total=total,
            show_description=not self.render.only_task_names,
            **kwargs
        )

    def get_lineitem_context(self, lineitem, **kwargs):
        return super().get_lineitem_context(
            lineitem, qty=ubrdecimal(lineitem['qty']), total=money(lineitem['estimate']), **kwargs
        )

    def get_subtotal_context(self, group, **kwargs):
        total = group['estimate']
        if isinstance(group['estimate'], Amount):
            total = group['estimate'].net
        return super().get_subtotal_context(
            group, total=money(total), **kwargs
        )


class ProposalRenderer:

    def __init__(self, proposal, letterhead, with_lineitems, only_groups,
                 only_task_names, technical_listing, format):
        self.proposal = proposal
        self.letterhead = letterhead
        self.with_lineitems = with_lineitems
        self.only_groups = only_groups
        self.only_task_names = only_task_names
        self.technical_listing = technical_listing
        self.format = format

        # cache template lookups
        if not self.technical_listing:
            self.header_html = get_template('document/proposal/header.html')
            self.group_html = get_template('document/base/group.html')
            self.lineitem_html = get_template('document/base/lineitem.html')
            self.subtotal_html = get_template('document/base/subtotal.html')
            self.itemized_html = get_template('document/proposal/itemized.html')
            self.footer_html = get_template('document/proposal/footer.html')
        else:
            self.header_html = get_template('document/technical_listing/header.html')
            # ToDo: Check if there's a better way than loading an empty template
            self.group_html = get_template('document/technical_listing/group.html')
            self.lineitem_html = get_template('document/technical_listing/lineitem.html')
            self.subtotal_html = get_template('document/technical_listing/subtotal.html')
            self.itemized_html = get_template('document/technical_listing/itemized.html')
            self.footer_html = get_template('document/technical_listing/footer.html')

    @property
    def pdf(self):
        return PDFStreamer(
            HTMLParser(self.generate, CSS(''.join(self.css))),
            os.path.join(
                settings.MEDIA_ROOT,
                self.letterhead.letterhead_pdf.name
            ) if self.format == 'email' else None
        )

    @property
    def html(self):
        return ''.join(chain(
            ('<style>',),
            self.css,
            ('</style>',),
            self.generate()
        ))

    @property
    def css(self):
        context = {
            'letterhead': self.letterhead,
            'format': self.format,
        }
        if not self.technical_listing:
            yield render_to_string('document/base/base.css', context)
            yield render_to_string('document/proposal/proposal.css', context)
        else:
            yield render_to_string('document/technical_listing/style.css', context)

    def generate(self):

        proposal = {
            'doc_date': parse_date(self.proposal['document_date'])
        }
        proposal.update(self.proposal)

        yield self.header_html.render(proposal)

        for template, context in ProposalRowIterator(self, self.proposal):
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
