from django.core.management.base import BaseCommand

from assessments.models import AnswerGroup_Institution


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('mobile_no', nargs='+', type=str)

    def handle(self, *args, **options):
        for number in options['mobile_no']:
            deleted = AnswerGroup_Institution.objects.filter(
                created_by__mobile_no=number
            ).delete()
            self.stdout.write(
                self.style.SUCCESS('%s: %s' % (number, deleted, ))
            )
