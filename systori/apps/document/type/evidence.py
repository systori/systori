from io import BytesIO
from reportlab.pdfgen import canvas
from django.utils.translation import ugettext_lazy as _


def render(project):

    with BytesIO() as buffer:
        p = canvas.Canvas(buffer)

        p.drawString(100, 100, "Hello world.")

        p.showPage()
        p.save()
        return buffer.getvalue()