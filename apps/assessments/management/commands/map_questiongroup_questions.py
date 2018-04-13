import csv
import sys
from io import StringIO

from django.utils import timezone
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from assessments.models import Survey, QuestionGroup, Question, QuestionGroup_Questions, Partner, SurveyOnType, Source, SurveyType, QuestionType, SurveyUserTypeMapping, SurveyTag, SurveyTagMapping
from common.models import Status, AcademicYear, InstitutionType, RespondentType
from boundary.models import Boundary


class Command(BaseCommand):
   
    fileoptions = {"questiongroup_questions"}
    csv_files = {}

    def add_arguments(self, parser):
        parser.add_argument('questiongroup_questions')

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


    def map_questiongroup_questions(self):
        count=0
        questions = []
        for row in self.csv_files["questiongroup_questions"]:
            if count == 0:
                count += 1
                continue
            count += 1

            questiongroup = QuestionGroup.objects.get(row[0].strip())
            question = Question.objects.get(row[1].strip())
            qgq_map = QuestionGroup_Questions.objects.create(
                      sequence = count,
                      question = question,
                      questiongroup = questiongroup)
            qgq_maps.append(qgq_map)

        return qgq_maps
                        

    def handle(self, *args, **options):
        if not self.get_csv_files(options):
           return
        
        qgq_maps = self.map_questiongroup_questions()
        if not qgq_maps:
            print("QuestionGroup Question Mapping did not happen")
            return
