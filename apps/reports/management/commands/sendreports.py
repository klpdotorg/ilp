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
        parser.add_argument('type')
        parser.add_argument('--report_from', required=True)
        parser.add_argument('--report_to', required=True)
        parser.add_argument('filename')
       
    def handle(self, *args, **options):
        generate_report(options['type'], options['filename'], options['report_from'], options['report_to'], options['dry'])
