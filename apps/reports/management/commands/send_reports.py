import argparse
from django.core.management.base import BaseCommand, CommandError
from reports.links import send_link

class Command(BaseCommand):
    help = 'Generate and send urls of the reports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry',
            action= 'store_true',
            help='Dry run of command instead of actual run',
        )
        parser.add_argument(
            '--filename',
            help='Dry run of command instead of actual run',
        )

    def handle(self, *args, **options):
        dry = False
        filename = 'contacts.csv'

        if options['filename']:
            filename =  options['filename']
        if options['dry']:
            print('dry running')
            dry = True

        send_link(dry, filename)
