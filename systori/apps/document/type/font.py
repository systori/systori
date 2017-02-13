import os.path
from django.conf import settings
from reportlab import rl_config
from reportlab.lib.styles import StyleSheet1, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

rl_config.TTFSearchPath = [os.path.join(settings.BASE_DIR, 'static/fonts')]

font_families = [
    "OpenSans",
    "DroidSerif",
    "Tinos",
    "Ubuntu"
]

for font_name in font_families:
    for font_face in ['Regular', 'Italic', 'Bold', 'BoldItalic']:
        font_family_member = '{}-{}'.format(font_name, font_face)
        pdfmetrics.registerFont(TTFont(font_family_member, font_family_member+'.ttf'))
    pdfmetrics.registerFontFamily(
        font_name,
        normal='{}-Regular'.format(font_name),
        bold='{}-Bold'.format(font_name),
        italic='{}-Italic'.format(font_name),
        boldItalic='{}-BoldItalic'.format(font_name)
    )

fonts = {}
for font_name in font_families:
    fonts[font_name] = StyleSheet1()
    fonts[font_name].add(ParagraphStyle(name='Small',
                                        fontName='{}-Regular'.format(font_name),
                                        fontSize=7,
                                        leading=8.4)
                         )
    fonts[font_name].add(ParagraphStyle(name='SmallRight',
                                        parent=fonts[font_name]['Small'],
                                        alignment=TA_RIGHT)
                         )
    fonts[font_name].add(ParagraphStyle(name='Normal',
                                        fontName='{}-Regular'.format(font_name),
                                        fontSize=10,
                                        leading=12)
                         )
    fonts[font_name].add(ParagraphStyle(name='NormalRight',
                                        parent=fonts[font_name]['Normal'],
                                        alignment=TA_RIGHT)
                         )
    fonts[font_name].add(ParagraphStyle(name='Bold',
                                        fontName='{}-Bold'.format(font_name),
                                        fontSize=10,
                                        leading=12)
                         )
    fonts[font_name].add(ParagraphStyle(name='BoldRight',
                                        parent=fonts[font_name]['Bold'],
                                        alignment=TA_RIGHT)
                         )
    fonts[font_name].add(ParagraphStyle(name='BodyText',
                                        parent=fonts[font_name]['Normal'],
                                        spaceBefore=6)
                         )
    fonts[font_name].add(ParagraphStyle(name='Italic',
                                        parent=fonts[font_name]['BodyText'],
                                        fontName='{}-Bold'.format(font_name))
                         )
    fonts[font_name].add(ParagraphStyle(name='Title',
                                        parent=fonts[font_name]['Normal'],
                                        fontName='{}-Bold'.format(font_name),
                                        fontSize=18,
                                        leading=22,
                                        spaceAfter=6,
                                        alignment=TA_CENTER),
                         alias='title')
    fonts[font_name].add(ParagraphStyle(name='Heading1',
                                        parent=fonts[font_name]['Normal'],
                                        fontName='{}-Bold'.format(font_name),
                                        fontSize=18,
                                        leading=22,
                                        spaceAfter=6),
                         alias='h1')
    fonts[font_name].add(ParagraphStyle(name='Heading2',
                                        parent=fonts[font_name]['Normal'],
                                        fontName='{}-Bold'.format(font_name),
                                        fontSize=14,
                                        leading=18,
                                        spaceBefore=12,
                                        spaceAfter=6),
                         alias='h2')
    fonts[font_name].add(ParagraphStyle(name='Heading3',
                                        parent=fonts[font_name]['Normal'],
                                        fontName='{}-Bold'.format(font_name),
                                        fontSize=12,
                                        leading=14,
                                        spaceBefore=12,
                                        spaceAfter=6),
                         alias='h3')
    fonts[font_name].add(ParagraphStyle(name='Heading4',
                                        parent=fonts[font_name]['Normal'],
                                        fontName='{}-BoldItalic'.format(font_name),
                                        fontSize=10,
                                        leading=12,
                                        spaceBefore=10,
                                        spaceAfter=4),
                         alias='h4')
    fonts[font_name].add(ParagraphStyle(name='Heading5',
                                        parent=fonts[font_name]['Normal'],
                                        fontName='{}-Bold'.format(font_name),
                                        fontSize=9,
                                        leading=10.8,
                                        spaceBefore=8,
                                        spaceAfter=4),
                         alias='h5')
    fonts[font_name].add(ParagraphStyle(name='Heading6',
                                        parent=fonts[font_name]['Normal'],
                                        fontName='{}-Bold'.format(font_name),
                                        fontSize=7,
                                        leading=8.4,
                                        spaceBefore=6,
                                        spaceAfter=2),
                         alias='h6')
    fonts[font_name].add(ParagraphStyle(name='Bullet',
                                        parent=fonts[font_name]['Normal'],
                                        firstLineIndent=0,
                                        spaceBefore=3),
                         alias='bu')
    fonts[font_name].add(ParagraphStyle(name='Definition',
                                        parent=fonts[font_name]['Normal'],
                                        firstLineIndent=0,
                                        leftIndent=36,
                                        bulletIndent=0,
                                        spaceBefore=6,
                                        bulletFontName='{}-BoldItalic'.format(font_name)),
                         alias='df')


class FontManager:

    def __init__(self, font):
        self.font = fonts[font]

    @property
    def bold(self):
        return self.font.byName.get('Bold')

    @property
    def bold_right(self):
        return self.font.byName.get('BoldRight')

    @property
    def normal(self):
        return self.font.byName.get('Normal')

    @property
    def normal_right(self):
        return self.font.byName.get('NormalRight')

    @property
    def h2(self):
        return self.font.byName.get('Heading2')

    @property
    def small(self):
        return self.font.byName.get('Small')

    @property
    def small_right(self):
        return self.font.byName.get('SmallRight')
