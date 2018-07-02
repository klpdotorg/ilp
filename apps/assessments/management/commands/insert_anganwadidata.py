import csv
import sys
from io import StringIO

from common.utils import post_to_slack, Date
from django.db import models
from django.utils import timezone
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from assessments.models import Survey, QuestionGroup, Question, AnswerGroup_Institution, AnswerInstitution
from common.models import Status
from schools.models import Institution


class Command(BaseCommand):
   
    fileoptions = {"assessment"}
    csv_files = {}

    def add_arguments(self, parser):
        parser.add_argument('assessment')

    def get_csv_files(self, options):
        for fileoption in self.fileoptions:
            file_name = options.get(fileoption, None)
            if not file_name:
                print ("Please specify a filename with the --"+fileoption+" argument")
                return False
            f = open(file_name, encoding='utf-8')
            self.csv_files[fileoption] = csv.reader(f)
        return True

    def check_value(self, value, default=None):
        if value.strip() == '':
            if default:
                return default
            return None 
        return value   


    def insert_assessments(self):
        count=0
        questions = []
        date = Date()
        for row in self.csv_files["assessment"]:
            if count == 0:
                count += 1
                continue
            count += 1 
            institution_id = row[3].strip()
            print(count)
            institution = Institution.objects.get(pk=institution_id)
            date_of_visit = date.get_datetime(row[5].strip())
            date_of_visit = timezone.make_aware(date_of_visit, timezone.get_current_timezone())
            is_verified = True
            questiongroup = QuestionGroup.objects.get(pk=30)
            status = Status.objects.get(pk='IA')
            answergroup = AnswerGroup_Institution.objects.create(
                            institution = institution,
                            date_of_visit = date_of_visit,
                            is_verified = True,
                            questiongroup = questiongroup,
                            status = status)
            order = 1
            for column in range(7,33):
               question = Question.objects.get(questiongroup_questions__questiongroup_id=30, questiongroup_questions__sequence=order)
               answer = AnswerInstitution.objects.create(
                            answergroup = answergroup,
                            question=question,
                            answer = row[column])
               order += 1
                            


    def handle(self, *args, **options):
        if not self.get_csv_files(options):
           return
        
        self.insert_assessments()
