import csv
#from datetime import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.conf import settings
from schools.models import Institution
from assessments.models import (AnswerGroup_Institution, AnswerInstitution,
                                QuestionGroup_Questions, QuestionGroup
                                )

#now = datetime.now()
now = timezone.now()


class Command(BaseCommand):

    dise_column = 3
    qgroupname_column = 2
    qstart_column = 4
    num_questions = 11
    args = ""
    academicyear = settings.DISE_ACADEMIC_YEAR.replace('-', '')
    help = """python3 manage.py loadgpc filename"""

    def add_arguments(self, parser):
        parser.add_argument('filename')

    def handle(self, *args, **options):
        csv_file = options.get('filename', None)
        answergroup_count = 0
        answer_count = 0

        with open(csv_file, 'r+', encoding='utf-8') as data_file:
            data = csv.reader(data_file)
            rowcount = 0
            for row in data:
                if rowcount == 0:
                    rowcount += 1
                    continue

                rowcount += 1
                if not row[self.dise_column].isdigit():
                    print("Invalid entry for dise: "+row[self.dise_column] +
                          " in row: "+str(rowcount))
                    continue
                try:
                    institution = Institution.objects.get(
                                   dise_id__school_code=row[self.dise_column],
                                   dise_id__academic_year_id=self.academicyear)
                except Institution.DoesNotExist:
                    print("Invalid institution,disecode: " +
                          row[self.dise_column] +
                          " in row:"+str(rowcount))
                    continue
                try:
                    qgroup = QuestionGroup.objects.get(
                                             name=row[self.qgroupname_column])
                except QuestionGroup.DoesNotExist:
                    print("Invalid QuestionGroup, name: " +
                          row[self.qgroupname_column] +
                          " in row:"+str(rowcount))
                    continue
                except QuestionGroup.MultipleObjectsReturned:
                    print("Invalid QuestionGroup, name: " +
                          row[self.qgroupname_column] +
                          " in row:"+str(rowcount))
                    continue

                questions = QuestionGroup_Questions.objects.filter(
                                                questiongroup=qgroup).values(
                                                    'question_id', 'sequence')
                if questions.count() != self.num_questions:
                    print("Number of questions in questiongroup: " +
                          str(questions.count()) +
                          ", does not match number specified: " +
                          str(self.num_questions))
                    break
                if len(row) < self.qstart_column + self.num_questions:
                    print("Lesser columns specified in the row: " +
                          str(rowcount))
                    continue

                entered_at = now

                answergroup = AnswerGroup_Institution.objects.create(
                                questiongroup=qgroup,
                                institution=institution,
                                entered_at=entered_at,
                                status_id='AC',
                                is_verified=True)

                answergroup_count += 1

                for question in questions:
                    ans = row[self.qstart_column+question['sequence']-1]
                    if not ans.isdigit():
                        print("Answer is not a number: "+ans+" for column: " +
                              str(self.qstart_column+question['sequence']-1) +
                              " for row: "+str(rowcount))
                        continue
                    AnswerInstitution.objects.create(
                                answer=ans,
                                answergroup=answergroup,
                                question_id=question['question_id'])

                    answer_count += 1

        print("%d AnswerGroup created, %d Answers created" % (
              answergroup_count, answer_count))
