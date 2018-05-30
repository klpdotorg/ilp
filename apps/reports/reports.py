import argparse, hashlib, random
from abc import ABC, abstractmethod
from jinja2 import Environment, FileSystemLoader
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
import pdfkit
import os.path
import datetime

from boundary.models import Boundary
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

    def get_html(self):
        if not self.data:
            self.data = self.get_data();
        html = render_to_string('reports/{}.html'.format(self._type), {'data':self.data})
        return html

    def get_pdf(self):
        html = self.get_html()
        config = pdfkit.configuration()
        pdf = pdfkit.PDFKit(html, 'string', configuration=config).to_pdf()
        return pdf

    def get_sms(self, track_id, name):
        t = Tracking.objects.get(track_id = track_id)
        url = reverse('view_report',kwargs={'report_id':t.report_id.link_id,'tracking_id':track_id})
        request = None
        full_url = ''.join(['http://', get_current_site(request).domain, url])
        return self.sms_template.format(name, t.report_id.parameters['gp_name'].title(),full_url)

    def save(self):
        r= Reports(report_type=self._type,parameters=self.params, data=self.data)
        r.link_id = hashlib.sha256(str(random.random()).encode('utf-8')).hexdigest()[:7]
        r.save()
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
    def __init__(self, gp_name=None, academic_year=None, **kwargs):
        self.gp_name = gp_name
        self.academic_year = academic_year
        self.params = dict(gp_name=self.gp_name,academic_year=self.academic_year)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--gp_name', required=True)
        self.parser.add_argument('--academic_year', required=True)
        self._template_path = 'GPMathContestReport.html'
        self._type = 'GPMathContestReport'
        self.sms_template ='Hi {}, We at Akshara Foundation are continuously working to provide Gram panchayat math contest report for {}. Please click the link {}'
        super().__init__(**kwargs)

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.gp_name = arguments.gp_name
        self.academic_year = arguments.academic_year
        self.params = dict(gp_name=self.gp_name,academic_year=self.academic_year)

    def get_data(self):
        print(self.gp_name)
        print(self.academic_year)
        gp = self.gp_name #"peramachanahalli"
        ay = self.academic_year #"2016-2017"

        ay2 = ay.split('-')
        dates = [ay2[0]+'-06-01', ay2[1]+'-03-31'] # [2016-06-01, 2017-03-31]

        report_generated_on = datetime.datetime.now().date().isoformat()

        try:
            gp_obj = Boundary.objects.get(name=gp) # Take the GP from db
        except Boundary.DoesNotExist:
            print('Gram panchayat {} does not exist\n'.format(self.gp_name))
            raise ValueError('Invalid Gram Panchayat name\n')

        block = gp_obj.parent.name           # Block name
        district = gp_obj.parent.parent.name    # District name

        gp_schools = Institution.objects.filter(admin3__name=gp).count() # Number of schools in GP


        # Get the answergroup_institution from gp name and academic year
        AGI = AnswerGroup_Institution.objects.filter(institution__admin3__name=self.gp_name, entered_at__range = dates, respondent_type_id='CH', questiongroup__survey_id=2)
        
        if not AGI.exists():
            raise ValueError("No contests found for {} in the year {}".format(gp, ay))

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


        survey = self.getHouseholdServey(gp, dates)

        self.data =  {'gp_name': gp.title(), 'academic_year': ay, 'block':block, 'district':district.title(),'no_schools_gp':gp_schools,'no_students':number_of_students,'today':report_generated_on,'boys':num_boys,'girls':num_girls,'schools':out,'cs':contest_list,'score_100':score_100,'score_zero':score_zero,'girls_zero':girls_zero,'boys_zero':boys_zero,'boys_100':boys_100,'girls_100':girls_100, 'survey':survey}
        return self.data

    def getHouseholdServey(self,gp_name,date_range):
        #Husehold Survey
        a = AnswerGroup_Institution.objects.filter(institution__admin3__name=gp_name, entered_at__range=date_range, questiongroup_id__in=[18, 20])

        questions = QuestionGroup.objects.get(id=18).questions.all()

        total_response = a.count()

        HHSurvey = []

        for i in questions:
            count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
            count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
            HHSurvey.append({'text':i.question_text,'percentage': round((count/total_response)*100, 2)})

        return HHSurvey

class SchoolReport(BaseReport):
    def __init__(self, school_code=None, academic_year=None, **kwargs):
        self.school_code = school_code
        self.academic_year = academic_year
        self.params = dict(school_code=self.school_code,academic_year=self.academic_year)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--school_code', required=True)
        self.parser.add_argument('--academic_year', required=True)
        self._template_path = 'SchoolReport.html'
        self._type = 'SchoolReport'
        self.sms_template ='Hi {}, We at Akshara Foundation are continuously working to provide Gram panchayat math contest report for {}. Please click the link {}'
        super().__init__(**kwargs)

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.school_code = arguments.school_code
        self.academic_year = arguments.academic_year
        self.params = dict(school_code=self.school_code,academic_year=self.academic_year)

    def get_data(self):
        ay = self.academic_year.split('-')
        dates = [ay[0]+'-06-01', ay[1]+'-03-31'] # [2016-06-01, 2017-03-31]

        report_generated_on = datetime.datetime.now().date().isoformat()

        try:
            school_obj = Institution.objects.get(dise__school_code=self.school_code) # Take the school from db
        except Institution.DoesNotExist:
            print('School {} does not exist\n'.format(self.school_name))
            raise ValueError('Invalid school name\n')

        gp = school_obj.gp.const_ward_name.title() # GP name
        cluster = school_obj.admin3.name.title()         # Cluster name
        block = school_obj.admin2.name.title()           # Block name
        district = school_obj.admin1.parent.name.title()    # District name

        AGI = AnswerGroup_Institution.objects.filter(institution=school_obj, entered_at__range = dates, respondent_type_id='CH', questiongroup__survey_id=2)

        if not AGI.exists():
            raise ValueError("No contests found for {} in the year {}".format(self.school_code, ay))

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

        self.data =  {'gp_name': gp, 'academic_year': self.academic_year, 'cluster':cluster, 'block':block, 'district':district,'no_students':number_of_students,'today':report_generated_on,'boys':num_boys,'girls':num_girls,'schools':out,'cs':contest_list,'score_100':score_100,'score_zero':score_zero,'girls_zero':girls_zero,'boys_zero':boys_zero,'boys_100':boys_100,'girls_100':girls_100}
        return self.data

class ClusterReport(BaseReport):
    def __init__(self, cluster_name=None, academic_year=None, **kwargs):
        self.cluster_name = cluster_name
        self.academic_year = academic_year
        self.params = dict(cluster_name=self.cluster_name,academic_year=self.academic_year)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--cluster_name', required=True)
        self.parser.add_argument('--academic_year', required=True)
        self._template_path = 'ClusterReport.html'
        self._type = 'ClusterReport'
        self.sms_template ='Hi {}, We at Akshara Foundation are continuously working to provide Gram panchayat math contest report for {}. Please click the link {}'
        super().__init__(**kwargs)

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.cluster_name = arguments.cluster_name
        self.academic_year = arguments.academic_year
        self.params = dict(cluster_name=self.cluster_name,academic_year=self.academic_year)

    def get_data(self):
        ay = self.academic_year.split('-')
        dates = [ay[0]+'-06-01', ay[1]+'-03-31'] # [2016-06-01, 2017-03-31]

        report_generated_on = datetime.datetime.now().date().isoformat()

        try:
            cluster_obj = Boundary.objects.get(name=self.cluster_name, boundary_type__char_id='SC') # Take the cluster from db
        except Boundary.DoesNotExist:
            print('Cluster {} does not exist\n'.format(self.cluster_name))
            raise ValueError('Invalid cluster name\n')

        block = cluster_obj.parent.name.title()           # Block name
        district = cluster_obj.parent.parent.name.title()    # District name

        cluster_schools = Institution.objects.filter(admin3=cluster_obj) # schools in GP
        no_of_schools_in_cluster = cluster_schools.count()

        schools = []
        for school in cluster_schools:
            r = SchoolReport(school_code=school.dise.school_code, academic_year=self.academic_year)
            try:
                school_data = r.get_data()['schools']
                schools.append(school_data)
            except ValueError:
                continue

        household = self.getHouseholdServey(cluster_obj, dates)
        gka = self.getGKAData(cluster_obj, dates)

        self.data = {'cluster':self.cluster_name, 'academic_year':self.academic_year, 'block':block, 'district':district, 'no_schools':no_of_schools_in_cluster, 'today':report_generated_on, 'gka':gka, 'household':household, 'schools':schools}
        return self.data

    def getHouseholdServey(self,cluster,date_range):
        #Husehold Survey
        a = AnswerGroup_Institution.objects.filter(institution__admin3=cluster, entered_at__range=date_range, questiongroup_id__in=[18, 20])

        questions = QuestionGroup.objects.get(id=18).questions.all()

        total_response = a.count()

        HHSurvey = []

        for i in questions:
            count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
            count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
            HHSurvey.append({'text':i.question_text,'percentage': round((count/total_response)*100, 2)})

        return HHSurvey

    def getGKAData(self, cluster, date_range):
        GKA = AnswerGroup_Institution.objects.filter(institution__admin3=cluster, entered_at__range=date_range, questiongroup__survey_id=11)
        teachers_trained = GKA.filter(answers__question__question_text__icontains='trained', answers__answer='Yes').count()/GKA.filter(answers__question__question_text__icontains='trained').count()
        kit_usage = GKA.filter(answers__question__question_text__contains='trained', answers__answer='Yes').count()/GKA.filter(answers__question__question_text__icontains='Ganitha Kalika Andolana TLM').count()
        group_work = GKA.filter(answers__question__question_text__contains='trained', answers__answer='Yes').count()/GKA.filter(answers__question__question_text__icontains='group').count()
        return dict(teachers_trained=round(teachers_trained*100, 2),  kit_usage=round(kit_usage*100, 2), group_work=round(group_work*100, 2))

if __name__ == "__main__":
    r= ReportOne();
    r.get_data
