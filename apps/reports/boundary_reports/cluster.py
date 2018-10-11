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

        schools_data = self.get_school_data(cluster, dates)
        schools = self.format_schools_data(schools_data)
        gka = self.getGKAData(cluster, dates)

        household = self.getHouseholdSurvey(cluster,dates)

        self.data = {'cluster':self.cluster_name.title(), 'academic_year':'{} - {}'.format(format_academic_year(self.report_from), format_academic_year(self.report_to)), 'block':self.block_name.title(), 'district':self.district_name.title(), 'no_schools':num_schools, 'today':report_generated_on, 'gka':gka, 'household':household, 'schools':schools, 'num_boys':num_boys, 'num_girls':num_girls, 'num_students':number_of_students, 'num_contests':num_contests}
        return self.data

    def get_school_data(self, cluster, dates):
        correct_answers_agg = SurveyInstitutionQuestionGroupQuestionKeyCorrectAnsAgg.objects.filter(survey_id=2, institution_id__admin3=cluster, yearmonth__range=dates)\
            .values('question_key', 'questiongroup_id', 'institution_id', 'num_assessments')\
            .annotate(total = Sum('num_assessments'))
        total_assessments = SurveyInstitutionQuestionGroupQuestionKeyAgg.objects.filter(survey_id=2, institution_id__admin3=cluster, yearmonth__range=dates)\
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
                print(e)
            
            if total is not None and total > 0:
                percent = total_correct_answers/total * 100
            #import pdb; pdb.set_trace()
            details = dict(school=Institution.objects.get(id=each_row['institution_id']).name, grade=each_row['questiongroup_name'])
            details['contest'] = each_row['question_key']
            details['percent'] = percent
            schools.append(details)
        return schools

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
        schools_data = self.get_school_data(cluster, dates)
        schools = self.format_schools_data(schools_data)

        gka = self.getGKAData(cluster, dates)

        household = self.getHouseholdSurvey(cluster,dates)

        #GPC Gradewise data
        gpc_grades = {'Class 4 Assessment':{}, 'Class 5 Assessment':{}, 'Class 6 Assessment':{}}
        for school in schools:
            for grade in school['grades']:
                for value in grade['values']:
                    try:
                        gpc_grades[grade['name']][value['contest']]+=value['count']
                    except KeyError:
                        gpc_grades[grade['name']][value['contest']]=value['count']
        gradewise_gpc = []
        for grade, values in gpc_grades.items():
            for j ,k in values.items():
                values[j] = round(k/len(schools), 2)
            gradewise_gpc.append({'grade':grade, 'values':[{'contest':contest, 'score':score} for contest,score in values.items()]})

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

   