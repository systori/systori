from django.test import TestCase

from .templatetags import task


class TemplateTagTest(TestCase):

    def is_formula(self, formula):
        self.assertTrue(task.is_formula(formula))

    def is_not_formula(self, formula):
        self.assertFalse(task.is_formula(formula))

    def test_is_formula_true(self):
        self.is_formula('1+1')
        self.is_formula('1e+3')
        self.is_formula('-Infinity')

    def test_is_formula_false(self):
        self.is_not_formula('')
        self.is_not_formula(' ')
        self.is_not_formula('1')
        self.is_not_formula(' 1')
        self.is_not_formula('-1')
        self.is_not_formula('+1')
        self.is_not_formula('1000.0')
        self.is_not_formula('1,000.0')
