from io import BytesIO
from datetime import date

from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer, KeepTogether

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from .style import NumberedSystoriDocument, stylesheets, force_break, p, b
from .style import NumberedLetterheadCanvas, NumberedCanvas
from .style import calculate_table_width_and_pagesize
from .style import heading_and_date, get_address_label, get_address_label_spacer

DEBUG_DOCUMENT = False  # Shows boxes in rendered output


def render(refund, letterhead, format):

    with BytesIO() as buffer:

        table_width, pagesize = calculate_table_width_and_pagesize(letterhead)

        refund_date = date_format(date(*map(int, refund['date'].split('-'))), use_l10n=True)

        doc = NumberedSystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

        flowables = [

            get_address_label(refund),

            get_address_label_spacer(refund),

            heading_and_date(refund.get('title') or _("Refund"), refund_date, table_width, debug=DEBUG_DOCUMENT),

            Spacer(0, 6*mm),

            Paragraph(force_break(refund['header']), stylesheets['OpenSans']['Normal']),

            Spacer(0, 4*mm),

            KeepTogether(Paragraph(force_break(refund['footer']), stylesheets['OpenSans']['Normal']))

        ]

        if format == 'print':
            doc.build(flowables, NumberedCanvas, letterhead)
        else:
            doc.build(flowables, NumberedLetterheadCanvas.factory(letterhead), letterhead)

        return buffer.getvalue()


def serialize(refund_obj, data):

    contact = refund_obj.project.billable_contact.contact

    refund = {

        'version': '1.0',

        'id': refund_obj.id,

        'title': data['title'],
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

        'amount': data['amount']

    }

    return refund
