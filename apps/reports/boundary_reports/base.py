import argparse
import hashlib
import random
import pdfkit
import os.path
import datetime
from django.conf import settings

from abc import ABC, abstractmethod

from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

from boundary.models import Boundary, ElectionBoundary
from schools.models import Institution

from assessments.models import (
    SurveyInstitutionAgg,
    SurveyInstitutionQuestionGroupGenderCorrectAnsAgg,
    SurveyInstitutionQuestionGroupQuestionKeyCorrectAnsAgg,
    SurveyInstitutionQuestionGroupQuestionKeyAgg,
    SurveyInstitutionQuestionGroupGenderAgg,
    SurveyInstitutionQuestionGroupAgg,
    SurveyBoundaryQuestionGroupAnsAgg,
    Question,
    SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg,
    SurveyBoundaryQuestionGroupQuestionKeyAgg,
    SurveyEBoundaryQuestionGroupAnsAgg,
    SurveyEBoundaryQuestionGroupQuestionKeyCorrectAnsAgg,
    SurveyEBoundaryQuestionGroupQuestionKeyAgg,
)
from assessments import models as assess_models
from assessments.models import AnswerGroup_Institution, QuestionGroup
from django.db.models import Sum
from reports.models import Reports, Tracking
from reports.helpers import calc_stud_performance

def format_academic_year(yearmonth_format):
    # The day attribute is a dummy one just to get a clean date object. Ignore the day param 
    date = datetime.datetime(year=int(yearmonth_format[0:4]), month=int(yearmonth_format[4:6]), day=1)
    return date.strftime("%m/%Y")

class BaseReport(ABC):
    def __init__(self,**args):
        self.generate_gka = args.pop('generate_gka')
        self.generate_gp = args.pop('generate_gp')
        self.generate_hh = args.pop('generate_hhsurvey')
        self.common_data= { 
            'render_gka': self.generate_gka,
            'render_gp': self.generate_gp,
            'render_hh': self.generate_hh
        }

    @abstractmethod
    def get_data(self):
        pass

    def generate(self, report_type, output_name):
        if report_type == 'html':
            html = self.get_html()
            with open(output_name, 'w') as f:
                f.write(html)

        elif report_type == 'pdf':
            pdf = self.get_pdf()
            with open(output_name, 'w') as f:
                f.write(pdf)

        else:
            raise ValueError('Invalid report format')

    def get_html(self, lang=None):
        if not self.data:
            self.data = self.get_data();

        if lang == 'english':
            template = 'reports/{}.html'.format(self._type)
        else:
            template = 'reports/{}kannada.html'.format(self._type)
        html = render_to_string(template, {'data':self.data})
        return html

    def get_pdf(self, lang=None):
        html = self.get_html(lang)
        config = pdfkit.configuration()
        options = {
            'encoding':'utf-8',
        }
        pdf = pdfkit.PDFKit(html, 'string', configuration=config, options=options).to_pdf()
        return pdf

    def get_sms(self, tracker, name):
        url = reverse('view_report',kwargs={'report_id':tracker.report_id.link_id,'tracking_id':tracker.track_id})
        request = None
        full_url = ''.join([settings.REPORTS_SERVER_BASE_URL, url])
        return self.sms_template.format(full_url)

    def save(self):
        r= Reports(report_type=self._type,parameters=self.params, data=self.data)
        r.link_id = hashlib.sha256(str(random.random()).encode('utf-8')).hexdigest()[:5]
        r.save()
        t = Tracking(report_id=r, track_id='default')
        t.save()
        return r

    def save_link(self, report):
        t = Tracking(report_id = report, track_id = hashlib.sha256(str(random.random()).encode('utf-8')).hexdigest()[:5])
        t.save()
        return t
    
    '''boundary_type is the type of boundary passed in, one of district/block/cluster '''
    def get_basic_boundary_data(self, boundary, boundary_type, report_from, report_to):
        aggregates = None
        gender_agg = None
        num_schools_in_boundary = 0
        if boundary_type == 'district':
            num_schools_in_boundary = Institution.objects.filter(admin1=boundary).count() # Number of schools in district
            aggregates = SurveyInstitutionQuestionGroupAgg.objects.filter(institution_id__admin1=boundary,survey_id=2)\
                                                            .filter(yearmonth__gte = report_from)\
                                                            .filter(yearmonth__lte = report_to)
            gender_agg = SurveyInstitutionQuestionGroupGenderAgg.objects.filter(
                institution_id__admin1=boundary, 
                survey_id=2, 
                yearmonth__gte=report_from,
                yearmonth__lte=report_to)
        elif boundary_type == 'block':
            num_schools_in_boundary = Institution.objects.filter(admin2=boundary).count() # Number of schools in block
            aggregates = SurveyInstitutionQuestionGroupAgg.objects.filter(institution_id__admin2=boundary,survey_id=2)\
                                                            .filter(yearmonth__gte = report_from)\
                                                            .filter(yearmonth__lte = report_to)
            gender_agg = SurveyInstitutionQuestionGroupGenderAgg.objects.filter(
                institution_id__admin2=boundary, 
                survey_id=2, 
                yearmonth__gte=report_from,
                yearmonth__lte=report_to)
        elif boundary_type == 'cluster':
            num_schools_in_boundary = Institution.objects.filter(admin3=boundary).count() # Number of schools in block
            aggregates = SurveyInstitutionQuestionGroupAgg.objects.filter(institution_id__admin3=boundary,survey_id=2)\
                                                            .filter(yearmonth__gte = report_from)\
                                                            .filter(yearmonth__lte = report_to)
            gender_agg = SurveyInstitutionQuestionGroupGenderAgg.objects.filter(
                institution_id__admin3=boundary, 
                survey_id=2, 
                yearmonth__gte=report_from,
                yearmonth__lte=report_to)
        

        if aggregates is None or not aggregates.exists():
            raise ValueError("No GP contest data for '{}' between {} and {}".format(boundary.name, report_from, report_to))
        
        if gender_agg is None or not gender_agg.exists():
            raise ValueError("No gender data for '{}' between {} and {}".format(boundary.name, report_from, report_to))
        
        num_boys = gender_agg.filter(gender='Male').aggregate(Sum('num_assessments'))['num_assessments__sum']
        num_girls = gender_agg.filter(gender='Female').aggregate(Sum('num_assessments'))['num_assessments__sum']
        number_of_students = num_boys + num_girls
   
        num_contests = aggregates.values_list('institution_id__gp__id', flat=True).distinct().count()
        return num_schools_in_boundary, num_boys, num_girls, number_of_students, num_contests

    ''' Returns household survey aggregate values per boundary '''
    def getHouseholdSurvey(self,boundary,date_range):
        hh_answers_agg = None
        if isinstance(boundary, ElectionBoundary):
            hh_answers_agg = SurveyEBoundaryQuestionGroupAnsAgg.objects.filter(eboundary_id=boundary)\
                .filter(yearmonth__range=date_range,questiongroup_id__in=[18, 20])\
                .filter(question_id__in=[269, 144, 145, 138])
        else:
        #Household Survey
            hh_answers_agg = SurveyBoundaryQuestionGroupAnsAgg.objects.filter(boundary_id=boundary)\
                .filter(yearmonth__range=date_range,questiongroup_id__in=[18, 20])\
                .filter(question_id__in=[269, 144, 145, 138])
        if hh_answers_agg is not None and hh_answers_agg.exists():
            total_hh_answers = hh_answers_agg.values('question_desc', 'question_id').annotate(Sum('num_answers'))
            total_yes_answers = hh_answers_agg.filter(answer_option='Yes').values('question_desc', 'question_id').annotate(Sum('num_answers'))
            HHSurvey = []
            for each_answer in total_hh_answers:
                question_desc = total_yes_answers.get(question_desc=each_answer['question_desc'])
                total_yes_count = question_desc['num_answers__sum']
                question_text = Question.objects.get(id=each_answer['question_id']).question_text
                HHSurvey.append({'text':question_text,'percentage': round((total_yes_count/each_answer['num_answers__sum'])*100, 2)})
        else:
             raise ValueError("No community survey data for '{}' between {} and {}".format(self.cluster_name, self.report_from, self.report_to))
        return HHSurvey

    ''' boundary_type is one of 'district', 'block'. Needed for formatting the JSON structure '''
    def getBoundaryGKAData(self, boundary, boundary_type, date_range):
        GKA = SurveyBoundaryQuestionGroupAnsAgg.objects.filter(boundary_id=boundary)\
            .filter(yearmonth__range=date_range)\
            .filter(survey_id=11)
        if GKA.exists():
            # Teachers trained percentage
            teachers_trained_rounded = self.getTeacherTrainedPercent(GKA,date_range)
            #Kit usage percentage
            percent_kit_usage_rounded = self.getKitUsagePercent(GKA,date_range)
            
            #Group work percentage
            group_work_percent_rounded = self.getGroupWorkPercent(GKA,date_range)
            gka_summary = dict(teachers_trained=teachers_trained_rounded,\
                        kit_usage=percent_kit_usage_rounded,\
                        group_work=group_work_percent_rounded,\
                        boundary=boundary_type)
            gka_summary['boundary'] = boundary.name
            return gka_summary
        else:
            print("No boundary GKA data for '{}' between {} and {}.".format(boundary.name, date_range[0], date_range[1]))
            return None

    ''' Calculates the GKA aggregates both at the parent boundary level and aggregates per
    child boundary '''
    def getGKAData(self,parent_boundary, date_range):
        boundary_type_string = None
        #If the boundary is a district, get all the blocks under it and loop
        if parent_boundary.boundary_type.char_id == 'SD':
            child_boundaries = Boundary.objects.filter(parent=parent_boundary, boundary_type__char_id='SB')
            boundary_type_string = 'block'
        # If boundary is a block, get all clusters under it
        elif parent_boundary.boundary_type.char_id == 'SB':
            child_boundaries = Boundary.objects.filter(parent=parent_boundary, boundary_type__char_id='SC')
            boundary_type_string = 'cluster'
        child_boundaries_gka = []
        # Calculate aggregate GKA data for each child boundary. The boundary_type_string is needed for JSON structure
        for boundary in child_boundaries:
            child_boundary_gka = self.getBoundaryGKAData(boundary, boundary_type_string, date_range)
            if child_boundary_gka is not None:
                child_boundaries_gka.append(child_boundary_gka)

        if not child_boundaries_gka:
            print("no data")
            raise ValueError("No GKA data for '{}' between {} and {}".format(boundary.name, date_range[0], date_range[1]))
        
        # Calculate overall GKA aggregates for the boundary
        GKA = SurveyBoundaryQuestionGroupAnsAgg.objects.filter(boundary_id=parent_boundary)\
            .filter(yearmonth__gte=date_range[0], yearmonth__lte=date_range[1])\
            .filter(survey_id=11)

        gka = {
            'teachers_trained': self.getTeacherTrainedPercent(GKA, date_range),
            'kit_usage': self.getKitUsagePercent(GKA,date_range),
            'group_work': self.getGroupWorkPercent(GKA,date_range)
        }

        #Return both overall aggregate for boundary as well as child boundary aggregates
        return gka, child_boundaries_gka

    def getTeacherTrainedPercent(self, gka_aggregate_obj, date_range):
        # Teachers trained percentage
        teachers_trained = gka_aggregate_obj.filter(question_desc__icontains='trained', answer_option='Yes').aggregate(trained = Sum('num_answers'))
        total_teachers = gka_aggregate_obj.filter(question_desc__icontains='trained').aggregate(total = Sum('num_answers'))
        if teachers_trained['trained'] is None:
            teachers_trained['trained']=0;
        percent_teachers_trained = teachers_trained['trained']/total_teachers['total']*100
        return round(percent_teachers_trained,2)
    
    def getKitUsagePercent(self, gka_aggregate_obj, date_range):
        #Kit usage percentage
        kits_used = gka_aggregate_obj.filter(question_desc__icontains='Ganitha Kalika Andolana TLM', answer_option='Yes').aggregate(kits_used= Sum('num_answers'))
        kits_total = gka_aggregate_obj.filter(question_desc__icontains='Ganitha Kalika Andolana TLM').aggregate(total_kits = Sum('num_answers'))
        if kits_used['kits_used'] is None:
            kits_used['kits_used'] = 0
        percent_kit_usage = kits_used['kits_used']/kits_total['total_kits']*100
        return round(percent_kit_usage,2)
    
    def getGroupWorkPercent(self, gka_aggregate_obj, date_range):
         #Group work percentage
        group_work_done = gka_aggregate_obj.filter(question_desc__icontains='group', answer_option='Yes').aggregate(group_work_yes = Sum('num_answers'))
        group_work_total = gka_aggregate_obj.filter(question_desc__icontains='group').aggregate(group_work_total = Sum('num_answers'))
        if group_work_done['group_work_yes'] is None:
            group_work_done['group_work_yes']=0
        group_work_percent = group_work_done['group_work_yes']/group_work_total['group_work_total'] * 100
        return round(group_work_percent,2)

    ''' boundary can be either a school OR a GP. Student performance is shown only in GP and school reports so far'''
    def calculate_student_performance(self, boundary, report_from, report_to):
        male_correct_ans_per_gp = None
        female_correct_ans_per_gp = None
        male_total_ans_per_gp = None
        female_total_ans_per_gp = None
        if isinstance(boundary, ElectionBoundary):
            male_correct_ans_per_gp = SurveyEBoundaryQuestionGroupGenderCorrectAnsAgg.objects.filter(
                eboundary_id=gp_obj, survey_id=2)\
                .filter(yearmonth__gte = report_from)\
                .filter(yearmonth__lte = report_to)\
                .filter(gender='Male')\
                .aggregate(male_correct=Sum('num_assessments'))
            female_correct_ans_per_gp = SurveyEBoundaryQuestionGroupGenderCorrectAnsAgg.objects.filter(
                eboundary_id=gp_obj, survey_id=2)\
                .filter(yearmonth__gte = report_from)\
                .filter(yearmonth__lte = report_to)\
                .filter(gender='Female')\
                .aggregate(female_correct=Sum('num_assessments'))
            male_total_ans_per_gp = SurveyEBoundaryQuestionGroupGenderAgg.objects.filter(
                eboundary_id=gp_obj, survey_id=2)\
                .filter(yearmonth__gte = report_from)\
                .filter(yearmonth__lte = report_to)\
                .filter(gender='Male')\
                .aggregate(male_total=Sum('num_assessments'))
            female_total_ans_per_gp = SurveyEBoundaryQuestionGroupGenderAgg.objects.filter(
                eboundary_id=gp_obj, survey_id=2)\
                .filter(yearmonth__gte = report_from)\
                .filter(yearmonth__lte = report_to)\
                .filter(gender='Female')\
                .aggregate(female_total=Sum('num_assessments'))
        elif isinstance(boundary, Institution):
            male_correct_ans_per_gp = SurveyInstitutionQuestionGroupGenderCorrectAnsAgg.objects.filter(
                institution_id=boundary, survey_id=2)\
                .filter(yearmonth__gte = report_from)\
                .filter(yearmonth__lte = report_to)\
                .filter(gender='Male')\
                .aggregate(male_correct=Sum('num_assessments'))
            female_correct_ans_per_gp = SurveyInstitutionQuestionGroupGenderCorrectAnsAgg.objects.filter(
                institution_id=boundary, survey_id=2)\
                .filter(yearmonth__gte = report_from)\
                .filter(yearmonth__lte = report_to)\
                .filter(gender='Female')\
                .aggregate(female_correct=Sum('num_assessments'))
            male_total_ans_per_gp = SurveyInstitutionQuestionGroupGenderAgg.objects.filter(
                institution_id=boundary, survey_id=2)\
                .filter(yearmonth__gte = report_from)\
                .filter(yearmonth__lte = report_to)\
                .filter(gender='Male')\
                .aggregate(male_total=Sum('num_assessments'))
            female_total_ans_per_gp = SurveyInstitutionQuestionGroupGenderAgg.objects.filter(
                institution_id=boundary, survey_id=2)\
                .filter(yearmonth__gte = report_from)\
                .filter(yearmonth__lte = report_to)\
                .filter(gender='Female')\
                .aggregate(female_total=Sum('num_assessments'))

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
        return male_total, female_total, male_correct, female_correct, male_zero_ans_per_gp, female_zero_ans_per_gp

    def get_schools_data(self, boundary, dates):
        correct_answers_agg = None
        total_assessments = None
        if isinstance(boundary, Boundary):
            if boundary.boundary_type.char_id == 'SC':
                correct_answers_agg = SurveyInstitutionQuestionGroupQuestionKeyCorrectAnsAgg.objects.filter(survey_id=2, institution_id__admin3=boundary, yearmonth__range=dates)\
                    .values('question_key', 'questiongroup_id', 'institution_id', 'num_assessments')\
                    .annotate(total = Sum('num_assessments'))
                total_assessments = SurveyInstitutionQuestionGroupQuestionKeyAgg.objects.filter(survey_id=2, institution_id__admin3=boundary, yearmonth__range=dates)\
                    .values('question_key', 'questiongroup_id', 'questiongroup_name', 'institution_id', 'num_assessments')\
                    .annotate(Sum('num_assessments'))
        elif isinstance(boundary, ElectionBoundary):
            if boundary.const_ward_type_id == 'GP':
                correct_answers_agg = SurveyInstitutionQuestionGroupQuestionKeyCorrectAnsAgg.objects.filter(survey_id=2, institution_id__gp=boundary, yearmonth__range=dates)\
                    .values('question_key', 'questiongroup_id', 'institution_id', 'num_assessments')\
                    .annotate(total = Sum('num_assessments'))
                total_assessments = SurveyInstitutionQuestionGroupQuestionKeyAgg.objects.filter(survey_id=2, institution_id__gp=boundary, yearmonth__range=dates)\
                    .values('question_key', 'questiongroup_id', 'questiongroup_name', 'institution_id', 'num_assessments')\
                    .annotate(Sum('num_assessments'))
        elif isinstance(boundary, Institution):
            correct_answers_agg = SurveyInstitutionQuestionGroupQuestionKeyCorrectAnsAgg.objects.filter(survey_id=2, institution_id=boundary.id, yearmonth__range=dates)\
                    .values('question_key', 'questiongroup_id', 'institution_id', 'num_assessments')\
                    .annotate(total = Sum('num_assessments'))
            total_assessments = SurveyInstitutionQuestionGroupQuestionKeyAgg.objects.filter(survey_id=2, institution_id=boundary.id, yearmonth__range=dates)\
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
            #import pdb; pdb.set_trace()
            details = dict(boundary=Institution.objects.get(id=each_row['institution_id']).name, boundary_type='school',grade=each_row['questiongroup_name'])
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
     
    ''' Returns the boundary wise aggregation per grade per contest. This method can take an election boundary
        (GP) or a boundary object
        For example: Class 4 aggregates at the boundary level for all concepts (Addition, Subtraction etc..)
     '''
    def get_boundary_gpc_gradewise_agg(self, boundary, report_from, report_to):
        correct_answers_agg= None
        total_assessments=None 
        distinct_grades = None

        if isinstance(boundary, Boundary):
            correct_answers_agg = SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.objects\
                    .filter(survey_id=2, boundary_id=boundary, survey_tag='gka')\
                    .filter(yearmonth__gte = report_from)\
                    .filter(yearmonth__lte = report_to)\
                    .values('question_key', 'questiongroup_name')\
                    .annotate(correct_answers = Sum('num_assessments'))
            total_assessments = SurveyBoundaryQuestionGroupQuestionKeyAgg.objects\
                    .filter(survey_id=2, boundary_id=boundary, survey_tag='gka')\
                    .filter(yearmonth__gte = report_from)\
                    .filter(yearmonth__lte = report_to)\
                    .values('question_key', 'questiongroup_name')\
                    .annotate(total_answers = Sum('num_assessments'))
            distinct_grades=total_assessments\
                    .values('questiongroup_name')\
                    .distinct()
        elif isinstance(boundary, ElectionBoundary):
            try:
                correct_answers_agg = SurveyEBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.objects\
                        .filter(survey_id=2, eboundary_id=boundary, survey_tag='gka')\
                        .filter(yearmonth__gte = report_from)\
                        .filter(yearmonth__lte = report_to)\
                        .values('question_key',  'questiongroup_name')\
                        .annotate(correct_answers = Sum('num_assessments'))
            except SurveyEBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.DoesNotExist:
                pass
            try:
                total_assessments = SurveyEBoundaryQuestionGroupQuestionKeyAgg.objects\
                        .filter(survey_id=2, eboundary_id=boundary, survey_tag='gka')\
                        .filter(yearmonth__gte = report_from)\
                        .filter(yearmonth__lte = report_to)\
                        .values('question_key', 'questiongroup_name')\
                        .annotate(total_answers = Sum('num_assessments'))
                if total_assessments is not None:
                    distinct_grades=total_assessments\
                            .values('questiongroup_name')\
                            .distinct()
            except SurveyEBoundaryQuestionGroupQuestionKeyAgg.DoesNotExist:
                pass

        gpc_gradewise_percent = []
        #We actually have assessments for this particular boundary
        if total_assessments is not None and correct_answers_agg is not None and distinct_grades is not None:    
            for each_grade in distinct_grades:
                qgroup_id = each_grade['questiongroup_name']
                gradewise_total_agg = total_assessments.filter(questiongroup_name = qgroup_id)
                gradewise_correctans_agg = correct_answers_agg.filter(questiongroup_name = qgroup_id)
                if total_assessments is not None:
                    scores = []
                    for each_row in gradewise_total_agg:
                        concept_scores = dict()
                        try:
                            sum_total = gradewise_total_agg.get(question_key=each_row['question_key'])
                        except SurveyBoundaryQuestionGroupQuestionKeyAgg.DoesNotExist:
                            print("No assessment matches this question_key, questiongroup_id combo")
                            sum_total = None
                        try:
                            sum_correct_ans = gradewise_correctans_agg.get(question_key=each_row['question_key'])
                        except SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.DoesNotExist:
                            sum_correct_ans = None
                    
                        percent = 0
                        correct_ans_total = 0
                        if sum_correct_ans is None or sum_correct_ans['correct_answers'] is None:
                            correct_ans_total =0
                        else:
                            correct_ans_total = sum_correct_ans['correct_answers']
                        
                        if sum_total is not None and sum_total['total_answers'] > 0:
                            percent = round(correct_ans_total/sum_total['total_answers'] * 100,2)
                        else:
                            percent = 0
                        concept_scores['contest']= each_row['question_key']
                        concept_scores['score'] = percent
                        scores.append(concept_scores) # End of for-loop
                    
                    details = dict(grade = each_grade['questiongroup_name'], 
                                        values = scores)
                    gpc_gradewise_percent.append(details)
        
        return gpc_gradewise_percent


    '''
        This is a generic method that returns the Gram Panchayat contest aggregations
        for a given boundary type. The child_bound_type parameter can be one of
        'block', 'cluster'. Move to base class
    '''
    def get_childboundary_GPC_agg(self,parent_boundary, child_bound_type, dates):
        children_under_parent = Boundary.objects.filter(parent=parent_boundary)\
                                .values_list('id', flat=True)
        
        child_gpc_dict = []
        for child_boundary in children_under_parent:
            correct_answers_agg = SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.objects\
                .filter(survey_id=2, boundary_id=child_boundary, survey_tag='gka')\
                .filter(yearmonth__gte = dates[0])\
                .filter(yearmonth__lte = dates[1])\
                .values('question_key', 'questiongroup_name', 'boundary_id')\
                .annotate(total = Sum('num_assessments'))
            total_assessments = SurveyBoundaryQuestionGroupQuestionKeyAgg.objects\
                .filter(survey_id=2, boundary_id=child_boundary, survey_tag='gka')\
                .filter(yearmonth__gte = dates[0])\
                .filter(yearmonth__lte = dates[1])\
                .values('question_key', 'questiongroup_name', 'boundary_id')\
                .annotate(Sum('num_assessments'))
            for each_row in total_assessments:
                sum_total = each_row['num_assessments__sum']
                percent = 0
                try:
                    sum_correct_ans = correct_answers_agg.filter(question_key=each_row['question_key'])\
                        .get(questiongroup_name=each_row['questiongroup_name'])
                    if sum_correct_ans is None or sum_correct_ans['total'] is None:
                        #import pdb; pdb.set_trace()
                        correct_ans_total =0
                    else:
                        correct_ans_total = sum_correct_ans['total']
                except Exception as e:
                    #Can't find any correct answers at all
                    correct_ans_total =0
                    # import pdb; pdb.set_trace()
                if sum_total is not None and sum_total > 0:
                    percent = correct_ans_total/sum_total * 100
                else:
                    percent = 0
                #import pdb; pdb.set_trace()
                details = dict(grade=each_row['questiongroup_name'],boundary_type=child_bound_type)
                details['boundary'] = (Boundary.objects.get(id=child_boundary)).name
                details['contest'] = each_row['question_key']
                details['percent'] = percent
                child_gpc_dict.append(details)
        return child_gpc_dict

    def format_boundary_data(self, blocks):
        blocks_out = []
        out= []

        for item in blocks:
            if not item['boundary'] in blocks_out:
                blocks_out.append(item['boundary'])
                out.append({'boundary':item['boundary'],
                            'boundary_type': item['boundary_type'],
                            'grades':[{
                                'name':item['grade'],
                                'values':[{'contest':item['contest'],'count':round(item['percent'], 2) }]}]
                })
            else:
                for o in out:
                    if o['boundary']==item['boundary']:
                        gradeExist= False
                        for grade in o['grades']:
                            if item['grade'] == grade['name']:
                                gradeExist = True
                                grade['values'].append({'contest':item['contest'],'count':round(item['percent'], 2) })
                        if not gradeExist:
                            o['grades'].append({'name':item['grade'],'values':[{'contest':item['contest'],'count':round(item['percent'], 2) }]})

        return out
