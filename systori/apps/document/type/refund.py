from io import BytesIO
from datetime import date

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from .style import NumberedSystoriDocument
from .style import NumberedLetterheadCanvas, NumberedCanvas
from .style import calculate_table_width_and_pagesize
from .style import heading_and_date, get_address_label, get_address_label_spacer
from .font import FontManager


DEBUG_DOCUMENT = False  # Shows boxes in rendered output


def render(refund, letterhead, format):

    with BytesIO() as buffer:

        font = FontManager(letterhead.font)
        table_width, pagesize = calculate_table_width_and_pagesize(letterhead)
        document_date = date_format(date(*map(int, refund['date'].split('-'))), use_l10n=True)
        doc = NumberedSystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

        flowables = [

            get_address_label(refund, font),

            get_address_label_spacer(refund),

            heading_and_date(refund.get('title') or _("Refund"), document_date, font, table_width,
                             debug=DEBUG_DOCUMENT),

        ]
        if format == 'print':
            doc.build(flowables, NumberedCanvas, letterhead)
        else:
            doc.build(flowables, NumberedLetterheadCanvas.factory(letterhead), letterhead)

        return buffer.getvalue()


def serialize(refund_obj, data):

    contact = refund_obj.project.billable_contact.contact

    refund = {

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

        'jobs': data['jobs'],

        'paid_total': data['paid_total'],
        'invoiced_total': data['invoiced_total'],
        'progress_total': data['progress_total'],
        'refund_total': data['refund_total'],
        'credit_total': data['credit_total'],
        'customer_refund': data['customer_refund']

    }

    return refund
