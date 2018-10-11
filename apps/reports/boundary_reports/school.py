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

class SchoolReport(BaseReport):
    parameters = ('school_code', )
    def __init__(self, school_code=None, report_from=None, report_to=None, **kwargs):
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
        super().__init__(**kwargs)

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

        AGI = AnswerGroup_Institution.objects.filter(institution=school_obj, date_of_visit__range = dates, respondent_type_id='CH', questiongroup__survey_id=2)

        if not AGI.exists():
            raise ValueError("No GP contest data for '{}' between {} and {}".format(self.school_code, self.report_from, self.report_to))

        num_boys = AGI.filter(answers__question__key='Gender', answers__answer='Male').count()
        num_girls = AGI.filter(answers__question__key='Gender', answers__answer='Female').count()
        number_of_students = num_boys + num_girls

        schools,scores = self.get_school_data(AGI)

        # Calculate the perfomance of students
        score_100, score_zero = calc_stud_performance(scores)

        contest_list = [i['contest'] for i in schools]

        out = self.format_schools_data(schools)

        if neighbour_required:
            neighbour_list = []
            for i in Institution.objects.filter(gp=school_obj.gp):
                neighbour_agi = AnswerGroup_Institution.objects.filter(institution=i, date_of_visit__range = dates, respondent_type_id='CH', questiongroup__survey_id=2)
                neighbour_data, _ = self.get_school_data(neighbour_agi)
                neighbour_list += neighbour_data

            neighbours = self.format_schools_data(neighbour_list)
        else:
            neighbours = []

        self.data =  {'gp_name': gp, 'academic_year':'{} - {}'.format(format_academic_year(self.report_from), format_academic_year(self.report_to)), 'cluster':cluster, 'block':block, 'district':district,'no_students':number_of_students,'today':report_generated_on,'boys':num_boys,'girls':num_girls,'schools':out,'cs':contest_list,'score_100':score_100,'score_zero':score_zero,'girls_zero':girls_zero,'boys_zero':boys_zero,'boys_100':boys_100,'girls_100':girls_100, 'neighbours':neighbours}
        return self.data

    def get_school_data(self,answergroup):
        conditions = answergroup.values_list('institution__name', 'questiongroup__name').distinct()
        contests = list(answergroup.values_list('answers__question__key', flat=True).distinct())
        contests.pop(contests.index('Gender'))
        schools = []
        scores = {}

        for school, qgroup in conditions:
            school_ag = answergroup.filter(institution__name=school, questiongroup__name=qgroup)
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

                    # The second logic we used in July
                    # total_students_appeared = school_ag.count()
                    # answered = 0
                    # for s in school_ag:
                    #     if s.answers.filter(
                    #         question__key=contest, answer='Yes'
                    #     ).exists():
                    #         answered += 1
                    # mark = (answered / total_students_appeared) * 100

                    # The new logic proposed by Nagraj & Vaijayanthi
                    total_students_appeared = school_ag.count()
                    answered = 0
                    for s in school_ag:
                        total_questions = s.answers.filter(
                            question__key=contest
                        ).count()
                        correct_answers = s.answers.filter(
                            question__key=contest,
                            answer='Yes'
                        ).count()
                        if total_questions == correct_answers:
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

        return schools,scores

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


class SchoolReportSummarized(BaseReport):
    parameters = ('school_code', )
    def __init__(self, school_code=None, report_from=None, report_to=None, **kwargs):
        self.school_code = school_code
        self.report_from = report_from
        self.report_to = report_to
        self.params = dict(school_code=self.school_code, report_from=self.report_from, report_to=self.report_to)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--school_code', required=True)
        self.parser.add_argument('--report_from', required=True)
        self.parser.add_argument('--report_to', required=True)
        self._template_path = 'SchoolReportSummarized.html'
        self._type = 'SchoolReportSummarized'
        self.sms_template ="2017-18 ರ ಜಿಕೆಏ ವರದಿ {} - ಅಕ್ಷರ"
        super().__init__(**kwargs)

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

        AGI = AnswerGroup_Institution.objects.filter(institution=school_obj, date_of_visit__range = dates, respondent_type_id='CH', questiongroup__survey_id=2)

        if not AGI.exists():
            raise ValueError("No GP contest data for '{}' between {} and {}".format(self.school_code, self.report_from, self.report_to))

        num_boys = AGI.filter(answers__question__key='Gender', answers__answer='Male').count()
        num_girls = AGI.filter(answers__question__key='Gender', answers__answer='Female').count()
        number_of_students = num_boys + num_girls

        schools,scores = self.get_school_data(AGI)

        # Calculate the perfomance of students
        score_100, score_zero = calc_stud_performance(scores)

        contest_list = [i['contest'] for i in schools]

        out = self.format_schools_data(schools)

        if neighbour_required:
            neighbour_list = []
            for i in Institution.objects.filter(gp=school_obj.gp):
                neighbour_agi = AnswerGroup_Institution.objects.filter(institution=i, date_of_visit__range = dates, respondent_type_id='CH', questiongroup__survey_id=2)
                neighbour_data, _ = self.get_school_data(neighbour_agi)
                neighbour_list += neighbour_data

            neighbours = self.format_schools_data(neighbour_list)
        else:
            neighbours = []

        #GPC Gradewise data
        gpc_grades = {'Class 4 Assessment':{}, 'Class 5 Assessment':{}, 'Class 6 Assessment':{}}
        for school in neighbours:
            for grade in school['grades']:
                for value in grade['values']:
                    try:
                        gpc_grades[grade['name']][value['contest']]+=value['count']
                    except KeyError:
                        gpc_grades[grade['name']][value['contest']]=value['count']
        gradewise_gpc = []
        for grade, values in gpc_grades.items():
            for j ,k in values.items():
                values[j] = round(k/len(neighbours), 2)
            gradewise_gpc.append({'grade':grade, 'values':[{'contest':contest, 'score':score} for contest,score in values.items()]})

        self.data =  {'gp_name': gp, 'academic_year':'{} - {}'.format(format_academic_year(self.report_from), format_academic_year(self.report_to)), 'cluster':cluster, 'block':block, 'district':district,'no_students':number_of_students,'today':report_generated_on,'boys':num_boys,'girls':num_girls,'schools':out,'cs':contest_list,'score_100':score_100,'score_zero':score_zero,'girls_zero':girls_zero,'boys_zero':boys_zero,'boys_100':boys_100,'girls_100':girls_100, 'neighbours':gradewise_gpc}
        return self.data

    def get_school_data(self,answergroup):
        conditions = answergroup.values_list('institution__name', 'questiongroup__name').distinct()
        contests = list(answergroup.values_list('answers__question__key', flat=True).distinct())
        contests.pop(contests.index('Gender'))
        schools = []
        scores = {}

        for school, qgroup in conditions:
            school_ag = answergroup.filter(institution__name=school, questiongroup__name=qgroup)
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

        return schools,scores

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
