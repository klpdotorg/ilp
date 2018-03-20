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
   
    fileoptions = {"questiongroup"}
    csv_files = {}

    def add_arguments(self, parser):
        parser.add_argument('questiongroup')

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


    def create_questiongroup(self, survey):
        count=0
        for row in self.csv_files["questiongroup"]:
            if count == 0:
                count += 1
                continue
            count += 1

            survey_id = Survey.objects.get(id=row[0].strip())
            id = row[1].strip()
            name = row[2].strip()
            group_text = row[3].strip()
            start_date = datetime.strptime(row[4].strip(), "%d-%m-%Y").date()
            version = row[6].strip()
            double_entry = row[7].strip()
            academicyear = AcademicYear.objects.get(char_id=row[8].strip())
            institution_type = InstitutionType.objects.get(char_id=row[9].strip())
            source = Source.objects.get(id=row[10].strip())
            status = Status.objects.get(char_id=row[11].strip())
            type_id = SurveyType.objects.get(char_id=row[12].strip())
            description = row[13].strip()
            image_required = row[14].strip()
            lang_name = row[15].strip()
            comments_required = row[16].strip()
            questiongroup = QuestionGroup.objects.create(
                                id = id,
                                name = name,
                                group_text = group_text,
                                start_date = start_date,
                                version = version,
                                double_entry = double_entry,
                                created_at = timezone.now(),
                                academic_year = academicyear,
                                inst_type = institution_type,
                                source = source,
                                status = status,
                                survey = survey_id,
                                type = type_id,
                                description = description,
                                lang_name = lang_name,
                                image_required = image_required,
                                comments_required = comments_required)
            return questiongroup 


    def handle(self, *args, **options):
        if not self.get_csv_files(options):
           return
        
        #create questiongroup
        questiongroup = self.create_questiongroup(survey)
        if not questiongroup:
            print("QuestionGroup did not get created")
            return
