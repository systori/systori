from django.test import TestCase
from django.core.urlresolvers import reverse


class UrlTest(TestCase):

    def test_report(self):
        self.assertTrue(reverse('report', args=[2019, 10]).endswith('report/2019/10/'))
        self.assertTrue(reverse('report', args=[2019]).endswith('report/2019/'))
        self.assertTrue(reverse('report').endswith('report/'))
