from datetime import datetime

from django.core.management.base import BaseCommand

from assessments.models import AnswerGroup_Student


class Command(BaseCommand):
    help = 'Removes data for classes that are not valid (class other than 4 and 5)'

    def add_arguments(self, parser):
        parser.add_argument(
            '-c', '--count',
            help='Show the count and exit without deleting anything',
            action='store_true'
        )

    def handle(self, *args, **options):
            qs_1617 = AnswerGroup_Student.objects.filter(
                questiongroup__survey=3, student__studentstudentgrouprelation__academic_year  = '1617',  questiongroup__academic_year='1617', student__studentstudentgrouprelation__student_group__name__in = ['1','2','3','6','7','8','9','10'])
            qs_1718 = AnswerGroup_Student.objects.filter(
                questiongroup__survey=3, student__studentstudentgrouprelation__academic_year  = '1718',  questiongroup__academic_year='1718', student__studentstudentgrouprelation__student_group__name__in = ['1','2','3','7','8','9','10'])


            if options['count']:
                print("The number of incorrect entries in year 2016-2017 is: ",qs_1617.count())
                print("The number of incorrect entries in year 2017-2018 is: ",qs_1718.count())
            else: 
                deleted = qs_1617.delete()
                print("Deleted entries for 2016-2017 :",deleted)
                deleted = qs_1718.delete()
                print("Deleted entries for 2017-2018 :",deleted)
