import csv
from datetime import datetime

from django.core.management.base import BaseCommand

from assessments.models import QuestionGroup, Question, QuestionGroup_Questions


class Command(BaseCommand):
    help = 'Deletes specified questions associated with the questiongroup'
    fileoptions = {"questions"}
    csv_files = {}

    def add_arguments(self, parser):
        parser.add_argument('questions')

    def get_csv_files(self, options):
        for fileoption in self.fileoptions:
            file_name = options.get(fileoption, None)
            if not file_name:
                print("Please specify a filename with the --"+fileoption+" argument")
                return False
            f = open(file_name, encoding='utf-8')
            self.csv_files[fileoption] = csv.reader(f)
        return True
 
    def delete_questions(self):
        count = 0
        questions = []
        for row in self.csv_files["questions"]:
            if count == 0:
                count += 1
                continue
            count += 1

            questiongroup = QuestionGroup.objects.get(id=row[0].strip())
            sequence = row[1]
            qg_q = QuestionGroup_Questions.objects.get(questiongroup=questiongroup,
                                           sequence=sequence)
            question = qg_q.question
            deleted = qg_q.delete()
            if deleted:
                print("QuestionGroup_Questions mapping deleted")
            deleted = question.delete()
            if deleted:
                print("Question deleted")


    def handle(self, *args, **options):
        if not self.get_csv_files(options):
            return

        self.delete_questions()
