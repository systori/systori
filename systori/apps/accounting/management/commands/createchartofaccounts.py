from django.core.management.base import BaseCommand
from systori.apps.accounting import workflow

class Command(BaseCommand):
    help = "Generate skr03 chart of accounts."
    def handle(self, *args, **options):
        workflow.create_chart_of_accounts()