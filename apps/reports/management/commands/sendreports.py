import argparse
from django.core.management.base import BaseCommand, CommandError
from reports.generator import generate_report

class Command(BaseCommand):
    help = 'Send links for reports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry',
            action= 'store_true',
            help='Dry run of command instead of actual run, always put first in argument',
        )
        parser.add_argument('type', help="Which report to send")
        parser.add_argument('--from', required=True, help="Start date for reports")
        parser.add_argument('--to', required=True, help="End date for reports")
        parser.add_argument('--skip', default=0, type=int, help="Skip these many lines from the input csv file. Useful to continue in case ofan interruption")
        parser.add_argument('filename')
       
    def handle(self, *args, **options):
        generate_report(options['type'], options['filename'], options['from'], options['to'], options['dry'], options['skip'], False)
