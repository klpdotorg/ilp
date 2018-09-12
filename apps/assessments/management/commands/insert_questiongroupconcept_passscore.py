import csv
import sys
from io import StringIO

from django.core.management.base import BaseCommand, CommandError
from assessments.models import Concept, MicroConceptGroup, MicroConcept, QuestionGroup, QuestionGroupConcept


class Command(BaseCommand):
   
    fileoptions = {"questiongroup_concept_passscore"}
    csv_files = {}

    def add_arguments(self, parser):
        parser.add_argument('questiongroup_concept_passscore')

    def get_csv_files(self, options):
        for fileoption in self.fileoptions:
            file_name = options.get(fileoption, None)
            if not file_name:
                print ("Please specify a filename with the --"+fileoption+" argument")
                return False
            f = open(file_name, encoding='utf-8')
            self.csv_files[fileoption] = csv.reader(f,delimiter='|')
        return True

    def check_value(self, value, default=None):
        if value.strip() == '':
            if default:
                return default
            return None 
        return value   

    def insert_questiongroup_concept_passscore(self):
        count=0
        data_created = []
        for row in self.csv_files["questiongroup_concept_passscore"]:
            if count == 0:
                count += 1
                continue
            count += 1
            questiongroup = QuestionGroup.objects.get(id=row[0].strip())
            concept = Concept.objects.get(char_id=row[1].strip())
            microconcept_group = MicroConceptGroup.objects.get(char_id=row[2].strip())
            microconcept = MicroConcept.objects.get(char_id=row[3].strip())
            passscore = row[4].strip()
            data, created = QuestionGroupConcept.objects.get_or_create(
                         questiongroup = questiongroup,
                         concept = concept.char_id,
                         microconcept_group = microconcept_group.char_id,
                         microconcept = microconcept.char_id,
                         pass_score = passscore)
            data_created.append(data)
        return data_created 


    def handle(self, *args, **options):
        if not self.get_csv_files(options):
           return

        qg_c = self.insert_questiongroup_concept_passscore()
