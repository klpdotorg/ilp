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
    SurveyEBoundaryQuestionGroupGenderAgg,
    SurveyEBoundaryElectionTypeCount
)
from assessments import models as assess_models
from assessments.models import AnswerGroup_Institution, QuestionGroup
from django.db.models import Sum
from reports.models import Reports, Tracking
from reports.helpers import calc_stud_performance


class GPMathContestReport(BaseReport):
    parameters = ('gp_code', )
    def __init__(self, gp_code=None, report_from=None, report_to=None, **kwargs):
       
        if gp_code is not None:
            self.gp_code = int(gp_code)
        else:
            self.gp_code=None
        self.report_from = report_from
        self.report_to = report_to
        self.params = dict(gp_code=self.gp_code, report_from=self.report_from, report_to=self.report_to)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--gp_code', required=True)
        self.parser.add_argument('--report_from', required=True)
        self.parser.add_argument('--report_to', required=True)
        self._template_path = 'GPMathContestReport.html'
        self._type = 'GPMathContestReport'
        self.sms_template ="2017-18 ರ ಜಿಕೆಏ ವರದಿ {} - ಅಕ್ಷರ"
        super().__init__(**kwargs)
        

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.gp_code = arguments.gp_code
        self.report_from = arguments.report_from
        self.report_to = arguments.report_to
        self.params = dict(gp_name=self.gp_name, report_from=self.report_from, report_to=self.report_to)

    def get_data(self):
        gp = self.gp_code #"peramachanahalli"
        #import pdb; pdb.set_trace()
        dates = [self.report_from, self.report_to] # [2016-06-01, 2017-03-31]

        report_generated_on = datetime.datetime.now().date().strftime('%d-%m-%Y')

        try:
            # gp_obj = ElectionBoundary.objects.get(const_ward_name=gp.capitalize(), const_ward_type_id='GP') # Take the GP from db
            gp_obj = ElectionBoundary.objects.get(id=gp, const_ward_type_id='GP') # Take the GP from db
        except ElectionBoundary.DoesNotExist:
            raise ValueError("Gram panchayat '{}' is not found in the database.".format(self.gp_code))
        gp_schools = Institution.objects.filter(gp=gp_obj).count() # Number of schools in GP

        block, district,num_boys, num_girls, number_of_students,\
                   male_total, female_total, male_correct, female_correct,\
                   male_zero_ans_per_gp, female_zero_ans_per_gp=\
                   self.get_basic_GP_data(gp_obj)

        formatted_schools_out = []
        gradewise_gpc=[]
        if self.generate_gp == "True" or self.generate_gp == True:
            schools_out = self.get_schools_data(gp_obj,dates)
            formatted_schools_out = self.format_boundary_data(schools_out)
            gradewise_gpc = self.get_boundary_gpc_gradewise_agg(gp_obj, self.report_from, self.report_to)
        
        survey = {}
        if self.generate_hh == "True" or self.generate_gp == True:
            try:
                survey = self.getHouseholdSurvey(gp_obj, dates)
            except:
                print("No household community survey data available for GP ", gp_obj.const_ward_name)

        num_contests_agg = SurveyEBoundaryElectionTypeCount.objects.filter(survey_id=2)\
                                               .filter(eboundary_id=gp_obj)\
                                               .filter(yearmonth__gte = self.report_from)\
                                               .filter(yearmonth__lte = self.report_to)\
                                               .filter(const_ward_type='GP')
        num_contests = 1
        if num_contests_agg.exists():
            num_contests = num_contests_agg.aggregate(Sum('electionboundary_count'))['electionboundary_count__sum']
        self.output =  {
            'gp_name': gp_obj.const_ward_name,\
            'academic_year':'{} - {}'.format(format_academic_year(self.report_from), format_academic_year(self.report_to)),\
            'block':block,\
            'district':district.title(),\
            'no_schools_gp':gp_schools,\
            'num_contests': num_contests,\
            'num_students':number_of_students,\
            'today':report_generated_on,\
            'num_boys':num_boys,\
            'num_girls':num_girls,\
            'overall_gradewise_perf': gradewise_gpc,\
            'gpc_child_boundaries':formatted_schools_out,\
            'score_100':female_correct+male_correct,\
            'score_zero':male_zero_ans_per_gp+ female_zero_ans_per_gp,\
            'girls_zero':female_zero_ans_per_gp,\
            'boys_zero':male_zero_ans_per_gp,\
            'boys_100':male_correct,\
            'girls_100':female_correct,\
            'household':survey,\
            'report_type': 'gp'}
        self.data = {**self.output, **self.common_data}
        return self.data

    def get_basic_GP_data(self, gp_obj):
        gp_schools = Institution.objects.filter(gp=gp_obj).count() # Number of schools in GP

        # Get the answergroup_institution from gp name and academic year
        aggregates = SurveyInstitutionQuestionGroupAgg.objects.filter(institution_id__gp=gp_obj,survey_id=self.gpcontest_survey_id)\
                                                            .filter(yearmonth__gte = self.report_from)\
                                                            .filter(yearmonth__lte = self.report_to)
        gender_agg = SurveyInstitutionQuestionGroupGenderAgg.objects.filter(
                institution_id__gp=gp_obj, 
                survey_id=2, 
                yearmonth__gte=self.report_from,
                yearmonth__lte=self.report_to)        
        
        if not aggregates.exists():
            raise ValueError("No GP contests found for '{}'-{} between {} and {}".format(gp_obj.const_ward_name,gp_obj.id, self.report_from, self.report_to))
        block = aggregates.values_list('institution_id__admin2__name', flat=True).distinct()[0]
        district = aggregates.values_list('institution_id__admin1__name', flat=True).distinct()[0]
        num_boys = gender_agg.filter(gender='Male').aggregate(Sum('num_assessments'))['num_assessments__sum']
        num_girls = gender_agg.filter(gender='Female').aggregate(Sum('num_assessments'))['num_assessments__sum']
        number_of_students=0
        if num_boys is not None and num_girls is not None:
            number_of_students = num_boys + num_girls
        male_correct_ans_per_gp = SurveyEBoundaryQuestionGroupGenderCorrectAnsAgg.objects.filter(
            eboundary_id=gp_obj, survey_id=self.gpcontest_survey_id)\
            .filter(yearmonth__gte = self.report_from)\
            .filter(yearmonth__lte = self.report_to)\
            .filter(gender='Male')\
            .aggregate(male_correct=Sum('num_assessments'))
        female_correct_ans_per_gp = SurveyEBoundaryQuestionGroupGenderCorrectAnsAgg.objects.filter(
            eboundary_id=gp_obj, survey_id=self.gpcontest_survey_id)\
            .filter(yearmonth__gte = self.report_from)\
            .filter(yearmonth__lte = self.report_to)\
            .filter(gender='Female')\
            .aggregate(female_correct=Sum('num_assessments'))
        male_total_ans_per_gp = SurveyEBoundaryQuestionGroupGenderAgg.objects.filter(
            eboundary_id=gp_obj, survey_id=self.gpcontest_survey_id)\
            .filter(yearmonth__gte = self.report_from)\
            .filter(yearmonth__lte = self.report_to)\
            .filter(gender='Male')\
            .aggregate(male_total=Sum('num_assessments'))
        female_total_ans_per_gp = SurveyEBoundaryQuestionGroupGenderAgg.objects.filter(
            eboundary_id=gp_obj, survey_id=self.gpcontest_survey_id)\
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

        return block, district,num_boys, num_girls, number_of_students,\
                male_total, female_total, male_correct, female_correct,\
                male_zero_ans_per_gp, female_zero_ans_per_gp 

 

class GPMathContestReportSummarized(GPMathContestReport):
    parameters = ('gp_code', )
    def __init__(self, gp_code=None, report_from=None, report_to=None, **kwargs):
        super().__init__(**kwargs)
        self.gp_code = gp_code
        self.report_from = report_from
        self.report_to = report_to
        self.params = dict(gp_code=self.gp_code, report_from=self.report_from, report_to=self.report_to)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--gp_code', required=True)
        self.parser.add_argument('--report_from', required=True)
        self.parser.add_argument('--report_to', required=True)
        self._template_path = 'GPMathContestReportSummarized.html'
        self._type = 'GPMathContestReportSummarized'
        self.sms_template ="2017-18 ರ ಜಿಕೆಏ ವರದಿ {} - ಅಕ್ಷರ"

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.gp_code = arguments.gp_code
        self.report_from = arguments.report_from
        self.report_to = arguments.report_to
        self.params = dict(gp_name=self.gp_name, report_from=self.report_from, report_to=self.report_to)

    def get_data(self):
        gp = self.gp_code #"peramachanahalli"
        dates = [self.report_from, self.report_to] # [2016-06-01, 2017-03-31]

        report_generated_on = datetime.datetime.now().date().strftime('%d-%m-%Y')

        try:
            gp_obj = ElectionBoundary.objects.get(id=gp, const_ward_type_id='GP') # Take the GP from db
        except ElectionBoundary.DoesNotExist:
            raise ValueError("Gram panchayat '{}' is not found in the database.".format(self.gp_code))

        gp_schools = Institution.objects.filter(gp=gp_obj).count() # Number of schools in GP
     
        block, district,num_boys, num_girls, number_of_students,\
                   male_total, female_total, male_correct, female_correct,\
                   male_zero_ans_per_gp, female_zero_ans_per_gp=\
                   self.get_basic_GP_data(gp_obj)
        gradewise_gpc = self.get_boundary_gpc_gradewise_agg(gp_obj, self.report_from, self.report_to)
        survey = self.getHouseholdSurvey(gp_obj, dates)
        self.output =  {
                        'gp_name': gp.title(),\
                        'academic_year':'{} - {}'.format(format_academic_year(self.report_from), format_academic_year(self.report_to)),\
                        'block':block,\
                        'district':district.title(),\
                        'no_schools_gp':gp_schools,\
                        'num_students':number_of_students,\
                        'today':report_generated_on,\
                        'boys':num_boys,\
                        'girls':num_girls,\
                        'overall_gradewise_perf':gradewise_gpc,\
                        'score_100':female_correct+male_correct,\
                        'score_zero':male_zero_ans_per_gp+ female_zero_ans_per_gp,\
                        'girls_zero':female_zero_ans_per_gp,\
                        'boys_zero':male_zero_ans_per_gp,\
                        'boys_100':male_correct,\
                        'girls_100':female_correct,\
                        'household':survey,\
                        'report_type': 'gpsummarized'}
        self.data = {**self.output, **self.common_data}
        return self.data

