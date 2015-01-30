from decimal import Decimal
from django.test import TestCase
from django.utils.translation import activate
from .templatetags.customformatting import *

class CustomFormattingTest(TestCase):

    def test_cleandecimal(self):
        for language, sep in [('en','.'),('de',',')]:
          activate(language)
          self.assertEqual('1%s00'%sep, cleandecimal('1%s00'%sep,2))
          self.assertEqual('1%s00'%sep, cleandecimal('1',2))
          self.assertEqual('1%s00'%sep, cleandecimal('1%s0'%sep,2))
          self.assertEqual('1%s00'%sep, cleandecimal('1%s000000'%sep,2))
          self.assertEqual('1%s001'%sep, cleandecimal('1%s001000'%sep,2))
          self.assertEqual('1234567891%s04'%sep, cleandecimal('1234567891%s040000'%sep, 2))