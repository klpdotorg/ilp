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
   
    fileoptions = {"questiongroup","questions"}
    csv_files = {}

    def add_arguments(self, parser):
        parser.add_argument('questiongroup')
        parser.add_argument('questions',nargs='?')

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


    def create_questiongroup(self):
        count=0
        questiongroups = []
        for row in self.csv_files["questiongroup"]:
            if count == 0:
                count += 1
                continue
            count += 1

            survey_id = Survey.objects.get(id=row[0].strip())
            id = row[1].strip()
            if id != '':
                questiongroup = QuestionGroup.objects.filter(pk=id)
                if questiongroup:
                    return questiongroup 
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
            respondenttype_required = row[17].strip()
            questiongroup = QuestionGroup.objects.create(
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
                                comments_required = comments_required,
                                respondenttype_required = respondenttype_required)
            questiongroups.append(questiongroup)
        return questiongroups


    def create_questions(self):
        count=0
        questions = []
        for row in self.csv_files["questions"]:
            if count == 0:
                count += 1
                continue
            count += 1

            id = row[0].strip()
            if id != '':
                question = Question.objects.get(pk=id)
                questions.append(question)
            else:
                question_text = row[1].strip()
                display_text = row[2].strip()
                key = self.check_value(row[3].strip())
                options = self.check_value(row[4].strip())
                is_featured = self.check_value(row[5].strip(), True)
                question_type = QuestionType.objects.get(id = self.check_value(row[6].strip(),4))
                status = Status.objects.get(char_id=row[7].strip())
                max_score = self.check_value(row[8].strip(),0)
                pass_score = self.check_value(row[9].strip(),0)
                lang_name = self.check_value(row[10].strip())
                lang_options = self.check_value(row[11].strip())
                question = Question.objects.create(
                            question_text = question_text,
                            display_text = display_text,
                            key = key,
                            options = options,
                            is_featured = is_featured,
                            question_type = question_type,
                            status = status,
                            max_score = max_score,
                            pass_score = pass_score,
                            lang_name = lang_name,
                            lang_options = lang_options)
                questions.append(question)
        return questions


    def map_questiongroup_questions(self, questiongroups, questions):
        for questiongroup in questiongroups:
            sequence = 1
            for question in questions:
                qgq_map = QuestionGroup_Questions.objects.create(
                          sequence = sequence,
                          question = question,
                          questiongroup = questiongroup)
                sequence += 1


    def handle(self, *args, **options):
        if not self.get_csv_files(options):
           return
        
        #create questiongroup
        questiongroups = self.create_questiongroup()
        if not questiongroups:
            print("QuestionGroup did not get created")
            return

        if options["questions"]:
            questions = self.create_questions()
            if not questions:
                print("Questions did not get created")
                return
  
            self.map_questiongroup_questions(questiongroups, questions)
