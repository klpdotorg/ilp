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
            '--kannada',
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
        parser.add_argument(
            '--r_type',
            help='report type',
        )
        parser.add_argument(
            '--arg_two',
            help='second argument' 
        )

    def handle(self, *args, **options):
        dry = False
        kannada = False
        filename = 'contacts.csv'
        gp_name = 'abbinahole'
        arg_two = ''
        r_type = 'GPMathContestReport'
        
        if options['filename']:
            filename =  options['filename']
        if options['dry']:
            print('dry running')
            dry = True
        if options['kannada']:
            print('kannada report')
            kannada = True
        if options['gp_name']:
           gp_name = options['gp_name']
        if options['r_type']:
            r_type = options['r_type']
        if options['arg_two']:
            arg_two = options['arg_two']

        send_link(dry,kannada, filename, gp_name, arg_two, r_type)
