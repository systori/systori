import os
from itertools import chain

from django.conf import settings
from django.utils.translation import ugettext as _
from django.template.loader import get_template, render_to_string

from bericht.pdf import PDFStreamer
from bericht.html import HTMLParser, CSS

from systori.apps.accounting.models import Entry
from systori.apps.accounting.report import create_invoice_report, create_invoice_table

from systori.lib.accounting.tools import Amount
from systori.lib.templatetags.customformatting import money, ubrdecimal
from .base import BaseRowIterator, parse_date


class InvoiceRowIterator(BaseRowIterator):

    def iterate_job(self, job):

        if job['invoiced'].net == job['progress'].net:
            yield from super().iterate_job(job)

        else:

            yield self.render.group_html, {
                'code': job['code'],
                'name': job['name'],
                'bold_name': True,
                'description': job['description'],
                'show_description': True,
            }

            debits = self.document['job_debits'].get(str(job['job.id']), [])
            for debit in debits:
                entry_date = parse_date(debit['date'])
                if debit['entry_type'] == Entry.WORK_DEBIT:
                    title = _('Work completed on {date}').format(date=entry_date)
                elif debit['entry_type'] == Entry.FLAT_DEBIT:
                    title = _('Flat invoice on {date}').format(date=entry_date)
                else:  # adjustment, etc
                    title = _('Adjustment on {date}').format(date=entry_date)
                yield self.render.debit_html, {
                    'title': title,
                    'total': money(debit['amount'].net)
                }

    def subtotal_job(self, job):
        if job['invoiced'].net == job['progress'].net:
            yield from super().subtotal_job(job)
        else:
            yield self.render.subtotal_html,\
                  self.get_subtotal_context(job, total=money(job['invoiced'].net), offset=False)

    def get_group_context(self, group, depth, **kwargs):
        return super().get_group_context(
            group, depth,
            show_description=depth <= 2,
            **kwargs
        )

    def get_task_context(self, task, **kwargs):
        return super().get_task_context(
            task,
            qty=ubrdecimal(task['complete']),
            total=money(task['progress']),
            show_description=False,
            **kwargs
        )

    def get_lineitem_context(self, lineitem, **kwargs):
        return super().get_lineitem_context(
            lineitem,
            qty=ubrdecimal(lineitem['qty']),
            total=money(lineitem['estimate']),
            **kwargs
        )

    def get_subtotal_context(self, group, **kwargs):
        if 'total' not in kwargs:
            kwargs['total'] = money(group['progress'])
        return super().get_subtotal_context(group, **kwargs)


class InvoiceRenderer:

    def __init__(self, invoice, letterhead, payment_details, format):
        self.invoice = invoice
        self.letterhead = letterhead
        self.payment_details = payment_details
        self.group_subtotals_added = False
        self.format = format

        # cache template lookups
        self.header_html = get_template('document/invoice/header.html')
        self.group_html = get_template('document/base/group.html')
        self.lineitem_html = get_template('document/base/lineitem.html')
        self.debit_html = get_template('document/invoice/debit.html')
        self.subtotal_html = get_template('document/base/subtotal.html')
        self.footer_html = get_template('document/invoice/footer.html')

    @property
    def pdf(self):
        return PDFStreamer(
            HTMLParser(self.generate(), CSS(''.join(self.css))),
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
        yield render_to_string('document/base/base.css', context)
        yield render_to_string('document/invoice/invoice.css', context)

    def generate(self):

        maximums = {
            'code': '',
            'qty': '',
            'unit': '',
            'price': '',
            'total': ''
        }

        rows = InvoiceRowIterator(self, self.invoice)

        for template, context in rows:
            for key, value in maximums.items():
                context_value = context.get(key, '')
                if len(context_value) > len(value):
                    maximums[key] = context_value

        invoice = self.invoice

        context = {
            'invoice_date': parse_date(invoice['document_date']),
            'vesting_start':  parse_date(invoice['vesting_start']),
            'vesting_end':  parse_date(invoice['vesting_end']),

            'longest_net': 'consideration',
            'longest_tax': '$999,999.99',
            'longest_gross': '$999,999.99',
            'payments': self.get_payments(),

            'invoice': invoice,
        }

        context.update({
            'longest_'+key: value for key, value in maximums.items()
        })

        yield self.header_html.render(context)

        for template, row_context in rows:
            yield template.render(row_context)

        yield self.footer_html.render(context)

    def get_payments(self):

        table = create_invoice_table(self.invoice)[1:]
        for idx, row in enumerate(table):
            txn = row[4]

            if row[0] == 'progress':
                title = _('Project progress')
            elif row[0] == 'payment':
                pay_day = parse_date(txn['date'])
                title = _('Payment on {date}').format(date=pay_day)
            elif row[0] == 'discount':
                title = _('Discount applied')
            elif row[0] == 'unpaid':
                title = _('Open claim from prior invoices')
            elif row[0] == 'debit':
                title = _('This Invoice')
            else:
                raise NotImplementedError()

            yield 'normal', title, money(row[1]), money(row[2]), money(row[3])

            if self.payment_details and row[0] == 'payment':
                for job in txn['jobs'].values():
                    yield 'small', job['name'], money(job['payment_applied_net']), money(job['payment_applied_tax']), money(job['payment_applied_gross'])

            if self.payment_details and row[0] == 'discount':
                for job in txn['jobs'].values():
                    yield 'small', job['name'], money(job['discount_applied_net']), money(job['discount_applied_tax']), money(job['discount_applied_gross'])


def serialize(invoice):

    if invoice.json['add_terms']:
        pass  # TODO: Calculate the terms.

    job_objs = []
    for job_data in invoice.json['jobs']:
        job_obj = job_data.pop('job')
        job_objs.append(job_obj)
        job_data['groups'] = []
        job_data['tasks'] = []
        _serialize(job_data, job_obj)

    invoice.json.update(create_invoice_report(invoice.transaction, job_objs))


def _serialize(data, parent):

    for group in parent.groups.all():
        group_dict = {
            'group.id': group.id,
            'code': group.code,
            'name': group.name,
            'description': group.description,
            'tasks': [],
            'groups': [],
            'progress': group.progress,
            'estimate': group.estimate
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
            'complete': task.complete,
            'unit': task.unit,
            'price': task.price,
            'progress': task.progress,
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
