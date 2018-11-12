from datetime import datetime

from django.core.management.base import BaseCommand

from assessments.models import AnswerGroup_Institution


class Command(BaseCommand):
    help = 'Fixes '

    def add_arguments(self, parser):
        parser.add_argument('mobile_no', nargs='+', type=str)
        parser.add_argument(
            '-c', '--count',
            help='Show the count and exit without deleting anything',
            action='store_true'
        )
        parser.add_argument(
            '-f', '--from',
            help='From date'
        )
        parser.add_argument(
            '-t', '--to',
            help='To date'
        )

    def handle(self, *args, **options):
        for number in options['mobile_no']:
            qs = AnswerGroup_Institution.objects.filter(
                created_by__mobile_no=number
            )

            if options['from'] is not None and options['to'] is not None:
                from_date = datetime.strptime(options['from'], '%Y-%m-%d')
                to_date = datetime.strptime(options['to'], '%Y-%m-%d')
                qs = qs.filter(
                    entered_at__range=[from_date, to_date]
                )

            # If only count is requested, show counts and exit
            if options['count']:
                self.stdout.write(
                    self.style.SUCCESS(
                        '%s: AnswerGroup_Institution - %s' % (
                            number, qs.count(),
                        )
                    )
                )
            else:
                deleted = qs.delete()
                self.stdout.write(
                    self.style.SUCCESS('%s: %s' % (number, deleted, ))
                )
