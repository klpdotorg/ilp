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

from assessments.models import (
    SurveyInstitutionAgg,
    SurveyInstitutionQuestionGroupQuestionKeyCorrectAnsAgg,
    SurveyInstitutionQuestionGroupGenderCorrectAnsAgg,
    SurveyInstitutionQuestionGroupQuestionKeyAgg,
    SurveyInstitutionQuestionGroupGenderAgg,
    SurveyInstitutionQuestionGroupAgg,
    SurveyBoundaryQuestionGroupAnsAgg,
    Question,
    SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg,
    SurveyBoundaryQuestionGroupQuestionKeyAgg
)
from assessments import models as assess_models
from assessments.models import AnswerGroup_Institution, QuestionGroup
from django.db.models import Sum
from reports.models import Reports, Tracking
from reports.helpers import calc_stud_performance

class SchoolReport(BaseReport):
    parameters = ('school_code', )
    def __init__(self, school_code=None, report_from=None, report_to=None, **kwargs):
        super().__init__(**kwargs)
        self.school_code = school_code
        self.report_from = report_from
        self.report_to = report_to
        self.params = dict(school_code=self.school_code, report_from=self.report_from, report_to=self.report_to)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--school_code', required=True)
        self.parser.add_argument('--report_from', required=True)
        self.parser.add_argument('--report_to', required=True)
        self._template_path = 'SchoolReport.html'
        self._type = 'SchoolReport'
        self.sms_template ="2017-18 ರ ಜಿಕೆಏ ವರದಿ {} - ಅಕ್ಷರ"

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.school_code = arguments.school_code
        self.report_from = arguments.report_from
        self.report_to = arguments.report_to
        self.params = dict(school_code=self.school_code, report_from=self.report_from, report_to=self.report_to)

    def get_data(self, neighbour_required=True):
        dates = [self.report_from, self.report_to] # [2016-06-01, 2017-03-31]

        report_generated_on = datetime.datetime.now().date().strftime('%d-%m-%Y')
        try:
            school_obj = Institution.objects.get(dise__school_code=self.school_code) # Take the school from db
        except Institution.DoesNotExist:
            raise ValueError("School with code '{}' cannot be found in the database".format(self.school_code))
        except AttributeError:
            raise("School '{}' does not have dise\n".format(self.school_code))

        try:
            gp = school_obj.gp.const_ward_name.title() # GP name
        except AttributeError:
            gp = 'Not Available'
        cluster = school_obj.admin3.name.title()         # Cluster name
        block = school_obj.admin2.name.title()           # Block name
        district = school_obj.admin1.name.title()    # District name

        aggregates = SurveyInstitutionQuestionGroupAgg.objects.filter(institution_id=school_obj,survey_id=2)\
                                                            .filter(yearmonth__gte = self.report_from)\
                                                            .filter(yearmonth__lte = self.report_to)
        gender_agg = SurveyInstitutionQuestionGroupGenderAgg.objects.filter(
                institution_id=school_obj, 
                survey_id=2, 
                yearmonth__gte=self.report_from,
                yearmonth__lte=self.report_to)        
        
        if not aggregates.exists():
            raise ValueError("No GP contests found for '{}' between {} and {}".format(gp, self.report_from, self.report_to))
        block = aggregates.values_list('institution_id__admin2__name', flat=True).distinct()[0]
        district = aggregates.values_list('institution_id__admin1__name', flat=True).distinct()[0]
        num_boys = gender_agg.filter(gender='Male').aggregate(Sum('num_assessments'))['num_assessments__sum']
        num_girls = gender_agg.filter(gender='Female').aggregate(Sum('num_assessments'))['num_assessments__sum']
        number_of_students = num_boys + num_girls

        schools = self.get_schools_data(school_obj, dates)

        # Calculate the perfomance of students
        male_total, female_total, male_correct, female_correct, male_zero_ans_per_gp, female_zero_ans_per_gp = \
            self.calculate_student_performance(school_obj, self.report_from, self.report_to)

        #contest_list = [i['contest'] for i in schools]

        out = self.format_schools_data(schools)

        if neighbour_required:
            neighbour_list = []
            # Get data for all schools in this GP
            neighbouring_schools_data = self.get_schools_data(school_obj.gp,dates)
            neighbours = self.format_schools_data(neighbouring_schools_data)
        else:
            neighbours = []

        self.data =  {'gp_name': gp,\
         'academic_year':'{} - {}'.format(format_academic_year(self.report_from), format_academic_year(self.report_to)),\
            'cluster':cluster,\
            'block':block,\
            'district':district,\
            'no_students':number_of_students,\
            'today':report_generated_on,\
            'boys':num_boys,\
            'girls':num_girls,\
            'schools':out,\
            'score_100':female_correct+male_correct,\
            'score_zero':male_zero_ans_per_gp+ female_zero_ans_per_gp,\
            'girls_zero':female_zero_ans_per_gp,\
            'boys_zero':male_zero_ans_per_gp,\
            'boys_100':male_correct,\
            'girls_100':female_correct,\
            'neighbours':neighbours}
        return self.data

