from io import BytesIO
from datetime import date

from reportlab.lib.units import mm
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import Paragraph, Spacer, KeepTogether, PageBreak
from reportlab.lib import colors

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.lib.templatetags.customformatting import ubrdecimal, money

from .style import NumberedSystoriDocument, TableFormatter, ContinuationTable
from .style import chunk_text, force_break, p, b
from .style import NumberedLetterheadCanvas, NumberedCanvas
from .style import calculate_table_width_and_pagesize
from .style import heading_and_date, get_address_label, get_address_label_spacer
from .utils import update_instance
from .font import FontManager

from ...accounting.constants import TAX_RATE


DEBUG_DOCUMENT = False  # Shows boxes in rendered output


def collate_tasks(proposal, font, available_width):

    t = TableFormatter([1, 0, 1, 1, 1, 1], available_width, font, debug=DEBUG_DOCUMENT)
    t.style.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
    t.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    t.style.append(('VALIGN', (0, 0), (-1, -1), 'TOP'))
    t.style.append(('LINEABOVE', (0, 'splitfirst'), (-1, 'splitfirst'), 0.25, colors.black))

    t.row(_("Pos."), _("Description"), _("Amount"), '', _("Price"), _("Total"))
    t.row_style('FONTNAME', 0, -1, font.bold)
    t.row_style('ALIGNMENT', 2, 3, "CENTER")
    t.row_style('ALIGNMENT', 4, -1, "RIGHT")
    t.row_style('SPAN', 2, 3)

    description_width = sum(t.get_widths()[1:6])

    for job in proposal['jobs']:
        t.row(b(job['code'], font), b(job['name'], font))
        t.row_style('SPAN', 1, -1)

        for taskgroup in job['taskgroups']:
            t.row(b(taskgroup['code'], font), b(taskgroup['name'], font))
            t.row_style('SPAN', 1, -1)
            t.keep_next_n_rows_together(2)
            lines = simpleSplit(taskgroup['description'], font.normal.fontName, t.font_size, description_width)
            for line in lines:
                t.row('', p(line, font))
                t.row_style('SPAN', 1, -1)
                t.row_style('TOPPADDING', 0, -1, 1)
            t.row_style('BOTTOMPADDING', 0, -1, 10)

            for task in taskgroup['tasks']:
                t.row(p(task['code'], font), p(task['name'], font))
                t.row_style('SPAN', 1, -2)

                lines = simpleSplit(task['description'], font.normal.fontName, t.font_size, description_width)
                for line in lines:
                    t.row('', p(line, font))
                    t.row_style('SPAN', 1, -1)
                    t.row_style('TOPPADDING', 0, -1, 1)

                task_total_column = money(task['total'])
                if task['is_optional']:
                    task_total_column = _('Optional')
                elif not task['selected']:
                    task_total_column = _('Alternative')

                t.row('', '', ubrdecimal(task['qty']), p(task['unit'], font), money(task['price']), task_total_column)
                t.row_style('ALIGNMENT', 1, -1, "RIGHT")
                t.keep_previous_n_rows_together(3)

                t.row_style('BOTTOMPADDING', 0, -1, 10)

            t.row('', b('{} {} - {}'.format(_('Total'), taskgroup['code'], taskgroup['name']), font),
                  '', '', '', money(taskgroup['total']))
            t.row_style('FONTNAME', 0, -1, font.bold)
            t.row_style('ALIGNMENT', -1, -1, "RIGHT")
            t.row_style('SPAN', 1, 4)
            t.row_style('VALIGN', 0, -1, "BOTTOM")

            t.row('')

    return t.get_table(ContinuationTable, repeatRows=1)


def collate_tasks_total(proposal, font, available_width):

    t = TableFormatter([0, 1], available_width, font, debug=DEBUG_DOCUMENT)
    t.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
    t.style.append(('LEFTPADDING', (0, 0), (0, -1), 0))
    t.style.append(('FONTNAME', (0, 0), (-1, -1), font.bold.fontName))
    t.style.append(('ALIGNMENT', (0, 0), (-1, -1), "RIGHT"))

    for job in proposal['jobs']:
        for taskgroup in job['taskgroups']:
            t.row(b('{} {} - {}'.format(_('Total'), taskgroup['code'], taskgroup['name']), font),
                  money(taskgroup['total']))
    t.row_style('LINEBELOW', 0, 1, 0.25, colors.black)

    t.row(_("Total without VAT"), money(proposal['total_base']))
    t.row("19,00% "+_("VAT"), money(proposal['total_tax']))
    t.row(_("Total including VAT"), money(proposal['total_gross']))

    return t.get_table()


def collate_lineitems(proposal, available_width, font):

    pages = []

    for job in proposal['jobs']:

        for taskgroup in job['taskgroups']:

            for task in taskgroup['tasks']:

                pages.append(PageBreak())

                t = TableFormatter([1, 0], available_width, debug=DEBUG_DOCUMENT)
                t.style.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
                t.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
                t.style.append(('VALIGN', (0, 0), (-1, -1), 'TOP'))

                t.row(b(job['code']), b(job['name']))
                t.row(b(taskgroup['code']), b(taskgroup['name']))
                t.row(p(task['code']), p(task['name']))

                for chunk in chunk_text(task['description']):
                    t.row('', p(chunk))

                # t.row_style('BOTTOMPADDING', 0, -1, 10)  seems to have no effect @elmcrest 09/2015

                pages.append(t.get_table(ContinuationTable))

                t = TableFormatter([0, 1, 1, 1, 1], available_width, debug=DEBUG_DOCUMENT)
                t.style.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
                t.style.append(('RIGHTPADDING', (-1, 0), (-1, -1), 0))
                t.style.append(('VALIGN', (0, 0), (-1, -1), 'TOP'))
                t.style.append(('ALIGNMENT', (1, 0), (1, -1), 'RIGHT'))
                t.style.append(('ALIGNMENT', (3, 0), (-1, -1), 'RIGHT'))

                for lineitem in task['lineitems']:
                    t.row(p(lineitem['name']),
                          ubrdecimal(lineitem['qty']),
                          p(lineitem['unit']),
                          money(lineitem['price']),
                          money(lineitem['price_per'])
                          )

                t.row_style('LINEBELOW', 0, -1, 0.25, colors.black)

                t.row('', ubrdecimal(task['qty']), b(task['unit']), '', money(task['total']))
                t.row_style('FONTNAME', 0, -1, font.bold)

                pages.append(t.get_table(ContinuationTable))

    return pages


def render(proposal, letterhead, with_line_items, format):

    with BytesIO() as buffer:

        font = FontManager(letterhead.font)

        table_width, pagesize = calculate_table_width_and_pagesize(letterhead)

        proposal_date = date_format(date(*map(int, proposal['date'].split('-'))), use_l10n=True)

        doc = NumberedSystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

        flowables = [

            get_address_label(proposal, font),

            get_address_label_spacer(proposal),

            heading_and_date(proposal.get('title') or _("Proposal"), proposal_date, font,
                             table_width, debug=DEBUG_DOCUMENT),

            Spacer(0, 4*mm),

            Paragraph(force_break(proposal['header']), font.normal),

            Spacer(0, 4*mm),

            collate_tasks(proposal, font, table_width),

            collate_tasks_total(proposal, font, table_width),

            Spacer(0, 10*mm),

            KeepTogether(Paragraph(force_break(proposal['footer']), font.normal)),

            ] + (collate_lineitems(proposal, table_width, font) if with_line_items else [])

        if format == 'print':
            doc.build(flowables, NumberedCanvas, letterhead)
        else:
            doc.build(flowables, NumberedLetterheadCanvas.factory(letterhead), letterhead)

        return buffer.getvalue()


def serialize(project, data):

    contact = project.billable_contact.contact

    proposal = {

        'version': '1.1',

        'date': data['document_date'],

        'header': data['header'],
        'footer': data['footer'],

        'business': contact.business,
        'salutation': contact.salutation,
        'first_name': contact.first_name,
        'last_name': contact.last_name,
        'address': contact.address,
        'postal_code': contact.postal_code,
        'city': contact.city,
        'address_label': contact.address_label,

        'total_gross': data['amount'] * (TAX_RATE+1),
        'total_base': data['amount'],
        'total_tax': data['amount'] * TAX_RATE,

    }

    if data['add_terms']:
        proposal['add_terms'] = True  # TODO: Calculate the terms.

    proposal['jobs'] = []

    for job in data['jobs']:
        job_dict = {
            'id': job.id,
            'code': job.code,
            'name': job.name,
            'taskgroups': []
        }
        proposal['jobs'].append(job_dict)

        for taskgroup in job.taskgroups.all():
            taskgroup_dict = {
                'id': taskgroup.id,
                'code': taskgroup.code,
                'name': taskgroup.name,
                'description': taskgroup.description,
                'total': taskgroup.estimate_total,
                'tasks': []
            }
            job_dict['taskgroups'].append(taskgroup_dict)

            for task in taskgroup.tasks.all():

                for instance in task.taskinstances.all():

                    task_dict = {
                        'id': task.id,
                        'code': instance.code,
                        'name': instance.full_name,
                        'description': instance.full_description,
                        'selected': instance.selected,
                        'is_optional': task.is_optional,
                        'qty': task.qty,
                        'unit': task.unit,
                        'price': instance.unit_price,
                        'total': instance.fixed_price_estimate,
                        'lineitems': []
                    }
                    taskgroup_dict['tasks'].append(task_dict)

                    for lineitem in task.instance.lineitems.all():
                        lineitem_dict = {
                            'id': lineitem.id,
                            'name': lineitem.name,
                            'qty': lineitem.unit_qty,
                            'unit': lineitem.unit,
                            'price': lineitem.price,
                            'price_per': lineitem.price_per_task_unit,
                        }
                        task_dict['lineitems'].append(lineitem_dict)

    return proposal


def update(instance, data):
    return update_instance(instance, data, {'document_date': 'date'})
