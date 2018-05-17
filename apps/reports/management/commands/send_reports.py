import argparse
from django.core.management.base import BaseCommand, CommandError
from reports.links import send_link

class Command(BaseCommand):
    help = 'Generate and send urls of the reports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry',
            help='Dry run of command instead of actual run',
        )

    def handle(self, *args, **options):
        if options['dry']:
            print('dry')
        print('send reports')
        send_link()
