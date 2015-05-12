import os.path
from django.conf import settings
from reportlab import rl_config

rl_config.TTFSearchPath = [os.path.join(settings.BASE_DIR, 'static/fonts')]

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

font_names = [
    "OpenSans-BoldItalic",
    "OpenSans-Bold",
    "OpenSans-ExtraBoldItalic",
    "OpenSans-ExtraBold",
    "OpenSans-Italic",
    "OpenSans-LightItalic",
    "OpenSans-Light",
    "OpenSans-Regular",
    "OpenSans-SemiboldItalic",
    "OpenSans-Semibold"
]
for font_name in font_names:
    pdfmetrics.registerFont(TTFont(font_name, font_name+'.ttf'))

normal = 'OpenSans-Regular'
bold = 'OpenSans-Bold'
italic = 'OpenSans-Italic'
boldItalic = 'OpenSans-BoldItalic'

pdfmetrics.registerFontFamily(
    'OpenSans',
    normal=normal,
    bold=bold,
    italic=italic,
    boldItalic=boldItalic
)
