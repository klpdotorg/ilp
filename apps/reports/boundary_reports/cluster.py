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

class ClusterReport(BaseReport):
    parameters = ('cluster_name', 'block_name', 'district_name')
    def __init__(self, cluster_name=None, block_name=None, district_name=None, report_from=None, report_to=None, **kwargs):
        self.cluster_name = cluster_name
        self.block_name = block_name
        self.district_name = district_name
        self.report_from = report_from
        self.report_to = report_to
        self.params = dict(cluster_name=self.cluster_name, block_name=self.block_name, district_name=self.district_name, report_from=self.report_from, report_to=self.report_to)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--cluster_name', required=True)
        self.parser.add_argument('--block_name', required=True)
        self.parser.add_argument('--report_from', required=True)
        self.parser.add_argument('--report_to', required=True)
        self._template_path = 'ClusterReport.html'
        self._type = 'ClusterReport'
        self.sms_template ="2017-18 ರ ಜಿಕೆಏ ವರದಿ {} - ಅಕ್ಷರ"
        super().__init__(**kwargs)

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.cluster_name = arguments.cluster_name
        self.block_name = arguments.block_name
        self.district_name = arguments.district_name
        self.report_from = arguments.report_from
        self.report_to = arguments.report_to
        self.params = dict(cluster_name=self.cluster_name, block_name=self.block_name, district_name=self.district_name, report_from=self.report_from, report_to=self.report_to)

    def get_data(self):
        dates = [self.report_from, self.report_to] # [201606,201702]
        report_generated_on = datetime.datetime.now().date().strftime('%d-%m-%Y')
        try:
             # Take the cluster from db
            cluster = Boundary.objects.get(name=self.cluster_name, parent__name=self.block_name, parent__parent__name=self.district_name, boundary_type__char_id='SC')
        except Boundary.DoesNotExist:
            raise ValueError("Cluster '{}' cannot be found in the database".format(self.cluster_name))

        num_schools, num_boys, num_girls, number_of_students, num_contests = self.get_basic_boundary_data(
            cluster, 
            'cluster',
            self.report_from, 
            self.report_to)

        schools_data = self.get_schools_data(cluster, dates)
        schools = self.format_schools_data(schools_data)
        gka = self.getGKAData(cluster, dates)
        #GPC Gradewise data
        gradewise_gpc = self.get_boundary_gpc_gradewise_agg(cluster, self.report_from, self.report_to)
        household = self.getHouseholdSurvey(cluster,dates)

        self.data = {'cluster':self.cluster_name.title(),\
                       'academic_year':'{} - {}'.format(format_academic_year(self.report_from), format_academic_year(self.report_to)),\
                       'block':self.block_name.title(),\
                       'district':self.district_name.title(),\
                       'no_schools':num_schools, 'today':report_generated_on,\
                       'gka':gka,\
                       'household':household,\
                       'overall_cluster_performance': gradewise_gpc,\
                       'schools':schools,\
                       'num_boys':num_boys,\
                       'num_girls':num_girls,\
                       'num_students':number_of_students,\
                       'num_contests':num_contests}
        return self.data

   
    def getGKAData(self, cluster, date_range):
        GKA = SurveyBoundaryQuestionGroupAnsAgg.objects.filter(boundary_id=cluster)\
            .filter(yearmonth__range=date_range)\
            .filter(survey_id=11)
        if not GKA.exists():
            raise ValueError("No GKA data for '{}' between {} and {}.".format(self.cluster_name, self.report_from, self.report_to))
        
        gka = {
            'teachers_trained': self.getTeacherTrainedPercent(GKA, date_range),
            'kit_usage': self.getKitUsagePercent(GKA,date_range),
            'group_work': self.getGroupWorkPercent(GKA,date_range)
        }

        return gka
       

class ClusterReportSummarized(ClusterReport):
    parameters = ('cluster_name', 'block_name', 'district_name')
    def __init__(self, cluster_name=None, block_name=None, district_name=None, report_from=None, report_to=None, **kwargs):
        self.cluster_name = cluster_name
        self.block_name = block_name
        self.district_name = district_name
        self.report_from = report_from
        self.report_to = report_to
        self.params = dict(cluster_name=self.cluster_name, block_name=self.block_name, district_name=self.district_name, report_from=self.report_from, report_to=self.report_to)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--cluster_name', required=True)
        self.parser.add_argument('--block_name', required=True)
        self.parser.add_argument('--report_from', required=True)
        self.parser.add_argument('--report_to', required=True)
        self._template_path = 'ClusterReportSummarized.html'
        self._type = 'ClusterReportSummarized'
        self.sms_template ="2017-18 ರ ಜಿಕೆಏ ವರದಿ {} - ಅಕ್ಷರ"
        # super().__init__(**kwargs)

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.cluster_name = arguments.cluster_name
        self.block_name = arguments.block_name
        self.district_name = arguments.district_name
        self.report_from = arguments.report_from
        self.report_to = arguments.report_to
        self.params = dict(cluster_name=self.cluster_name, block_name=self.block_name, district_name=self.district_name, report_from=self.report_from, report_to=self.report_to)

    def get_data(self):
        dates = [self.report_from, self.report_to] # [201606, 201703]
        report_generated_on = datetime.datetime.now().date().strftime('%d-%m-%Y')
        try:
             # Take the cluster from db
            cluster = Boundary.objects.get(name=self.cluster_name, parent__name=self.block_name, parent__parent__name=self.district_name, boundary_type__char_id='SC')
        except Boundary.DoesNotExist:
            raise ValueError("Cluster '{}' cannot be found in the database".format(self.cluster_name))

        num_schools, num_boys, num_girls, number_of_students, num_contests = self.get_basic_boundary_data(
            cluster, 
            'cluster',
            self.report_from, 
            self.report_to)
        schools_data = self.get_schools_data(cluster, dates)
        schools = self.format_schools_data(schools_data)

        gka = self.getGKAData(cluster, dates)

        household = self.getHouseholdSurvey(cluster,dates)

        #GPC Gradewise data
        gradewise_gpc = self.get_boundary_gpc_gradewise_agg(cluster, self.report_from, self.report_to)
        # gpc_grades = {'Class 4 Assessment':{}, 'Class 5 Assessment':{}, 'Class 6 Assessment':{}}
        # for school in schools:
        #     for grade in school['grades']:
        #         for value in grade['values']:
        #             try:
        #                 gpc_grades[grade['name']][value['contest']]+=value['count']
        #             except KeyError:
        #                 gpc_grades[grade['name']][value['contest']]=value['count']
        # gradewise_gpc = []
        # for grade, values in gpc_grades.items():
        #     for j ,k in values.items():
        #         values[j] = round(k/len(schools), 2)
        #     gradewise_gpc.append({'grade':grade, 'values':[{'contest':contest, 'score':score} for contest,score in values.items()]})

        self.data = {\
                        'cluster':self.cluster_name.title(),\
                        'academic_year':'{} - {}'.format(format_academic_year(self.report_from), format_academic_year(self.report_to)),\
                        'block':self.block_name.title(),\
                        'district':self.district_name.title(),\
                        'no_schools':num_schools,\
                        'today':report_generated_on,\
                        'gka':gka, 'household':household,\
                        'schools':gradewise_gpc,\
                        'num_boys':num_boys,\
                        'num_girls':num_girls,\
                        'num_students':number_of_students,\
                        'num_contests':num_contests}
        return self.data

   