from reports.boundary_reports import (
    BaseReport,
    format_academic_year)
import argparse
import hashlib
import random
import pdfkit
import os.path
import datetime

from abc import ABC, abstractmethod

from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

from boundary.models import Boundary, ElectionBoundary
from schools.models import Institution
from django.db.models import Sum

from assessments.models import (
    SurveyInstitutionAgg,
    SurveyInstitutionQuestionGroupQuestionKeyCorrectAnsAgg,
    SurveyInstitutionQuestionGroupQuestionKeyAgg,
    SurveyInstitutionQuestionGroupGenderAgg,
    SurveyInstitutionQuestionGroupAgg,
    SurveyBoundaryQuestionGroupAnsAgg,
    Question,
    SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg,
    SurveyBoundaryQuestionGroupQuestionKeyAgg,
    SurveyEBoundaryQuestionGroupGenderCorrectAnsAgg,
    SurveyEBoundaryQuestionGroupGenderAgg
)
from assessments import models as assess_models
from assessments.models import AnswerGroup_Institution, QuestionGroup
from django.db.models import Sum
from reports.models import Reports, Tracking
from reports.helpers import calc_stud_performance


class GPMathContestReport(BaseReport):
    parameters = ('gp_name', )
    def __init__(self, gp_name=None, report_from=None, report_to=None, **kwargs):
        self.gp_name = gp_name
        self.report_from = report_from
        self.report_to = report_to
        self.params = dict(gp_name=self.gp_name, report_from=self.report_from, report_to=self.report_to)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--gp_name', required=True)
        self.parser.add_argument('--report_from', required=True)
        self.parser.add_argument('--report_to', required=True)
        self._template_path = 'GPMathContestReport.html'
        self._type = 'GPMathContestReport'
        self.sms_template ="2017-18 ರ ಜಿಕೆಏ ವರದಿ {} - ಅಕ್ಷರ"
        #super().__init__(**kwargs)

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.gp_name = arguments.gp_name
        self.report_from = arguments.report_from
        self.report_to = arguments.report_to
        self.params = dict(gp_name=self.gp_name, report_from=self.report_from, report_to=self.report_to)

    def get_data(self):
        gp = self.gp_name #"peramachanahalli"
        #import pdb; pdb.set_trace()
        dates = [self.report_from, self.report_to] # [2016-06-01, 2017-03-31]

        report_generated_on = datetime.datetime.now().date().strftime('%d-%m-%Y')

        try:
            gp_obj = ElectionBoundary.objects.get(const_ward_name=gp, const_ward_type_id='GP') # Take the GP from db
        except ElectionBoundary.DoesNotExist:
            raise ValueError("Gram panchayat '{}' is not found in the database.".format(self.gp_name))

        # block = gp_obj.parent.name           # Block name
        # district = gp_obj.parent.parent.name    # District name

        gp_schools = Institution.objects.filter(gp=gp_obj).count() # Number of schools in GP

        # Get the answergroup_institution from gp name and academic year
        aggregates = SurveyInstitutionQuestionGroupAgg.objects.filter(institution_id__gp=gp_obj,survey_id=2)\
                                                            .filter(yearmonth__gte = self.report_from)\
                                                            .filter(yearmonth__lte = self.report_to)
        gender_agg = SurveyInstitutionQuestionGroupGenderAgg.objects.filter(
                institution_id__gp=gp_obj, 
                survey_id=2, 
                yearmonth__gte=self.report_from,
                yearmonth__lte=self.report_to)        
        
        if not aggregates.exists():
            raise ValueError("No GP contests found for '{}' between {} and {}".format(gp, self.report_from, self.report_to))
        #import pdb; pdb.set_trace()
        block = aggregates.values_list('institution_id__admin2__name', flat=True).distinct()[0]
        district = aggregates.values_list('institution_id__admin1__name', flat=True).distinct()[0]
        num_boys = gender_agg.filter(gender='Male').aggregate(Sum('num_assessments'))['num_assessments__sum']
        num_girls = gender_agg.filter(gender='Female').aggregate(Sum('num_assessments'))['num_assessments__sum']
        number_of_students = num_boys + num_girls
        male_correct_ans_per_gp = SurveyEBoundaryQuestionGroupGenderCorrectAnsAgg.objects.filter(
            eboundary_id=gp_obj, survey_id=2)\
            .filter(yearmonth__gte = self.report_from)\
            .filter(yearmonth__lte = self.report_to)\
            .filter(gender='Male')\
            .aggregate(male_correct=Sum('num_assessments'))
        female_correct_ans_per_gp = SurveyEBoundaryQuestionGroupGenderCorrectAnsAgg.objects.filter(
            eboundary_id=gp_obj, survey_id=2)\
            .filter(yearmonth__gte = self.report_from)\
            .filter(yearmonth__lte = self.report_to)\
            .filter(gender='Female')\
            .aggregate(female_correct=Sum('num_assessments'))
        male_total_ans_per_gp = SurveyEBoundaryQuestionGroupGenderAgg.objects.filter(
            eboundary_id=gp_obj, survey_id=2)\
            .filter(yearmonth__gte = self.report_from)\
            .filter(yearmonth__lte = self.report_to)\
            .filter(gender='Male')\
            .aggregate(male_total=Sum('num_assessments'))
        female_total_ans_per_gp = SurveyEBoundaryQuestionGroupGenderAgg.objects.filter(
            eboundary_id=gp_obj, survey_id=2)\
            .filter(yearmonth__gte = self.report_from)\
            .filter(yearmonth__lte = self.report_to)\
            .filter(gender='Female')\
            .aggregate(female_total=Sum('num_assessments'))
        #import pdb; pdb.set_trace()

        male_total = male_total_ans_per_gp['male_total']
        female_total =  female_total_ans_per_gp['female_total']
        male_correct = male_correct_ans_per_gp['male_correct']
        female_correct = female_correct_ans_per_gp['female_correct']
        if male_total is None:
            male_total = 0
        if male_correct is None:
            male_correct = 0
        if female_total is None:
            female_total =0
        if female_correct is None:
            female_correct = 0
        male_zero_ans_per_gp = int(male_total) - int(male_correct)
        female_zero_ans_per_gp = int(female_total) - int(female_correct)
        # conditions = AGI.values_list('institution__name', 'questiongroup__name').distinct()
        # contests = list(AGI.values_list('answers__question__key', flat=True).distinct())
        # contests.pop(contests.index('Gender'))
        # schools = []
        # scores = {}
        
        # for school, qgroup in conditions:
        #     school_ag = AGI.filter(institution__name=school, questiongroup__name=qgroup)
        #     for contest in contests:
        #         percent = []
        #         for ag in school_ag:
        #             num_q = ag.answers.filter(question__key=contest).count()
        #             if num_q == 0:
        #                 continue

        #             # This was the original logic for generating GP contest report
        #             # In July, the logic has been changed to the block below this
        #             # block.
        #             # 
        #             # answered = ag.answers.filter(question__key=contest, answer='Yes').count()
        #             # mark = (answered/num_q)*100

        #             # The second logic we used in July
        #             # total_students_appeared = school_ag.count()
        #             # answered = 0
        #             # for s in school_ag:
        #             #     if s.answers.filter(
        #             #         question__key=contest, answer='Yes'
        #             #     ).exists():
        #             #         answered += 1
        #             # mark = (answered / total_students_appeared) * 100

        #             # New logic from Nagraj & Vaijayanthi
        #             total_students_appeared = school_ag.count()
        #             answered = 0
        #             for s in school_ag:
        #                 total_questions = s.answers.filter(
        #                     question__key=contest
        #                 ).count()
        #                 correct_answers = s.answers.filter(
        #                     question__key=contest,
        #                     answer='Yes'
        #                 ).count()
        #                 if total_questions == correct_answers:
        #                     answered += 1
        #             mark = (answered / total_students_appeared) * 100

        #             try:
        #                 scores[ag.id]['mark'].append(mark)
        #             except KeyError:
        #                 scores[ag.id] = dict(mark=[], gender=ag.answers.get(question__key='Gender').answer)
        #                 scores[ag.id]['mark'].append(mark)
        #             percent.append(mark)

        #         if len(percent) == 0:
        #             continue
        #         details = dict(school=school, grade=qgroup)
        #         details['contest'] = contest
        #         details['percent'] = sum(percent)/len(percent)
        #         schools.append(details)

        # # Calculate the perfomance of students
        # score_100, score_zero = calc_stud_performance(scores)

        # contest_list = [i['contest'] for i in schools]
        # schools_out = []
        # out= []

        # for item in schools:
        #     if not item['school'] in schools_out:
        #         schools_out.append(item['school'])
        #         out.append({'school':item['school'],
        #                     'grades':[{
        #                         'name':item['grade'],
        #                         'values':[{'contest':item['contest'],'count':round(item['percent'], 2) }]}]
        #         })
        #     else:
        #         for o in out:
        #             if o['school']==item['school']:
        #                 gradeExist= False
        #                 for grade in o['grades']:
        #                     if item['grade'] == grade['name']:
        #                         gradeExist = True
        #                         grade['values'].append({'contest':item['contest'],'count':round(item['percent'], 2) })
        #                 if not gradeExist:
        #                     o['grades'].append({'name':item['grade'],'values':[{'contest':item['contest'],'count':round(item['percent'], 2) }]})

        # We dont need Other Areas
        #Combine data to get the 'Other Areas' contest
        # for i in out:
        #     for grade in i['grades']:
        #         count = 0
        #         num = 0
        #         for value in grade['values']:
        #             if value['contest'] not in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']:
        #                 count += value['count']
        #                 num += 1
        #         grade['values']  = [k for k in grade['values'] if k['contest'] in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']]
        #         grade['values'].append(dict(contest='Other Areas', count=round(count/num, 2)))

        schools_out = self.get_school_data(gp_obj,dates)
        formatted_schools_out = self.format_schools_data(schools_out)
        survey = self.getHouseholdSurvey(gp_obj, dates)
        self.data =  {
            'gp_name': gp.title(),\
            'academic_year':'{} - {}'.format(format_academic_year(self.report_from), format_academic_year(self.report_to)),\
            'block':block,\
            'district':district.title(),\
            'no_schools_gp':gp_schools,\
            'no_students':number_of_students,\
            'today':report_generated_on,\
            'boys':num_boys,\
            'girls':num_girls,\
            'schools':formatted_schools_out,\
            'score_100':female_correct+male_correct,\
            'score_zero':male_zero_ans_per_gp+ female_zero_ans_per_gp,\
            'girls_zero':female_zero_ans_per_gp,\
            'boys_zero':male_zero_ans_per_gp,\
            'boys_100':male_correct,\
            'girls_100':female_correct,\
            'survey':survey}
        return self.data

    def format_schools_data(self,schools):
        schools_out = []
        out= []

        for item in schools:
            if not item['school'] in schools_out:
                schools_out.append(item['school'])
                out.append({'school':item['school'],
                            'grades':[{
                                'name':item['grade'],
                                'values':[{'contest':item['contest'],'count':round(item['percent'], 2) }]}]
                })
            else:
                for o in out:
                    if o['school']==item['school']:
                        gradeExist= False
                        for grade in o['grades']:
                            if item['grade'] == grade['name']:
                                gradeExist = True
                                grade['values'].append({'contest':item['contest'],'count':round(item['percent'], 2) })
                        if not gradeExist:
                            o['grades'].append({'name':item['grade'],'values':[{'contest':item['contest'],'count':round(item['percent'], 2) }]})

        # for i in out:
        #     for grade in i['grades']:
        #         count = 0
        #         num = 0
        #         for value in grade['values']:
        #             if value['contest'] not in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']:
        #                 count += value['count']
        #                 num += 1
        #         grade['values']  = [k for k in grade['values'] if k['contest'] in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']]
        #         grade['values'].append(dict(contest='Other Areas', count=round(count/num, 2)))
        return out
    def get_school_data(self, gp, dates):
        correct_answers_agg = SurveyInstitutionQuestionGroupQuestionKeyCorrectAnsAgg.objects.filter(survey_id=2, institution_id__gp=gp, yearmonth__range=dates)\
            .values('question_key', 'questiongroup_id', 'institution_id', 'num_assessments')\
            .annotate(total = Sum('num_assessments'))
        total_assessments = SurveyInstitutionQuestionGroupQuestionKeyAgg.objects.filter(survey_id=2, institution_id__gp=gp, yearmonth__range=dates)\
            .values('question_key', 'questiongroup_id', 'questiongroup_name', 'institution_id', 'num_assessments')\
            .annotate(Sum('num_assessments'))
        schools = []
        for each_row in total_assessments:
            sum_total = each_row['num_assessments__sum']
            percent = 0
            total = 0
            total_correct_answers = 0
            try:
                sum_correct_ans = correct_answers_agg.filter(question_key=each_row['question_key'])\
                    .filter(institution_id=each_row['institution_id'])\
                    .get(questiongroup_id=each_row['questiongroup_id'])        
                if sum_total is not None:
                    total = sum_total
                if sum_correct_ans is None or sum_correct_ans['total'] is None:
                    total_correct_answers = 0
                else:
                    total_correct_answers = sum_correct_ans['total']
            except Exception as e:
                pass
            
            if total is not None and total > 0:
                percent = total_correct_answers/total * 100
            details = dict(school=Institution.objects.get(id=each_row['institution_id']).name, grade=each_row['questiongroup_name'])
            details['contest'] = each_row['question_key']
            details['percent'] = percent
            schools.append(details)
        return schools

    # def getHouseholdServey(self,gp_obj,date_range):
    #     #Husehold Survey
    #     a = AnswerGroup_Institution.objects.filter(institution__gp=gp_obj, date_of_visit__range=date_range, questiongroup_id__in=[18, 20])

    #     questions = QuestionGroup.objects.get(id=18).questions.filter(id__in=[269, 144, 145, 138])

    #     total_response = a.count()

    #     HHSurvey = []

    #     for i in questions:
    #         count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
    #         count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
    #         HHSurvey.append({'text':i.question_text,'percentage': round((count/total_response)*100, 2)})

    #     return HHSurvey

class GPMathContestReportSummarized(BaseReport):
    parameters = ('gp_name', )
    def __init__(self, gp_name=None, report_from=None, report_to=None, **kwargs):
        self.gp_name = gp_name
        self.report_from = report_from
        self.report_to = report_to
        self.params = dict(gp_name=self.gp_name, report_from=self.report_from, report_to=self.report_to)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--gp_name', required=True)
        self.parser.add_argument('--report_from', required=True)
        self.parser.add_argument('--report_to', required=True)
        self._template_path = 'GPMathContestReportSummarized.html'
        self._type = 'GPMathContestReportSummarized'
        self.sms_template ="2017-18 ರ ಜಿಕೆಏ ವರದಿ {} - ಅಕ್ಷರ"
        super().__init__(**kwargs)

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.gp_name = arguments.gp_name
        self.report_from = arguments.report_from
        self.report_to = arguments.report_to
        self.params = dict(gp_name=self.gp_name, report_from=self.report_from, report_to=self.report_to)

    def get_data(self):
        gp = self.gp_name #"peramachanahalli"
        dates = [self.report_from, self.report_to] # [2016-06-01, 2017-03-31]

        report_generated_on = datetime.datetime.now().date().strftime('%d-%m-%Y')

        try:
            gp_obj = ElectionBoundary.objects.get(const_ward_name=gp, const_ward_type_id='GP') # Take the GP from db
        except ElectionBoundary.DoesNotExist:
            raise ValueError("Gram panchayat '{}' is not found in the database.".format(self.gp_name))

        # block = gp_obj.parent.name           # Block name
        # district = gp_obj.parent.parent.name    # District name

        gp_schools = Institution.objects.filter(gp=gp_obj).count() # Number of schools in GP

        # Get the answergroup_institution from gp name and academic year
        AGI = AnswerGroup_Institution.objects.filter(institution__gp=gp_obj, date_of_visit__range = dates, respondent_type_id='CH', questiongroup__survey_id=2)
        if not AGI.exists():
            raise ValueError("No GP contests found for '{}' between {} and {}".format(gp, self.report_from, self.report_to))

        block = AGI.values_list('institution__admin2__name', flat=True).distinct()[0]
        district = AGI.values_list('institution__admin1__name', flat=True).distinct()[0]
        num_boys = AGI.filter(answers__question__key='Gender', answers__answer='Male').count()
        num_girls = AGI.filter(answers__question__key='Gender', answers__answer='Female').count()
        number_of_students = num_boys + num_girls

        conditions = AGI.values_list('institution__name', 'questiongroup__name').distinct()
        contests = list(AGI.values_list('answers__question__key', flat=True).distinct())
        contests.pop(contests.index('Gender'))
        schools = []
        scores = {}

        for school, qgroup in conditions:
            school_ag = AGI.filter(institution__name=school, questiongroup__name=qgroup)
            for contest in contests:
                percent = []
                for ag in school_ag:
                    num_q = ag.answers.filter(question__key=contest).count()
                    if num_q == 0:
                        continue

                    # This was the original logic for generating GP contest report
                    # In July, the logic has been changed to the block below this
                    # block.
                    # 
                    # answered = ag.answers.filter(question__key=contest, answer='Yes').count()
                    # mark = (answered/num_q)*100

                    total_students_appeared = school_ag.count()
                    answered = 0
                    for s in school_ag:
                        if s.answers.filter(
                            question__key=contest, answer='Yes'
                        ).exists():
                            answered += 1
                    mark = (answered / total_students_appeared) * 100

                    try:
                        scores[ag.id]['mark'].append(mark)
                    except KeyError:
                        scores[ag.id] = dict(mark=[], gender=ag.answers.get(question__key='Gender').answer)
                        scores[ag.id]['mark'].append(mark)
                    percent.append(mark)

                if len(percent) == 0:
                    continue
                details = dict(school=school, grade=qgroup)
                details['contest'] = contest
                details['percent'] = sum(percent)/len(percent)
                schools.append(details)

        # Calculate the perfomance of students
        score_100, score_zero = calc_stud_performance(scores)

        contest_list = [i['contest'] for i in schools]
        schools_out = []
        out= []

        for item in schools:
            if not item['school'] in schools_out:
                schools_out.append(item['school'])
                out.append({'school':item['school'],
                            'grades':[{
                                'name':item['grade'],
                                'values':[{'contest':item['contest'],'count':round(item['percent'], 2) }]}]
                })
            else:
                for o in out:
                    if o['school']==item['school']:
                        gradeExist= False
                        for grade in o['grades']:
                            if item['grade'] == grade['name']:
                                gradeExist = True
                                grade['values'].append({'contest':item['contest'],'count':round(item['percent'], 2) })
                        if not gradeExist:
                            o['grades'].append({'name':item['grade'],'values':[{'contest':item['contest'],'count':round(item['percent'], 2) }]})

        #Combine data to get the 'Other Areas' contest
        # for i in out:
        #     for grade in i['grades']:
        #         count = 0
        #         num = 0
        #         for value in grade['values']:
        #             if value['contest'] not in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']:
        #                 count += value['count']
        #                 num += 1
        #         grade['values']  = [k for k in grade['values'] if k['contest'] in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']]
        #         grade['values'].append(dict(contest='Other Areas', count=round(count/num, 2)))


        #GPC Gradewise data
        gpc_grades = {'Class 4 Assessment':{}, 'Class 5 Assessment':{}, 'Class 6 Assessment':{}}
        for school in out:
            for grade in school['grades']:
                for value in grade['values']:
                    try:
                        gpc_grades[grade['name']][value['contest']]+=value['count']
                    except KeyError:
                        gpc_grades[grade['name']][value['contest']]=value['count']
        gradewise_gpc = []
        for grade, values in gpc_grades.items():
            for j ,k in values.items():
                values[j] = round(k/len(out), 2)
            gradewise_gpc.append({'grade':grade, 'values':[{'contest':contest, 'score':score} for contest,score in values.items()]})

        survey = self.getHouseholdServey(gp_obj, dates)

        self.data =  {'gp_name': gp.title(), 'academic_year':'{} - {}'.format(format_academic_year(self.report_from), format_academic_year(self.report_to)), 'block':block, 'district':district.title(),'no_schools_gp':gp_schools,'no_students':number_of_students,'today':report_generated_on,'boys':num_boys,'girls':num_girls,'schools':gradewise_gpc,'cs':contest_list,'score_100':score_100,'score_zero':score_zero,'girls_zero':girls_zero,'boys_zero':boys_zero,'boys_100':boys_100,'girls_100':girls_100, 'survey':survey}
        return self.data

    # def getHouseholdServey(self,gp_obj,date_range):
    #     #Husehold Survey
    #     a = AnswerGroup_Institution.objects.filter(institution__gp=gp_obj, date_of_visit__range=date_range, questiongroup_id__in=[18, 20])

    #     questions = QuestionGroup.objects.get(id=18).questions.filter(id__in=[269, 144, 145, 138])

    #     total_response = a.count()

    #     HHSurvey = []

    #     for i in questions:
    #         count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
    #         count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
    #         HHSurvey.append({'text':i.question_text,'percentage': round((count/total_response)*100, 2)})

    #     return HHSurvey
