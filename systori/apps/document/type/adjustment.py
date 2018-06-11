from io import BytesIO
from datetime import date

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from .style import NumberedSystoriDocument
from .style import NumberedLetterheadCanvas, NumberedCanvas
from .style import get_available_width_height_and_pagesize
from .style import heading_and_date, get_address_label, get_address_label_spacer
from .font import FontManager


DEBUG_DOCUMENT = False  # Shows boxes in rendered output


def render(adjustment, letterhead, format):

    with BytesIO() as buffer:

        font = FontManager(letterhead.font)
        available_width, available_height, pagesize = get_available_width_height_and_pagesize(
            letterhead
        )
        document_date = date_format(
            date(*map(int, adjustment["document_date"].split("-"))), use_l10n=True
        )
        doc = NumberedSystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

        flowables = [
            get_address_label(adjustment, font),
            get_address_label_spacer(adjustment),
            heading_and_date(
                adjustment.get("title") or _("Adjustment"),
                document_date,
                font,
                available_width,
                debug=DEBUG_DOCUMENT,
            ),
        ]
        if format == "print":
            doc.build(flowables, NumberedCanvas, letterhead)
        else:
            doc.build(
                flowables, NumberedLetterheadCanvas.factory(letterhead), letterhead
            )

        return buffer.getvalue()


def serialize(adjustment):
    pass
