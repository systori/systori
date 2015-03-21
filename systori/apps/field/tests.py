from django.test import TestCase
from datetime import date

from .utils import find_next_workday

class TestDateCalculations(TestCase):

    def test_find_next_workday(self):
        self.assertEqual(date(2015, 3, 20), find_next_workday(date(2015, 3, 19)))
        self.assertEqual(date(2015, 3, 23), find_next_workday(date(2015, 3, 20)))
        self.assertEqual(date(2015, 3, 23), find_next_workday(date(2015, 3, 21)))
        self.assertEqual(date(2015, 3, 23), find_next_workday(date(2015, 3, 22)))
        self.assertEqual(date(2015, 3, 24), find_next_workday(date(2015, 3, 23)))