import csv
import sys
from io import StringIO

from django.core.management.base import BaseCommand, CommandError
from assessments.models import Concept, MicroConceptGroup, MicroConcept, QuestionLevel, QuestionInformationType, LearningIndicator


class Command(BaseCommand):
   
    fileoptions = {"concept", "microconceptgroup", "microconcept", "level", "questioninformationtype", "learningindicator"}
    csv_files = {}

    def add_arguments(self, parser):
        parser.add_argument('concept')
        parser.add_argument('microconceptgroup')
        parser.add_argument('microconcept')
        parser.add_argument('level')
        parser.add_argument('questioninformationtype')
        parser.add_argument('learningindicator')

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

    def create_object(self, type, instance):
        count=0
        data_created = []
        for row in self.csv_files[type]:
            if count == 0:
                count += 1
                continue
            count += 1
            char_id = row[0].strip()
            description= row[1].strip()
            data, created = instance.objects.get_or_create(
                         char_id = char_id,
                         description = description)
            data_created.append(data)
        return data_created 

    
    def handle(self, *args, **options):
        if not self.get_csv_files(options):
           return

        concept = self.create_object("concept", Concept)
        microconceptgroup = self.create_object("microconceptgroup", MicroConceptGroup)
        microconcept = self.create_object("microconcept", MicroConcept)
        level = self.create_object("level", QuestionLevel)
        learningindicator = self.create_object("learningindicator", LearningIndicator)
        questioninformationtype  = self.create_object("questioninformationtype", QuestionInformationType)
