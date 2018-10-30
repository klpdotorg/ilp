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

class DistrictReport(BaseReport):
    parameters = ('district_name', )
    def __init__(self, district_name=None, report_from=None, report_to=None, **kwargs):
        self.district_name = district_name
        self.report_from = report_from
        self.report_to = report_to
        self.params = dict(district_name=self.district_name, report_from=self.report_from, report_to=self.report_to)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--district_name', required=True)
        self.parser.add_argument('--report_from', required=True)
        self.parser.add_argument('--report_to', required=True)
        self._template_path = 'DistrictReport.html'
        self._type = 'DistrictReport'
        self.sms_template ="2017-18 ರ ಜಿಕೆಏ ವರದಿ {} - ಅಕ್ಷರ"
        super().__init__(**kwargs)

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.district_name = arguments.district_name
        self.report_from = arguments.report_from
        self.report_to = arguments.report_to
        self.params = dict(district_name=self.district_name, report_from=self.report_from, report_to=self.report_to)

   
    def get_data(self):
        # import pdb; pdb.set_trace()
        dates = [self.report_from, self.report_to] # [2016-06, 2017-03]
        report_generated_on = datetime.datetime.now().date().strftime('%d-%m-%Y')

        try:
            district = Boundary.objects.get(name=self.district_name, boundary_type__char_id='SD')
        except Boundary.DoesNotExist:
            raise ValueError("District '{}' cannot be found in the database".format(self.district_name))

        num_schools_in_block, num_boys, num_girls, number_of_students, num_contests = self.get_basic_boundary_data(
            district, 'district',
            self.report_from, 
            self.report_to)
        num_gp = district.institution_admin1.exclude(gp=None).values_list('gp__id',flat=True).distinct().count()
        
        block_gpc_data = self.get_childboundary_GPC_agg(district,'block',dates)
        gpc_blocks = self.format_block_data(block_gpc_data)
        gka, gka_blocks = self.getGKAData(district, dates)
        household = self.getHouseholdSurvey(district, dates)

        #GPC Gradewise data
        gpc_district_gradewise_percent = self.get_boundary_gpc_gradewise_agg(district, self.report_from, self.report_to)
       
        self.data = {'academic_year':'{} - {}'.format(format_academic_year(self.report_from), format_academic_year(self.report_to)), 'today':report_generated_on, 'district':self.district_name.title(), 'no_schools':num_schools_in_block, 
        'gka':gka, 'gka_blocks':gka_blocks,'gpc_blocks':gpc_blocks, 'household':household, 'num_boys':num_boys, 'num_girls':num_girls, 'num_students':number_of_students, 'num_contests':num_contests, 'gpc_grades':gpc_district_gradewise_percent, 'num_gp':num_gp}
        print(self.data)
        return self.data

  

    def format_block_data(self, blocks):
        blocks_out = []
        out= []

        for item in blocks:
            if not item['block'] in blocks_out:
                blocks_out.append(item['block'])
                out.append({'block':item['block'],
                            'grades':[{
                                'name':item['grade'],
                                'values':[{'contest':item['contest'],'count':round(item['percent'], 2) }]}]
                })
            else:
                for o in out:
                    if o['block']==item['block']:
                        gradeExist= False
                        for grade in o['grades']:
                            if item['grade'] == grade['name']:
                                gradeExist = True
                                grade['values'].append({'contest':item['contest'],'count':round(item['percent'], 2) })
                        if not gradeExist:
                            o['grades'].append({'name':item['grade'],'values':[{'contest':item['contest'],'count':round(item['percent'], 2) }]})

        return out


''' Exactly like DistrictReport except instead of returning gpc_blocks we are just
returning gpc_gradewise_percent. '''
class DistrictReportSummarized(DistrictReport):
    parameters = ('district_name', )
    def __init__(self, district_name=None, report_from=None, report_to=None, **kwargs):
        super().__init__(**kwargs)
        self.district_name = district_name
        self.report_from = report_from
        self.report_to = report_to
        self.params = dict(district_name=self.district_name, report_from=self.report_from, report_to=self.report_to)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--district_name', required=True)
        self.parser.add_argument('--report_from', required=True)
        self.parser.add_argument('--report_to', required=True)
        self._template_path = 'DistrictReportSummarized.html'
        self._type = 'DistrictReportSummarized'
        self.sms_template ="2017-18 ರ ಜಿಕೆಏ ವರದಿ {} - ಅಕ್ಷರ"
        

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.district_name = arguments.district_name
        self.report_from = arguments.report_from
        self.report_to = arguments.report_to
        self.params = dict(district_name=self.district_name, report_from=self.report_from, report_to=self.report_to)

    def get_data(self):
        dates = [self.report_from, self.report_to] # [2016-06-01, 2017-03-31]
        report_generated_on = datetime.datetime.now().date().strftime('%d-%m-%Y')
        try:
            district = Boundary.objects.get(name=self.district_name, boundary_type__char_id='SD')
        except Boundary.DoesNotExist:
            raise ValueError("District '{}' cannot be found in the database".format(self.district_name))

        num_schools, num_boys, num_girls, number_of_students, num_contests,= self.get_basic_boundary_data(
            district, 'district',
            self.report_from, 
            self.report_to)
        num_gp = district.institution_admin1.exclude(gp=None).values_list('gp__id',flat=True).distinct().count()


        gka, gka_blocks = self.getGKAData(district, dates)

        household = self.getHouseholdSurvey(district, dates)

        #GPC Gradewise data
        gpc_district_gradewise_percent = self.get_boundary_gpc_gradewise_agg(district, self.report_from, self.report_to)

        self.data = {'academic_year':'{} - {}'.format(format_academic_year(self.report_from),format_academic_year(self.report_to)),\
                    'today':report_generated_on,\
                    'district':self.district_name.title(),\
                    'gka':gka,\
                    'gka_blocks':gka_blocks,\
                    'no_schools':num_schools,\
                    'gpc_blocks':gpc_district_gradewise_percent,\
                    'household':household,\
                    'num_boys':num_boys,\
                    'num_girls':num_girls,\
                    'num_students':number_of_students,\
                    'num_contests':num_contests,\
                    'num_gp':num_gp}
        return self.data
