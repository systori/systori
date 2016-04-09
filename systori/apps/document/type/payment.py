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


def render(payment, letterhead, format):

    with BytesIO() as buffer:

        font = FontManager(letterhead.font)
        table_width, pagesize = calculate_table_width_and_pagesize(letterhead)
        document_date = date_format(date(*map(int, payment['date'].split('-'))), use_l10n=True)
        doc = NumberedSystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

        flowables = [

            heading_and_date(payment.get('title') or _("Payment"), document_date, font, table_width,
                             debug=DEBUG_DOCUMENT),

        ]
        if format == 'print':
            doc.build(flowables, NumberedCanvas, letterhead)
        else:
            doc.build(flowables, NumberedLetterheadCanvas.factory(letterhead), letterhead)

        return buffer.getvalue()


def serialize(payment_obj, data):

    payment = {
        'bank_account': data['bank_account'].id,
        'date': data['document_date'],
        'payment': data['payment'],
        'discount': data['discount'],
        'split_total': data['split_total'],
        'discount_total': data['discount_total'],
        'adjustment_total': data['adjustment_total'],
        'credit_total': data['credit_total'],
        'jobs': data['jobs'],
    }

    return payment
