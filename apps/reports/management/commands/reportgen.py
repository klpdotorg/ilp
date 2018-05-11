import argparse
from django.core.management.base import BaseCommand, CommandError
from reports.generator import generate_report

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    fileoptions = {"questiongroup","questions"}

    def add_arguments(self, parser):
        parser.add_argument('type')
        parser.add_argument('format')
        parser.add_argument('output')
        parser.add_argument('arguments', nargs=argparse.REMAINDER)

    def handle(self, *args, **options):
        generate_report(options['format'],options['type'],options['output'
        ],options['arguments'])
