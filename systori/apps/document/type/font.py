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
    "OpenSans-Semibold",
    "droid-serif.bold-italic",
    "droid-serif.bold",
    "droid-serif.italic",
    "droid-serif.regular",
    "Tinos-700",
    "Tinos-700italic",
    "Tinos-italic",
    "Tinos-regular"
]
for font_name in font_names:
    pdfmetrics.registerFont(TTFont(font_name, font_name+'.ttf'))

pdfmetrics.registerFontFamily(
    'OpenSans',
    normal='OpenSans-Regular',
    bold='OpenSans-Bold',
    italic='OpenSans-Italic',
    boldItalic='OpenSans-BoldItalic'
)

pdfmetrics.registerFontFamily(
    'Droid-Serif',
    normal="droid-serif.regular",
    bold="droid-serif.bold",
    italic="droid-serif.italic",
    boldItalic="droid-serif.bold-italic"
)

pdfmetrics.registerFontFamily(
    'Tinos',
    normal="Tinos-regular",
    bold="Tinos-700",
    italic="Tinos-italic",
    boldItalic="Tinos-700italic"
)