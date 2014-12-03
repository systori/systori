from django.test import TestCase
from django.contrib.auth import get_user_model
from ..project.models import *
from .models import *

class EstimateCalculationTests(TestCase):

    def test_simple(self):
        proj = Project.objects.create(
                name="my project")
        p = Proposal.objects.create(project=proj)
        u = Unit.objects.create()
        labor = LineItemType.objects.create(
                name="labor")
        materials = LineItemType.objects.create(
                name="materials")
        e = Estimate.objects.create(proposal=p)
        li = LineItem.objects.create(
                estimate=e,
                value = 10, unit = u,
                itemtype = labor)
