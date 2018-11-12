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

class BlockReport(BaseReport):
    parameters = ('block_name', 'district_name')
    def __init__(self, block_name=None, district_name=None, report_from=None, report_to=None, **kwargs):
        self.block_name = block_name
        self.district_name = district_name
        self.report_from = report_from
        self.report_to = report_to
        self.params = dict(block_name=self.block_name, district_name=self.district_name, report_from=self.report_from, report_to=self.report_to)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--block_name', required=True)
        self.parser.add_argument('--district_name', required=True)
        self.parser.add_argument('--report_from', required=True)
        self.parser.add_argument('--report_to', required=True)
        self._template_path = 'BlockReport.html'
        self._type = 'BlockReport'
        self.sms_template ="2017-18 ರ ಜಿಕೆಏ ವರದಿ {} - ಅಕ್ಷರ"
        super().__init__(**kwargs)

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.block_name = arguments.block_name
        self.district_name = arguments.district_name
        self.report_from = arguments.report_from
        self.report_to = arguments.report_to
        self.params = dict(block_name=self.block_name, district_name=self.district_name, report_from=self.report_from, report_to=self.report_to)

    def get_data(self):
        dates = [self.report_from, self.report_to] # [201706,201803]
        report_generated_on = datetime.datetime.now().date().strftime('%d-%m-%Y')

        try:
            # Take the block from db
            block = Boundary.objects.get(name=self.block_name, parent__name=self.district_name, boundary_type__char_id='SB') 
        except Boundary.DoesNotExist:
            raise ValueError("Block '{}' cannot be found in the database".format(self.block_name))

        num_schools, num_boys, num_girls, number_of_students, num_contests = self.get_basic_boundary_data(
            block, 'block',
            self.report_from, 
            self.report_to)

        gpc_clusters = []
        gradewise_gpc = {}
        if self.generate_gp == 'True':
            cluster_gpc_data = self.get_childboundary_GPC_agg(block, 'cluster', dates)
            gpc_clusters = self.format_boundary_data(cluster_gpc_data)
            #GPC Gradewise data
            gradewise_gpc = self.get_boundary_gpc_gradewise_agg(block, self.report_from, self.report_to)

        gka = {}
        gka_clusters=[]
        if self.generate_gka == 'True':
            gka, gka_clusters = self.getGKAData(block, dates)
        
        household = {}
        if self.generate_hh == 'True':
            household = self.getHouseholdSurvey(block, dates)
        self.output = {'block':self.block_name.title(),\
                     'district':self.district_name.title(),\
                     'academic_year':'{} - {}'.format(format_academic_year(self.report_from), format_academic_year(self.report_to)),\
                     'today':report_generated_on,\
                     'no_schools':num_schools,\
                     'gka':gka,\
                     'gka_child_boundaries':gka_clusters,\
                     'overall_gradewise_perf': gradewise_gpc,\
                     'gpc_child_boundaries':gpc_clusters,\
                     'household':household,\
                     'num_boys':num_boys,\
                     'num_girls':num_girls,\
                     'num_students':number_of_students,\
                     'num_contests':num_contests,\
                     'report_type': 'block',\
                    }
        self.data = {**self.output, **self.common_data}
        return self.data
    
class BlockReportSummarized(BlockReport):
    parameters = ('block_name', 'district_name')
    def __init__(self, block_name=None, district_name=None, report_from=None, report_to=None, **kwargs):
        super().__init__(**kwargs)
        self.block_name = block_name
        self.district_name = district_name
        self.report_from = report_from
        self.report_to = report_to
        self.params = dict(block_name=self.block_name, district_name=self.district_name, report_from=self.report_from, report_to=self.report_to)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--block_name', required=True)
        self.parser.add_argument('--district_name', required=True)
        self.parser.add_argument('--report_from', required=True)
        self.parser.add_argument('--report_to', required=True)
        self._template_path = 'BlockReportSummarized.html'
        self._type = 'BlockReportSummarized'
        self.sms_template ="2017-18 ರ ಜಿಕೆಏ ವರದಿ {} - ಅಕ್ಷರ"

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.block_name = arguments.block_name
        self.district_name = arguments.district_name
        self.report_from = arguments.report_from
        self.report_to = arguments.report_to
        self.params = dict(block_name=self.block_name, district_name=self.district_name, report_from=self.report_from, report_to=self.report_to)

    def get_data(self):
        dates = [self.report_from, self.report_to] # [2016-06-01, 2017-03-31]
        report_generated_on = datetime.datetime.now().date().strftime('%d-%m-%Y')

        try:
            # Take the block from db
            block = Boundary.objects.get(name=self.block_name, parent__name=self.district_name, boundary_type__char_id='SB') 
        except Boundary.DoesNotExist:
            raise ValueError("Block '{}' cannot be found in the database".format(self.block_name))

        num_schools, num_boys, num_girls, number_of_students, num_contests = self.get_basic_boundary_data(
            block, 
            'block',
            self.report_from, 
            self.report_to)
        
    
        gka, gka_clusters = self.getGKAData(block, dates)

        household = self.getHouseholdSurvey(block, dates)

        #GPC Gradewise data
        gradewise_gpc = self.get_boundary_gpc_gradewise_agg(block, self.report_from, self.report_to)
        self.output = {
                        'block':self.block_name.title(),\
                        'district':self.district_name.title(),\
                        'academic_year':'{} - {}'.format(format_academic_year(self.report_from),\
                            format_academic_year(self.report_to)),\
                        'today':report_generated_on,\
                        'no_schools':num_schools,\
                        'gka':gka,\
                        'gka_child_boundaries':gka_clusters,\
                        'overall_gradewise_perf':gradewise_gpc,\
                        'household':household,\
                        'num_boys':num_boys,\
                        'num_girls':num_girls,\
                        'num_students':number_of_students,\
                        'num_contests':num_contests,
                        'report_type':'blocksummarized'
                    }
        self.data = {**self.output, **self.common_data}
        return self.data
