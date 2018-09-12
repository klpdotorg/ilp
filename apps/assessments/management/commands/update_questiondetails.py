import csv
import sys
from io import StringIO

from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from assessments.models import QuestionGroup, Question, QuestionGroup_Questions, Concept, MicroConceptGroup, MicroConcept, QuestionLevel, QuestionInformationType, LearningIndicator


class Command(BaseCommand):
   
    fileoptions = {"questiondetails"}
    csv_files = {}

    def add_arguments(self, parser):
        parser.add_argument('questiondetails')

    def get_csv_files(self, options):
        for fileoption in self.fileoptions:
            file_name = options.get(fileoption, None)
            if not file_name:
                print ("Please specify a filename with the --"+fileoption+" argument")
                return False
            f = open(file_name, encoding='utf-8')
            self.csv_files[fileoption] = csv.reader(f,delimiter='|')
        return True

    def update_questiondetails(self):
        count=0
        for row in self.csv_files["questiondetails"]:
            if count == 0:
                count += 1
                continue
            count += 1
            print(row)
            questiongroup_id = row[0].strip()
            sequence = row[1].strip()
            concept = Concept.objects.get(char_id = row[2].strip())
            microconceptgroup = MicroConceptGroup.objects.get(char_id=row[3].strip())
            microconcept = MicroConcept.objects.get(char_id = row[4].strip())
            questionlevel = QuestionLevel.objects.get(char_id=row[5].strip())
            questioninformationtype = QuestionInformationType.objects.get(char_id=row[6].strip())
            learningindicator = LearningIndicator.objects.get(char_id=row[7].strip())
            question = Question.objects.filter(pk = QuestionGroup_Questions.objects.get(questiongroup_id=questiongroup_id,sequence=sequence).question_id).update(concept=concept, microconcept_group=microconceptgroup, microconcept=microconcept, question_level=questionlevel, question_info_type=questioninformationtype,learning_indicator=learningindicator)


    def handle(self, *args, **options):
        if not self.get_csv_files(options):
           return
        
        self.update_questiondetails()
