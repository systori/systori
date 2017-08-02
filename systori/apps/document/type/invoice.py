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
from systori.apps.accounting.models import Entry
from systori.apps.accounting.report import create_invoice_report, create_invoice_table


class InvoiceRenderer:

    def __init__(self, invoice, letterhead, payment_details, format):
        self.invoice = invoice
        self.letterhead = letterhead
        self.payment_details = payment_details
        self.group_subtotals_added = False
        self.format = format

        # cache template lookups
        self.header_html = get_template('document/invoice/header.html')
        self.group_html = get_template('document/invoice/group.html')
        self.task_html = get_template('document/invoice/task.html')
        self.debit_html = get_template('document/invoice/debit.html')
        self.subtotal_html = get_template('document/invoice/subtotal.html')
        self.footer_html = get_template('document/invoice/footer.html')

    @property
    def pdf(self):
        return PDFStreamer(
            HTMLParser(self.generate(), CSS(self.css)),
            os.path.join(settings.MEDIA_ROOT, self.letterhead.letterhead_pdf.name)
        )

    @property
    def html(self):
        return ''.join(chain(
            ('<style>', self.css, '</style>'),
            self.generate()
        ))

    @property
    def css(self):
        return render_to_string('document/invoice/invoice.css', {
            'letterhead': self.letterhead
        })

    def generate(self):
        invoice = self.invoice

        def get_date(str_date):
            return date_format(date(*map(int, str_date.split('-'))), use_l10n=True) if str_date else None

        context = {
            'invoice_date': get_date(invoice['document_date']),
            'vesting_start':  get_date(invoice['vesting_start']),
            'vesting_end':  get_date(invoice['vesting_end']),

            'longest_net': '$999,999.99',
            'longest_tax': '$999,999.99',
            'longest_gross': '$999,999.99',
            'payments': self.get_payments(),

            'longest_code': '01.01.01.01',
            'longest_amount': '1.000,00',
            'longest_unit': 'unit',
            'longest_price': '00.000,00',
            'longest_total': '000.000,00',

            'invoice': invoice,
        }

        yield self.header_html.render(context)

        for job in invoice['jobs']:

            if job['invoiced'].net == job['progress'].net:
                yield from self.render_group(job, 0)

            else:
                yield self.group_html.render({
                    'bold_name': True,
                    'code': job['code'],
                    'name': job['name'],
                    'description': job['description']
                })
                debits = invoice['job_debits'].get(str(job['job.id']), [])
                for debit in debits:
                    entry_date = date_format(date(*map(int, debit['date'].split('-'))), use_l10n=True)
                    if debit['entry_type'] == Entry.WORK_DEBIT:
                        title = _('Work completed on {date}').format(date=entry_date)
                    elif debit['entry_type'] == Entry.FLAT_DEBIT:
                        title = _('Flat invoice on {date}').format(date=entry_date)
                    else:  # adjustment, etc
                        title = _('Adjustment on {date}').format(date=entry_date)
                    yield self.debit_html.render({
                        'title': title,
                        'amount': debit['amount']
                    })

        for job in invoice['jobs']:
            if job['invoiced'].net == job['progress'].net:
                for group in job.get('groups', []):
                    yield self.subtotal_html.render(group)
            else:
                yield self.subtotal_html.render({
                    'code': job['code'],
                    'name': job['name'],
                    'progress': job['invoiced'].net
                })

        yield self.footer_html.render(context)

    def get_payments(self):

        table = create_invoice_table(self.invoice)[1:]
        for idx, row in enumerate(table):
            txn = row[4]

            if row[0] == 'progress':
                title = _('Project progress')
            elif row[0] == 'payment':
                pay_day = date_format(date(*map(int, txn['date'].split('-'))), use_l10n=True)
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

    def render_group(self, group, depth):

        kwargs = {
            'bold_name': depth <= 2,
        }
        kwargs.update(group)

        yield self.group_html.render(kwargs)

        for task in group.get('tasks', []):
            yield self.task_html.render({'task': task})

        for subgroup in group.get('groups', []):
            yield from self.render_group(subgroup, depth+1)

        if not group.get('groups', []) and group.get('tasks', []):
            total_kwargs = {'offset': True}
            total_kwargs.update(group)
            yield self.subtotal_html.render(total_kwargs)
            self.group_subtotals_added = True


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
