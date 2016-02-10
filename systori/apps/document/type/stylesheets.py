from reportlab.lib.styles import StyleSheet1, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

stylesheets = {}

stylesheets['OpenSans'] = StyleSheet1()

stylesheets['OpenSans'].add(ParagraphStyle(name='Small',
                                           fontName='OpenSans-Regular',
                                           fontSize=7,
                                           leading=8.4)
                            )

stylesheets['OpenSans'].add(ParagraphStyle(name='Normal',
                                           fontName='OpenSans-Regular',
                                           fontSize=10,
                                           leading=12)
                            )

stylesheets['OpenSans'].add(ParagraphStyle(name='NormalRight',
                                           parent=stylesheets['OpenSans']['Normal'],
                                           alignment=TA_RIGHT)
                            )

stylesheets['OpenSans'].add(ParagraphStyle(name='Bold',
                                           fontName='OpenSans-Bold',
                                           fontSize=10,
                                           leading=12)
                            )

stylesheets['OpenSans'].add(ParagraphStyle(name='BoldRight',
                                           parent=stylesheets['OpenSans']['Bold'],
                                           alignment=TA_RIGHT)
                            )

stylesheets['OpenSans'].add(ParagraphStyle(name='BodyText',
                                           parent=stylesheets['OpenSans']['Normal'],
                                           spaceBefore=6)
                            )

stylesheets['OpenSans'].add(ParagraphStyle(name='Italic',
                                           parent=stylesheets['OpenSans']['BodyText'],
                                           fontName='OpenSans-Italic')
                            )

stylesheets['OpenSans'].add(ParagraphStyle(name='Heading1',
                                           parent=stylesheets['OpenSans']['Normal'],
                                           fontName='OpenSans-Bold',
                                           fontSize=18,
                                           leading=22,
                                           spaceAfter=6),
                            alias='h1')

stylesheets['OpenSans'].add(ParagraphStyle(name='Title',
                                           parent=stylesheets['OpenSans']['Normal'],
                                           fontName='OpenSans-Bold',
                                           fontSize=18,
                                           leading=22,
                                           alignment=TA_CENTER,
                                           spaceAfter=6),
                            alias='title')

stylesheets['OpenSans'].add(ParagraphStyle(name='Heading2',
                                           parent=stylesheets['OpenSans']['Normal'],
                                           fontName='OpenSans-Bold',
                                           fontSize=14,
                                           leading=18,
                                           spaceBefore=12,
                                           spaceAfter=6),
                            alias='h2')

stylesheets['OpenSans'].add(ParagraphStyle(name='Heading3',
                                           parent=stylesheets['OpenSans']['Normal'],
                                           fontName='OpenSans-Bold',
                                           fontSize=12,
                                           leading=14,
                                           spaceBefore=12,
                                           spaceAfter=6),
                            alias='h3')

stylesheets['OpenSans'].add(ParagraphStyle(name='Heading4',
                                           parent=stylesheets['OpenSans']['Normal'],
                                           fontName='OpenSans-BoldItalic',
                                           fontSize=10,
                                           leading=12,
                                           spaceBefore=10,
                                           spaceAfter=4),
                            alias='h4')

stylesheets['OpenSans'].add(ParagraphStyle(name='Heading5',
                                           parent=stylesheets['OpenSans']['Normal'],
                                           fontName='OpenSans-Bold',
                                           fontSize=9,
                                           leading=10.8,
                                           spaceBefore=8,
                                           spaceAfter=4),
                            alias='h5')

stylesheets['OpenSans'].add(ParagraphStyle(name='Heading6',
                                           parent=stylesheets['OpenSans']['Normal'],
                                           fontName='OpenSans-Bold',
                                           fontSize=7,
                                           leading=8.4,
                                           spaceBefore=6,
                                           spaceAfter=2),
                            alias='h6')

stylesheets['OpenSans'].add(ParagraphStyle(name='Bullet',
                                           parent=stylesheets['OpenSans']['Normal'],
                                           firstLineIndent=0,
                                           spaceBefore=3),
                            alias='bu')

stylesheets['OpenSans'].add(ParagraphStyle(name='Definition',
                                           parent=stylesheets['OpenSans']['Normal'],
                                           firstLineIndent=0,
                                           leftIndent=36,
                                           bulletIndent=0,
                                           spaceBefore=6,
                                           bulletFontName='OpenSans-BoldItalic'),
                            alias='df')

stylesheets['droid-serif'] = StyleSheet1()

stylesheets['droid-serif'].add(ParagraphStyle(name='Small',
                                              fontName='droid-serif.regular',
                                              fontSize=7,
                                              leading=8.4)
                               )

stylesheets['droid-serif'].add(ParagraphStyle(name='Normal',
                                              fontName='droid-serif.regular',
                                              fontSize=10,
                                              leading=12)
                               )

stylesheets['droid-serif'].add(ParagraphStyle(name='NormalRight',
                                              parent=stylesheets['OpenSans']['Normal'],
                                              alignment=TA_RIGHT)
                               )

stylesheets['droid-serif'].add(ParagraphStyle(name='Bold',
                                              fontName='droid-serif.bold',
                                              fontSize=10,
                                              leading=12)
                               )

stylesheets['droid-serif'].add(ParagraphStyle(name='BoldRight',
                                              parent=stylesheets['droid-serif']['Bold'],
                                              alignment=TA_RIGHT)
                               )

stylesheets['droid-serif'].add(ParagraphStyle(name='BodyText',
                                              parent=stylesheets['droid-serif']['Normal'],
                                              spaceBefore=6)
                               )

stylesheets['droid-serif'].add(ParagraphStyle(name='Italic',
                                              parent=stylesheets['droid-serif']['BodyText'],
                                              fontName='droid-serif.italic')
                               )

stylesheets['droid-serif'].add(ParagraphStyle(name='Heading1',
                                              parent=stylesheets['droid-serif']['Normal'],
                                              fontName='droid-serif.bold',
                                              fontSize=18,
                                              leading=22,
                                              spaceAfter=6),
                               alias='h1')

stylesheets['droid-serif'].add(ParagraphStyle(name='Title',
                                              parent=stylesheets['droid-serif']['Normal'],
                                              fontName='droid-serif.bold',
                                              fontSize=18,
                                              leading=22,
                                              alignment=TA_CENTER,
                                              spaceAfter=6),
                               alias='title')

stylesheets['droid-serif'].add(ParagraphStyle(name='Heading2',
                                              parent=stylesheets['droid-serif']['Normal'],
                                              fontName='droid-serif.bold',
                                              fontSize=14,
                                              leading=18,
                                              spaceBefore=12,
                                              spaceAfter=6),
                               alias='h2')

stylesheets['droid-serif'].add(ParagraphStyle(name='Heading3',
                                              parent=stylesheets['droid-serif']['Normal'],
                                              fontName='droid-serif.bold',
                                              fontSize=12,
                                              leading=14,
                                              spaceBefore=12,
                                              spaceAfter=6),
                               alias='h3')

stylesheets['droid-serif'].add(ParagraphStyle(name='Heading4',
                                              parent=stylesheets['droid-serif']['Normal'],
                                              fontName='droid-serif.bold-italic',
                                              fontSize=10,
                                              leading=12,
                                              spaceBefore=10,
                                              spaceAfter=4),
                               alias='h4')

stylesheets['droid-serif'].add(ParagraphStyle(name='Heading5',
                                              parent=stylesheets['droid-serif']['Normal'],
                                              fontName='droid-serif.bold',
                                              fontSize=9,
                                              leading=10.8,
                                              spaceBefore=8,
                                              spaceAfter=4),
                               alias='h5')

stylesheets['droid-serif'].add(ParagraphStyle(name='Heading6',
                                              parent=stylesheets['droid-serif']['Normal'],
                                              fontName='droid-serif.bold',
                                              fontSize=7,
                                              leading=8.4,
                                              spaceBefore=6,
                                              spaceAfter=2),
                               alias='h6')

stylesheets['droid-serif'].add(ParagraphStyle(name='Bullet',
                                              parent=stylesheets['droid-serif']['Normal'],
                                              firstLineIndent=0,
                                              spaceBefore=3),
                               alias='bu')

stylesheets['droid-serif'].add(ParagraphStyle(name='Definition',
                                              parent=stylesheets['droid-serif']['Normal'],
                                              firstLineIndent=0,
                                              leftIndent=36,
                                              bulletIndent=0,
                                              spaceBefore=6,
                                              bulletFontName='droid-serif.bold'),
                               alias='df')

stylesheets['tinos'] = StyleSheet1()

stylesheets['tinos'].add(ParagraphStyle(name='Small',
                                        fontName='Tinos-regular',
                                        fontSize=7,
                                        leading=8.4)
                         )

stylesheets['tinos'].add(ParagraphStyle(name='Normal',
                                        fontName='Tinos-regular',
                                        fontSize=10,
                                        leading=12)
                         )

stylesheets['tinos'].add(ParagraphStyle(name='NormalRight',
                                        parent=stylesheets['tinos']['Normal'],
                                        alignment=TA_RIGHT)
                         )

stylesheets['tinos'].add(ParagraphStyle(name='Bold',
                                        fontName='Tinos-700',
                                        fontSize=10,
                                        leading=12)
                         )

stylesheets['tinos'].add(ParagraphStyle(name='BoldRight',
                                        parent=stylesheets['tinos']['Bold'],
                                        alignment=TA_RIGHT)
                         )

stylesheets['tinos'].add(ParagraphStyle(name='BodyText',
                                        parent=stylesheets['tinos']['Normal'],
                                        spaceBefore=6)
                         )

stylesheets['tinos'].add(ParagraphStyle(name='Italic',
                                        parent=stylesheets['tinos']['BodyText'],
                                        fontName='Tinos-italic')
                         )

stylesheets['tinos'].add(ParagraphStyle(name='Heading1',
                                        parent=stylesheets['tinos']['Normal'],
                                        fontName='Tinos-700',
                                        fontSize=18,
                                        leading=22,
                                        spaceAfter=6),
                         alias='h1')

stylesheets['tinos'].add(ParagraphStyle(name='Title',
                                        parent=stylesheets['tinos']['Normal'],
                                        fontName='Tinos-700',
                                        fontSize=18,
                                        leading=22,
                                        alignment=TA_CENTER,
                                        spaceAfter=6),
                         alias='title')

stylesheets['tinos'].add(ParagraphStyle(name='Heading2',
                                        parent=stylesheets['tinos']['Normal'],
                                        fontName='Tinos-700',
                                        fontSize=14,
                                        leading=18,
                                        spaceBefore=12,
                                        spaceAfter=6),
                         alias='h2')

stylesheets['tinos'].add(ParagraphStyle(name='Heading3',
                                        parent=stylesheets['tinos']['Normal'],
                                        fontName='Tinos-700',
                                        fontSize=12,
                                        leading=14,
                                        spaceBefore=12,
                                        spaceAfter=6),
                         alias='h3')

stylesheets['tinos'].add(ParagraphStyle(name='Heading4',
                                        parent=stylesheets['tinos']['Normal'],
                                        fontName='Tinos-700italic',
                                        fontSize=10,
                                        leading=12,
                                        spaceBefore=10,
                                        spaceAfter=4),
                         alias='h4')

stylesheets['tinos'].add(ParagraphStyle(name='Heading5',
                                        parent=stylesheets['tinos']['Normal'],
                                        fontName='Tinos-700',
                                        fontSize=9,
                                        leading=10.8,
                                        spaceBefore=8,
                                        spaceAfter=4),
                         alias='h5')

stylesheets['tinos'].add(ParagraphStyle(name='Heading6',
                                        parent=stylesheets['tinos']['Normal'],
                                        fontName='Tinos-700',
                                        fontSize=7,
                                        leading=8.4,
                                        spaceBefore=6,
                                        spaceAfter=2),
                         alias='h6')

stylesheets['tinos'].add(ParagraphStyle(name='Bullet',
                                        parent=stylesheets['tinos']['Normal'],
                                        firstLineIndent=0,
                                        spaceBefore=3),
                         alias='bu')

stylesheets['tinos'].add(ParagraphStyle(name='Definition',
                                        parent=stylesheets['tinos']['Normal'],
                                        firstLineIndent=0,
                                        leftIndent=36,
                                        bulletIndent=0,
                                        spaceBefore=6,
                                        bulletFontName='Tinos-700'),
                         alias='df')
