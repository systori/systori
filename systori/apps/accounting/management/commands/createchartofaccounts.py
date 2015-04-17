from django.core.management.base import BaseCommand
from systori.apps.accounting import skr03

class Command(BaseCommand):
    help = "Generate skr03 chart of accounts."
    def handle(self, *args, **options):
        skr03.create_chart_of_accounts()