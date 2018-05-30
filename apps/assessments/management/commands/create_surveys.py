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
   
    fileoptions = {"survey", "questiongroup", "questions", "surveyusertype", "surveytag"}
    csv_files = {}

    def add_arguments(self, parser):
        parser.add_argument('survey')
        parser.add_argument('questiongroup')
        parser.add_argument('questions')
        parser.add_argument('surveyusertype')
        parser.add_argument('surveytag')

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

    def create_survey(self):
        count=0
        for row in self.csv_files["survey"]:
            if count == 0:
                count += 1
                continue
            count += 1
            id = row[0].strip()
            name = row[1].strip()
            description = row[2].strip()
            partner = Partner.objects.get(char_id=row[3].strip())
            status = Status.objects.get(char_id = row[4].strip())
            state = Boundary.objects.get(id=row[5].strip())
            survey_on_id = SurveyOnType.objects.get(char_id=row[6].strip())
            lang_name = row[7].strip()
            survey = Survey.objects.create(
                         id = id,
                         name = name,
                         description = description,
                         partner = partner,
                         status = status,
                         survey_on = survey_on_id,
                         lang_name = lang_name,
                         admin0 = state)
            return survey


    def create_questiongroup(self, survey):
        count=0
        for row in self.csv_files["questiongroup"]:
            if count == 0:
                count += 1
                continue
            count += 1

            id = row[0].strip()
            name = row[1].strip()
            group_text = row[2].strip()
            start_date = datetime.strptime(row[3].strip(), "%d-%m-%Y").date()
            version = row[5].strip()
            double_entry = row[6].strip()
            academicyear = AcademicYear.objects.get(char_id=row[7].strip())
            institution_type = InstitutionType.objects.get(char_id=row[8].strip())
            source = Source.objects.get(id=row[9].strip())
            status = Status.objects.get(char_id=row[10].strip())
            type_id = SurveyType.objects.get(char_id=row[11].strip())
            description = row[12].strip()
            image_required = row[13].strip()
            lang_name = row[14].strip()
            comments_required = row[15].strip()
            respondenttype_required = row[16].strip()
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
                                survey = survey,
                                type = type_id,
                                description = description,
                                lang_name = lang_name,
                                image_required = image_required,
                                comments_required = comments_required,
                                respondenttype_required = respondenttype_required)
            return questiongroup 


    def create_questions(self):
        count=0
        questions = []
        for row in self.csv_files["questions"]:
            if count == 0:
                count += 1
                continue
            count += 1

            id = row[0].strip()
            question = Question.objects.filter(pk=id)
            if question:
                questions.append(question[0])
                continue
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
                            id = id,
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


    def map_questiongroup_questions(self, questiongroup, questions):
        qgq_maps = []
        sequence = 1
        for question in questions:
            qgq_map = QuestionGroup_Questions.objects.create(
                      sequence = sequence,
                      question = question,
                      questiongroup = questiongroup)
            sequence += 1
            qgq_maps.append(qgq_map)

        return qgq_maps

 
    def map_survey_usertype(self, survey):
        count=0
        su_maps = []
        for row in self.csv_files["surveyusertype"]:
            if count == 0:
                count += 1
                continue
            count += 1
            user_type = RespondentType.objects.get(char_id = row[0].strip())
            su_map = SurveyUserTypeMapping.objects.create(
                         usertype = user_type,
                         survey = survey)
            su_maps.append(su_map)
        return su_maps
                        
 
    def map_surveytag(self, survey):
        count=0
        st_maps = []
        for row in self.csv_files["surveytag"]:
            if count == 0:
                count += 1
                continue
            count += 1
            tag = SurveyTag.objects.get(char_id = row[0].strip())
            st_map = SurveyTagMapping.objects.create(
                         tag = tag,
                         survey = survey)
            st_maps.append(st_map)
        return st_maps


    def handle(self, *args, **options):
        if not self.get_csv_files(options):
           return
        
        #create survey
        survey = self.create_survey()
        if not survey:
            print("Survey did not get created")
            return

        #create questiongroup
        questiongroup = self.create_questiongroup(survey)
        if not questiongroup:
            print("QuestionGroup did not get created")
            return

        questions = self.create_questions()
        if not questions:
            print("Questions did not get created")
            return

        qgq_maps = self.map_questiongroup_questions(questiongroup, questions)
        if not qgq_maps:
            print("QuestionGroup Question Mapping did not happen")
            return
  
        survey_user_map = self.map_survey_usertype(survey)
        if not survey_user_map:
            print("Survey UserType Mapping did not happen")
            return

        survey_tag = self.map_surveytag(survey)
        if not survey_tag:
            print("Survey Tag Mapping did not happen")
            return
  
