import argparse, hashlib, random
from abc import ABC, abstractmethod
from jinja2 import Environment, FileSystemLoader
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
import pdfkit
import os.path
import datetime

from boundary.models import Boundary, ElectionBoundary
from assessments.models import SurveyInstitutionAgg
from schools.models import Institution
from assessments import models as assess_models
from assessments.models import AnswerGroup_Institution, QuestionGroup
from .models import Reports, Tracking

class BaseReport(ABC):
    def __init__(self, data=None):
        self.data = data

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

        if lang == 'kannada':
            template = 'reports/{}kannada.html'.format(self._type)
        else:
            template = 'reports/{}.html'.format(self._type)
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
        full_url = ''.join(['http://', get_current_site(request).domain, url])
        return self.sms_template.format(name, full_url)

    def save(self):
        r= Reports(report_type=self._type,parameters=self.params, data=self.data)
        r.link_id = hashlib.sha256(str(random.random()).encode('utf-8')).hexdigest()[:7]
        r.save()
        t = Tracking(report_id=r, track_id='default')
        t.save()
        return r

    def save_link(self, report):
        t = Tracking(report_id = report, track_id = hashlib.sha256(str(random.random()).encode('utf-8')).hexdigest()[:7])
        t.save()
        return t

class ReportOne(BaseReport):
    def __init__(self, from_date, to_date, **kwargs):
        self.from_date = from_date
        self.to_date = to_date
        self._template_path  = 'report_one.html'
        self.sms_template = 'some_url/{}/{}'
        self._type = 'reportOne'
        self.params = dict(from_date=self.from_date,to_date=self.to_date)
        super().__init__(**kwargs)

    def get_data(self):
#        return assess_models.AnswerGroup_Institution.objects.all()[:5]
        return ['name','some','dfdfdfa','dfdafad']

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
        self.sms_template ="Hi {}, We at Akshara Foundation are continuously working to provide Gram panchayat math contest report for %s . Please click the link {}"% self.gp_name
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

        report_generated_on = datetime.datetime.now().date().isoformat()

        try:
            gp_obj = ElectionBoundary.objects.get(const_ward_name=gp, const_ward_type__char_id='GP') # Take the GP from db
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
        district = AGI.values_list('institution__admin3__name', flat=True).distinct()[0]
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
                    answered = ag.answers.filter(question__key=contest, answer='Yes').count()
                    mark = (answered/num_q)*100
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

        #Calculate the perfomance of students
        boys_100 = 0
        girls_100 = 0
        boys_zero = 0
        girls_zero = 0
        for i in scores.values():
            total = sum(i['mark'])/len(i['mark'])
            if total == 100.0:
                if i['gender'] == 'Male':
                    boys_100 += 1
                else:
                    girls_100 += 1
            elif total == 0.0:
                if i['gender'] == 'Male':
                    boys_zero += 1
                else:
                    girls_zero += 1

        score_100 = boys_100 + girls_100
        score_zero = boys_zero + girls_zero

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
        for i in out:
            for grade in i['grades']:
                count = 0
                num = 0
                for value in grade['values']:
                    if value['contest'] not in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']:
                        count += value['count']
                        num += 1
                grade['values']  = [k for k in grade['values'] if k['contest'] in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']]
                grade['values'].append(dict(contest='Other Areas', count=round(count/num, 2)))


        survey = self.getHouseholdServey(gp_obj, dates)

        self.data =  {'gp_name': gp.title(), 'academic_year':'{} - {}'.format(self.report_from, self.report_to), 'block':block, 'district':district.title(),'no_schools_gp':gp_schools,'no_students':number_of_students,'today':report_generated_on,'boys':num_boys,'girls':num_girls,'schools':out,'cs':contest_list,'score_100':score_100,'score_zero':score_zero,'girls_zero':girls_zero,'boys_zero':boys_zero,'boys_100':boys_100,'girls_100':girls_100, 'survey':survey}
        return self.data

    def getHouseholdServey(self,gp_obj,date_range):
        #Husehold Survey
        a = AnswerGroup_Institution.objects.filter(institution__gp=gp_obj, date_of_visit__range=date_range, questiongroup_id__in=[18, 20])

        questions = QuestionGroup.objects.get(id=18).questions.filter(id__in=[269, 144, 145, 138])

        total_response = a.count()

        HHSurvey = []

        for i in questions:
            count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
            count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
            HHSurvey.append({'text':i.question_text,'percentage': round((count/total_response)*100, 2)})

        return HHSurvey

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
        self.sms_template ="Hi {}, We at Akshara Foundation are continuously working to provide Gram panchayat math contest report for %s. Please click the link {}"
        super().__init__(**kwargs)

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.school_code = arguments.school_code
        self.report_from = arguments.report_from
        self.report_to = arguments.report_to
        self.params = dict(school_code=self.school_code, report_from=self.report_from, report_to=self.report_to)

    def get_data(self, neighbour_required=True):
        dates = [self.report_from, self.report_to] # [2016-06-01, 2017-03-31]

        report_generated_on = datetime.datetime.now().date().isoformat()

        try:
            school_obj = Institution.objects.get(dise__school_code=self.school_code) # Take the school from db
            self.sms_template = self.sms_template % school_obj.name
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

        #Calculate the perfomance of students
        boys_100 = 0
        girls_100 = 0
        boys_zero = 0
        girls_zero = 0
        for i in scores.values():
            total = sum(i['mark'])/len(i['mark'])
            if total == 100.0:
                if i['gender'] == 'Male':
                    boys_100 += 1
                else:
                    girls_100 += 1
            elif total == 0.0:
                if i['gender'] == 'Male':
                    boys_zero += 1
                else:
                    girls_zero += 1

        score_100 = boys_100 + girls_100
        score_zero = boys_zero + girls_zero

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

        self.data =  {'gp_name': gp, 'academic_year':'{} - {}'.format(self.report_from, self.report_to), 'cluster':cluster, 'block':block, 'district':district,'no_students':number_of_students,'today':report_generated_on,'boys':num_boys,'girls':num_girls,'schools':out,'cs':contest_list,'score_100':score_100,'score_zero':score_zero,'girls_zero':girls_zero,'boys_zero':boys_zero,'boys_100':boys_100,'girls_100':girls_100, 'neighbours':neighbours}
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
                    answered = ag.answers.filter(question__key=contest, answer='Yes').count()
                    mark = (answered/num_q)*100
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

        for i in out:
            for grade in i['grades']:
                count = 0
                num = 0
                for value in grade['values']:
                    if value['contest'] not in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']:
                        count += value['count']
                        num += 1
                grade['values']  = [k for k in grade['values'] if k['contest'] in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']]
                grade['values'].append(dict(contest='Other Areas', count=round(count/num, 2)))
        return out

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
        self.sms_template ='Hi {}, We at Akshara Foundation are continuously working to provide Gram panchayat math contest report for %s. Please click the link {}'% self.cluster_name
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
        dates = [self.report_from, self.report_to] # [2016-06-01, 2017-03-31]
        report_generated_on = datetime.datetime.now().date().isoformat()
        try:
             # Take the cluster from db
            cluster = Boundary.objects.get(name=self.cluster_name, parent__name=self.block_name, parent__parent__name=self.district_name, boundary_type__char_id='SC')
        except Boundary.DoesNotExist:
            raise ValueError("Cluster '{}' cannot be found in the database".format(self.cluster_name))

        no_of_schools_in_cluster = Institution.objects.filter(admin3=cluster).count() # Number of schools in cluster

        AGI = AnswerGroup_Institution.objects.filter(institution__admin3=cluster, date_of_visit__range=dates, respondent_type_id='CH', questiongroup__survey_id=2)
        if not AGI.exists():
            raise ValueError("No GP contest data for '{}' between {} and {}".format(self.cluster_name, self.report_from, self.report_to))

        num_boys = AGI.filter(answers__question__key='Gender', answers__answer='Male').count()
        num_girls = AGI.filter(answers__question__key='Gender', answers__answer='Female').count()
        number_of_students = num_boys + num_girls

        num_contests = AGI.values_list('answers__question__key', flat=True).distinct().count()

        schools_data = self.get_school_data(AGI)
        schools = self.format_schools_data(schools_data)

        gka = self.getGKAData(cluster, dates)

        household = self.getHouseholdSurvey(cluster,dates)

        self.data = {'cluster':self.cluster_name.title(), 'academic_year':'{} - {}'.format(self.report_from, self.report_to), 'block':self.block_name.title(), 'district':self.district_name.title(), 'no_schools':no_of_schools_in_cluster, 'today':report_generated_on, 'gka':gka, 'household':household, 'schools':schools, 'num_boys':num_boys, 'num_girls':num_girls, 'num_students':number_of_students, 'num_contests':num_contests}
        return self.data

    def get_school_data(self,answergroup):
        conditions = answergroup.values_list('institution__name', 'questiongroup__name').distinct()
        contests = list(answergroup.values_list('answers__question__key', flat=True).distinct())
        contests.pop(contests.index('Gender'))
        schools = []

        for school, qgroup in conditions:
            school_ag = answergroup.filter(institution__name=school, questiongroup__name=qgroup)
            for contest in contests:
                try:
                    score = school_ag.filter(answers__question__key=contest, answers__answer='Yes').count()/school_ag.filter(answers__question__key=contest).count()
                except ZeroDivisionError:
                    continue
                details = dict(school=school, grade=qgroup)
                details['contest'] = contest
                details['percent'] = score*100
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

        for i in out:
            for grade in i['grades']:
                count = 0
                num = 0
                for value in grade['values']:
                    if value['contest'] not in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']:
                        count += value['count']
                        num += 1
                grade['values']  = [k for k in grade['values'] if k['contest'] in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']]
                grade['values'].append(dict(contest='Other Areas', count=round(count/num, 2)))
        return out

    def getHouseholdSurvey(self,cluster,date_range):
        #Husehold Survey
        a = AnswerGroup_Institution.objects.filter(institution__admin3=cluster, date_of_visit__range=date_range, questiongroup_id__in=[18, 20])
        HHSurvey = []
        if a.exists():
            questions = QuestionGroup.objects.get(id=18).questions.filter(id__in=[269, 144, 145, 138])

            total_response = a.count()

            for i in questions:
                count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
                count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
                HHSurvey.append({'text':i.question_text,'percentage': round((count/total_response)*100, 2)})
        else:
             raise ValueError("No community survey data for '{}' between {} and {}".format(self.cluster_name, self.report_from, self.report_to))
        return HHSurvey

    def getGKAData(self, cluster, date_range):
        GKA = AnswerGroup_Institution.objects.filter(institution__admin3=cluster, date_of_visit__range=date_range, questiongroup__survey_id=11)
        if GKA.exists():
            teachers_trained = GKA.filter(answers__question__question_text__icontains='trained', answers__answer='Yes').count()/GKA.filter(answers__question__question_text__icontains='trained').count()
            kit_usage = GKA.filter(answers__question__question_text__contains='Ganitha Kalika Andolana TLM', answers__answer='Yes').count()/GKA.filter(answers__question__question_text__icontains='Ganitha Kalika Andolana TLM').count()
            group_work = GKA.filter(answers__question__question_text__contains='group', answers__answer='Yes').count()/GKA.filter(answers__question__question_text__icontains='group').count()
            return dict(teachers_trained=round(teachers_trained*100, 2),  kit_usage=round(kit_usage*100, 2), group_work=round(group_work*100, 2))
        else:
            raise ValueError("No GKA data for '{}' between {} and {}.".format(self.cluster_name, self.report_from, self.report_to))

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
        self.sms_template ='Hi {}, We at Akshara Foundation are continuously working to provide Gram panchayat math contest report for %s. Please click the link {}'% self.block_name
        super().__init__(**kwargs)

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.block_name = arguments.block_name
        self.district_name = arguments.district_name
        self.report_from = arguments.report_from
        self.report_to = arguments.report_to
        self.params = dict(block_name=self.block_name, district_name=self.district_name, report_from=self.report_from, report_to=self.report_to)

    def get_data(self):
        dates = [self.report_from, self.report_to] # [2016-06-01, 2017-03-31]
        report_generated_on = datetime.datetime.now().date().isoformat()

        try:
            # Take the block from db
            block = Boundary.objects.get(name=self.block_name, parent__name=self.district_name, boundary_type__char_id='SB') 
        except Boundary.DoesNotExist:
            raise ValueError("Block '{}' cannot be found in the database".format(self.block_name))

        num_schools = Institution.objects.filter(admin2=block).count() # schools in block

        AGI = AnswerGroup_Institution.objects.filter(institution__admin2=block, date_of_visit__range=dates, respondent_type_id='CH', questiongroup__survey_id=2)
        if not AGI.exists():
            raise ValueError("No GP contest data for '{}' between {} and {}".format(self.block_name, self.report_from, self.report_to))

        num_boys = AGI.filter(answers__question__key='Gender', answers__answer='Male').count()
        num_girls = AGI.filter(answers__question__key='Gender', answers__answer='Female').count()
        number_of_students = num_boys + num_girls

        num_contests = AGI.values_list('answers__question__key', flat=True).distinct().count()

        cluster_gpc_data = self.get_cluster_GPC(AGI)
        gpc_clusters = self.format_cluster_data(cluster_gpc_data)

        gka, gka_clusters = self.getGKAData(block, dates)

        household = self.getHouseholdSurvey(block, dates)

        self.data = {'block':self.block_name.title(), 'district':self.district_name.title(), 'academic_year':'{} - {}'.format(self.report_from, self.report_to), 'today':report_generated_on, 'no_schools':num_schools, 'gka':gka, 'gka_clusters':gka_clusters, 'gpc_clusters':gpc_clusters, 'household':household, 'num_boys':num_boys, 'num_girls':num_girls, 'num_students':number_of_students, 'num_contests':num_contests}
        return self.data

    def get_cluster_GPC(self,answergroup):
        conditions = answergroup.values_list('institution__admin3__name', 'questiongroup__name').distinct()
        contests = list(answergroup.values_list('answers__question__key', flat=True).distinct())
        contests.pop(contests.index('Gender'))
        clusters = []

        for cluster, qgroup in conditions:
            cluster_ag = answergroup.filter(institution__admin3__name=cluster, questiongroup__name=qgroup)
            for contest in contests:
                try:
                    score = cluster_ag.filter(answers__question__key=contest, answers__answer='Yes').count()/cluster_ag.filter(answers__question__key=contest).count()
                except ZeroDivisionError:
                    continue
                details = dict(cluster=cluster, grade=qgroup)
                details['contest'] = contest
                details['percent'] = score*100
                clusters.append(details)

        return clusters

    def format_cluster_data(self, clusters):
        clusters_out = []
        out= []

        for item in clusters:
            if not item['cluster'] in clusters_out:
                clusters_out.append(item['cluster'])
                out.append({'cluster':item['cluster'],
                            'grades':[{
                                'name':item['grade'],
                                'values':[{'contest':item['contest'],'count':round(item['percent'], 2) }]}]
                })
            else:
                for o in out:
                    if o['cluster']==item['cluster']:
                        gradeExist= False
                        for grade in o['grades']:
                            if item['grade'] == grade['name']:
                                gradeExist = True
                                grade['values'].append({'contest':item['contest'],'count':round(item['percent'], 2) })
                        if not gradeExist:
                            o['grades'].append({'name':item['grade'],'values':[{'contest':item['contest'],'count':round(item['percent'], 2) }]})

        for i in out:
            for grade in i['grades']:
                count = 0
                num = 0
                for value in grade['values']:
                    if value['contest'] not in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']:
                        count += value['count']
                        num += 1
                grade['values']  = [k for k in grade['values'] if k['contest'] in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']]
                grade['values'].append(dict(contest='Other Areas', count=round(count/num, 2)))
        return out

    def getGKAData(self, block, date_range):
        clusters  = Boundary.objects.filter(parent=block, boundary_type__char_id='SC') # Clusters that belong to the block
        cluster_gka = []
        for cluster in clusters:
            GKA = AnswerGroup_Institution.objects.filter(institution__admin3=cluster, date_of_visit__range=date_range, questiongroup__survey_id=11)
            if GKA.exists():
                teachers_trained = GKA.filter(answers__question__question_text__icontains='trained', answers__answer='Yes').count()/GKA.filter(answers__question__question_text__icontains='trained').count()
                kit_usage = GKA.filter(answers__question__question_text__contains='Ganitha Kalika Andolana TLM', answers__answer='Yes').count()/GKA.filter(answers__question__question_text__icontains='Ganitha Kalika Andolana TLM').count()
                group_work = GKA.filter(answers__question__question_text__contains='group', answers__answer='Yes').count()/GKA.filter(answers__question__question_text__icontains='group').count()
                cluster_gka.append(dict(cluster=cluster.name, teachers_trained=round(teachers_trained*100, 2),  kit_usage=round(kit_usage*100, 2), group_work=round(group_work*100, 2)))
            else:
                print("No GKA data for CLUSTER {} in {} block for academic year {}".format(cluster.name, cluster.parent.name, date_range))
                continue

        if not cluster_gka:
            raise ValueError("No GKA data for '{}' between {} and {}".format(self.block_name, self.report_from, self.report_to))

        gka = dict(teachers_trained=round(sum([i['teachers_trained'] for i in cluster_gka])/len(cluster_gka), 2),  kit_usage=round(sum([i['kit_usage'] for i in cluster_gka])/len(cluster_gka), 2), group_work=round(sum([i['group_work'] for i in cluster_gka])/len(cluster_gka), 2))

        return gka, cluster_gka

    def getHouseholdSurvey(self,block,date_range):
        #Husehold Survey
        a = AnswerGroup_Institution.objects.filter(institution__admin2=block, date_of_visit__range=date_range, questiongroup_id__in=[18, 20])
        HHSurvey = []
        if a.exists():
            questions = QuestionGroup.objects.get(id=18).questions.filter(id__in=[269, 144, 145, 138])

            total_response = a.count()

            for i in questions:
                count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
                count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
                HHSurvey.append({'text':i.question_text,'percentage': round((count/total_response)*100, 2)})
        else:
             raise ValueError("No community survey data for '{}' between {} and {}".format(self.block_name, self.report_from, self.report_to))
        return HHSurvey

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
        self.sms_template ='Hi {}, We at Akshara Foundation are continuously working to provide Gram panchayat math contest report for %s. Please click the link {}'% self.district_name
        super().__init__(**kwargs)

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.distrct_name = arguments.district_name
        self.report_from = arguments.report_from
        self.report_to = arguments.report_to
        self.params = dict(district_name=self.district_name, report_from=self.report_from, report_to=self.report_to)

    def get_data(self):
        dates = [self.report_from, self.report_to] # [2016-06-01, 2017-03-31]
        report_generated_on = datetime.datetime.now().date().isoformat()

        try:
            district = Boundary.objects.get(name=self.district_name, boundary_type__char_id='SD')
        except Boundary.DoesNotExist:
            raise ValueError("District '{}' cannot be found in the database".format(self.district_name))

        AGI = AnswerGroup_Institution.objects.filter(institution__admin1=district, date_of_visit__range = dates, respondent_type_id='CH', questiongroup__survey_id=2)
        if not AGI.exists():
            raise ValueError("No GP contest data for '{}' between {} and {}".format(self.district_name, self.report_from, self.report_to))

        num_schools = Institution.objects.filter(admin1=district).count()
        num_boys = AGI.filter(answers__question__key='Gender', answers__answer='Male').count()
        num_girls = AGI.filter(answers__question__key='Gender', answers__answer='Female').count()
        number_of_students = num_boys + num_girls
        num_contests = AGI.values_list('answers__question__key', flat=True).distinct().count()
        num_gp = district.institution_admin1.exclude(gp=None).values_list('gp__id',flat=True).distinct().count()

        block_gpc_data = self.get_block_GPC(AGI)
        gpc_blocks = self.format_block_data(block_gpc_data)

        gka, gka_blocks = self.getGKAData(district, dates)

        household = self.getHouseholdSurvey(district, dates)

        #GPC Gradewise data
        gpc_grades = {'Class 4 Assessment':{}, 'Class 5 Assessment':{}, 'Class 6 Assessment':{}}
        for block in gpc_blocks:
            for grade in block['grades']:
                for value in grade['values']:
                    try:
                        gpc_grades[grade['name']][value['contest']]+=value['count']
                    except KeyError:
                        gpc_grades[grade['name']][value['contest']]=value['count']
        gradewise_gpc = []
        for grade, values in gpc_grades.items():
            for j ,k in values.items():
                values[j] = round(k/len(gpc_blocks), 2)
            gradewise_gpc.append({'grade':grade, 'values':[{'contest':contest, 'score':score} for contest,score in values.items()]})

        self.data = {'academic_year':'{} - {}'.format(self.report_from, self.report_to), 'today':report_generated_on, 'district':self.district_name.title(), 'gka':gka, 'gka_blocks':gka_blocks, 'no_schools':num_schools, 'gpc_blocks':gpc_blocks, 'household':household, 'num_boys':num_boys, 'num_girls':num_girls, 'num_students':number_of_students, 'num_contests':num_contests, 'gpc_grades':gradewise_gpc, 'num_gp':num_gp}
        return self.data

    def get_block_GPC(self,answergroup):
        conditions = answergroup.values_list('institution__admin2__name', 'questiongroup__name').distinct()
        contests = list(answergroup.values_list('answers__question__key', flat=True).distinct())
        contests.pop(contests.index('Gender'))
        blocks = []

        for block, qgroup in conditions:
            block_ag = answergroup.filter(institution__admin2__name=block, questiongroup__name=qgroup)
            for contest in contests:
                try:
                    score = block_ag.filter(answers__question__key=contest, answers__answer='Yes').count()/block_ag.filter(answers__question__key=contest).count()
                except ZeroDivisionError:
                    continue
                details = dict(block=block, grade=qgroup)
                details['contest'] = contest
                details['percent'] = score*100
                blocks.append(details)

        return blocks

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

        for i in out:
            for grade in i['grades']:
                count = 0
                num = 0
                for value in grade['values']:
                    if value['contest'] not in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']:
                        count += value['count']
                        num += 1
                grade['values']  = [k for k in grade['values'] if k['contest'] in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']]
                grade['values'].append(dict(contest='Other Areas', count=round(count/num, 2)))
        return out

    def getGKAData(self, district, date_range):
        blocks  = Boundary.objects.filter(parent=district, boundary_type__char_id='SB') # Blocks that belong to the district
        block_gka = []
        for block in blocks:
            GKA = AnswerGroup_Institution.objects.filter(institution__admin2=block, date_of_visit__range=date_range, questiongroup__survey_id=11)
            if GKA.exists():
                teachers_trained = GKA.filter(answers__question__question_text__icontains='trained', answers__answer='Yes').count()/GKA.filter(answers__question__question_text__icontains='trained').count()
                kit_usage = GKA.filter(answers__question__question_text__contains='Ganitha Kalika Andolana TLM', answers__answer='Yes').count()/GKA.filter(answers__question__question_text__icontains='Ganitha Kalika Andolana TLM').count()
                group_work = GKA.filter(answers__question__question_text__contains='group', answers__answer='Yes').count()/GKA.filter(answers__question__question_text__icontains='group').count()
                block_gka.append(dict(block=block.name, teachers_trained=round(teachers_trained*100, 2),  kit_usage=round(kit_usage*100, 2), group_work=round(group_work*100, 2)))
            else:
                print("No GKA data for BLOCK {} in {} district for academic year {}".format(block.name, block.parent.name, date_range))
                continue

        if not block_gka:
            raise ValueError("No GKA data for '{}' between {} and {}".format(self.district_name, self.report_from, self.report_to))

        gka = dict(teachers_trained=round(sum([i['teachers_trained'] for i in block_gka])/len(block_gka), 2),  kit_usage=round(sum([i['kit_usage'] for i in block_gka])/len(block_gka), 2), group_work=round(sum([i['group_work'] for i in block_gka])/len(block_gka), 2))

        return gka, block_gka

    def getHouseholdSurvey(self,district,date_range):
        #Husehold Survey
        a = AnswerGroup_Institution.objects.filter(institution__admin1=district, date_of_visit__range=date_range, questiongroup_id__in=[18, 20])
        HHSurvey = []
        if a.exists():
            questions = QuestionGroup.objects.get(id=18).questions.filter(id__in=[269, 144, 145, 138])

            total_response = a.count()

            for i in questions:
                count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
                count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
                HHSurvey.append({'text':i.question_text,'percentage': round((count/total_response)*100, 2)})
        else:
             raise ValueError("No community survey data for '{}' between {} and {}".format(self.deistrict_name, self.report_from, self.report_to))
        return HHSurvey

# Summarized reports

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
        self.sms_template ="Hi {}, We at Akshara Foundation are continuously working to provide Gram panchayat math contest report for %s . Please click the link {}"% self.gp_name
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

        report_generated_on = datetime.datetime.now().date().isoformat()

        try:
            gp_obj = ElectionBoundary.objects.get(const_ward_name=gp, const_ward_type__char_id='GP') # Take the GP from db
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
        district = AGI.values_list('institution__admin3__name', flat=True).distinct()[0]
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
                    answered = ag.answers.filter(question__key=contest, answer='Yes').count()
                    mark = (answered/num_q)*100
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

        #Calculate the perfomance of students
        boys_100 = 0
        girls_100 = 0
        boys_zero = 0
        girls_zero = 0
        for i in scores.values():
            total = sum(i['mark'])/len(i['mark'])
            if total == 100.0:
                if i['gender'] == 'Male':
                    boys_100 += 1
                else:
                    girls_100 += 1
            elif total == 0.0:
                if i['gender'] == 'Male':
                    boys_zero += 1
                else:
                    girls_zero += 1

        score_100 = boys_100 + girls_100
        score_zero = boys_zero + girls_zero

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
        for i in out:
            for grade in i['grades']:
                count = 0
                num = 0
                for value in grade['values']:
                    if value['contest'] not in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']:
                        count += value['count']
                        num += 1
                grade['values']  = [k for k in grade['values'] if k['contest'] in ['Addition', 'Subtraction', 'Number Concept', 'Multiplication', 'Division']]
                grade['values'].append(dict(contest='Other Areas', count=round(count/num, 2)))


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

        self.data =  {'gp_name': gp.title(), 'academic_year':'{} - {}'.format(self.report_from, self.report_to), 'block':block, 'district':district.title(),'no_schools_gp':gp_schools,'no_students':number_of_students,'today':report_generated_on,'boys':num_boys,'girls':num_girls,'schools':gradewise_gpc,'cs':contest_list,'score_100':score_100,'score_zero':score_zero,'girls_zero':girls_zero,'boys_zero':boys_zero,'boys_100':boys_100,'girls_100':girls_100, 'survey':survey}
        return self.data

    def getHouseholdServey(self,gp_obj,date_range):
        #Husehold Survey
        a = AnswerGroup_Institution.objects.filter(institution__gp=gp_obj, date_of_visit__range=date_range, questiongroup_id__in=[18, 20])

        questions = QuestionGroup.objects.get(id=18).questions.filter(id__in=[269, 144, 145, 138])

        total_response = a.count()

        HHSurvey = []

        for i in questions:
            count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
            count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
            HHSurvey.append({'text':i.question_text,'percentage': round((count/total_response)*100, 2)})

        return HHSurvey


if __name__ == "__main__":
    r= ReportOne();
    r.get_data
