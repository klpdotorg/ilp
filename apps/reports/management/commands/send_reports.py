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
            help='file name of contacts in csv format',
        )
        parser.add_argument(
            '--gp_name',
            help='gram panchayat name for report',
        )

    def handle(self, *args, **options):
        dry = False
        filename = 'contacts.csv'
        gp_name = 'abbinahole'
        if options['filename']:
            filename =  options['filename']
        if options['dry']:
            print('dry running')
            dry = True
        if options['gp_name']:
           gp_name = options['gp_name']

        send_link(dry, filename, gp_name)
