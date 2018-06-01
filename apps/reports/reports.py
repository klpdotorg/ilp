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

    def get_sms(self, track_id, name, param_id):
        t = Tracking.objects.get(track_id = track_id)
        url = reverse('view_report',kwargs={'report_id':t.report_id.link_id,'tracking_id':track_id})
        request = None
        full_url = ''.join(['http://', get_current_site(request).domain, url])
        return self.sms_template.format(name, t.report_id.parameters[param_id].title(),full_url)

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
            print('School {} does not exist\n'.format(self.school_code))
            raise ValueError('Invalid school name\n')

        try:
            gp = school_obj.gp.const_ward_name.title() # GP name
        except AttributeError:
            gp = 'Not Available'
        cluster = school_obj.admin3.name.title()         # Cluster name
        block = school_obj.admin2.name.title()           # Block name
        district = school_obj.admin1.parent.name.title()    # District name

        AGI = AnswerGroup_Institution.objects.filter(institution=school_obj, entered_at__range = dates, respondent_type_id='CH', questiongroup__survey_id=2)

        if not AGI.exists():
            # raise ValueError("No contests found for {} in the year {}".format(self.school_code, ay))
            print("No data school data for {} in academic year {}".format(self.school_code, self.academic_year))
            return {}

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

        neighbour_list = []
        for i in Institution.objects.filter(gp=school_obj.gp):
            neighbour_agi = AnswerGroup_Institution.objects.filter(institution=i, entered_at__range = dates, respondent_type_id='CH', questiongroup__survey_id=2)
            neighbour_list.append(self.get_school_data(neighbour_agi))

        neighbours = self.format_schools_data(neighbour_list)

        self.data =  {'gp_name': gp, 'academic_year': self.academic_year, 'cluster':cluster, 'block':block, 'district':district,'no_students':number_of_students,'today':report_generated_on,'boys':num_boys,'girls':num_girls,'schools':out,'cs':contest_list,'score_100':score_100,'score_zero':score_zero,'girls_zero':girls_zero,'boys_zero':boys_zero,'boys_100':boys_100,'girls_100':girls_100, 'neighbours':neighbours}
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
    def __init__(self, cluster_name=None, block_name=None, academic_year=None, **kwargs):
        self.cluster_name = cluster_name
        self.academic_year = academic_year
        self.block_name = block_name
        self.params = dict(cluster_name=self.cluster_name, block_name=self.block_name, academic_year=self.academic_year)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--cluster_name', required=True)
        self.parser.add_argument('--block_name', required=True)
        self.parser.add_argument('--academic_year', required=True)
        self._template_path = 'ClusterReport.html'
        self._type = 'ClusterReport'
        self.sms_template ='Hi {}, We at Akshara Foundation are continuously working to provide Gram panchayat math contest report for {}. Please click the link {}'
        super().__init__(**kwargs)

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.cluster_name = arguments.cluster_name
        self.block_name = argument.block_name
        self.academic_year = arguments.academic_year
        self.params = dict(cluster_name=self.cluster_name, block_name=self.block_name, academic_year=self.academic_year)

    def get_data(self):
        ay = self.academic_year.split('-')
        dates = [ay[0]+'-06-01', ay[1]+'-03-31'] # [2016-06-01, 2017-03-31]

        report_generated_on = datetime.datetime.now().date().isoformat()

        try:
            cluster_obj = Boundary.objects.get(name=self.cluster_name, parent__name = self.block_name, boundary_type__char_id='SC') # Take the cluster from db
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
                school_data = r.get_data()
                if not school_data:
                  continue
                schools.append(school_data['schools'][0])
            except ValueError:
                continue

        household = self.getHouseholdServey(cluster_obj, dates)
        gka = self.getGKAData(cluster_obj, dates)

        self.data = {'cluster':self.cluster_name, 'academic_year':self.academic_year, 'block':block, 'district':district, 'no_schools':no_of_schools_in_cluster, 'today':report_generated_on, 'gka':gka, 'household':household, 'schools':schools}
        return self.data

    def getHouseholdServey(self,cluster,date_range):
        #Husehold Survey
        a = AnswerGroup_Institution.objects.filter(institution__admin3=cluster, entered_at__range=date_range, questiongroup_id__in=[18, 20])
        HHSurvey = []
        if a.exists():
            questions = QuestionGroup.objects.get(id=18).questions.all()

            total_response = a.count()

            for i in questions:
                count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
                count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
                # try:
                HHSurvey.append({'text':i.question_text,'percentage': round((count/total_response)*100, 2)})
                # except ZeroDivisionError:
                #     HHSurvey.append({'text':i.question_text,'percentage':0.0})
        else:
             print("No HH data for CLUSTER {} in {} block for academic year {}".format(cluster.name, cluster.parent.name, self.academic_year))
        return HHSurvey

    def getGKAData(self, cluster, date_range):
        GKA = AnswerGroup_Institution.objects.filter(institution__admin3=cluster, entered_at__range=date_range, questiongroup__survey_id=11)
        if GKA.exists():
            teachers_trained = GKA.filter(answers__question__question_text__icontains='trained', answers__answer='Yes').count()/GKA.filter(answers__question__question_text__icontains='trained').count()
            kit_usage = GKA.filter(answers__question__question_text__contains='trained', answers__answer='Yes').count()/GKA.filter(answers__question__question_text__icontains='Ganitha Kalika Andolana TLM').count()
            group_work = GKA.filter(answers__question__question_text__contains='trained', answers__answer='Yes').count()/GKA.filter(answers__question__question_text__icontains='group').count()
            return dict(teachers_trained=round(teachers_trained*100, 2),  kit_usage=round(kit_usage*100, 2), group_work=round(group_work*100, 2))
        else:
            print("No GKA data for CLUSTER {} in {} block for academic year {}".format(cluster.name, cluster.parent.name, self.academic_year))
            return {}

class BlockReport(BaseReport):
    def __init__(self, block_name=None, academic_year=None, **kwargs):
        self.block_name = block_name
        self.academic_year = academic_year
        self.params = dict(block_name=self.block_name,academic_year=self.academic_year)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--block_name', required=True)
        self.parser.add_argument('--academic_year', required=True)
        self._template_path = 'BlockReport.html'
        self._type = 'BlockReport'
        self.sms_template ='Hi {}, We at Akshara Foundation are continuously working to provide Gram panchayat math contest report for {}. Please click the link {}'
        super().__init__(**kwargs)

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.block_name = arguments.block_name
        self.academic_year = arguments.academic_year
        self.params = dict(block_name=self.block_name,academic_year=self.academic_year)

    def get_data(self):

        ay = self.academic_year.split('-')
        dates = [ay[0]+'-06-01', ay[1]+'-03-31'] # [2016-06-01, 2017-03-31]

        report_generated_on = datetime.datetime.now().date().isoformat()

        try:
            block = Boundary.objects.get(name=self.block_name, boundary_type__char_id='SB') # Take the block from db
        except Boundary.DoesNotExist:
            print('Block {} does not exist\n'.format(self.block_name))
            raise ValueError('Invalid block name\n')

        district = block.parent.parent.name.title()    # District name

        clusters  = Boundary.objects.filter(parent=block) # Clusters that belong to the block
        num_clusters = clusters.count()

        num_schools = 0
        teachers_trained, kit_usage, group_work = 0, 0, 0
        gka_clusters = []
        gpc_clusters = []

        for cluster in clusters:
            # Aggregating number of schools and gka data
            r = ClusterReport(cluster_name=cluster.name, block_name=block.name, academic_year=self.academic_year)
            data = r.get_data()
            num_schools += data['no_schools']
            cluster_gka = data['gka']
            if cluster_gka:
                teachers_trained += cluster_gka['teachers_trained']
                kit_usage += cluster_gka['kit_usage']
                group_work += cluster_gka['group_work']
                cluster_gka['cluster'] = cluster.name
                gka_clusters.append(cluster_gka)
            else:
                print("No GKA data for CLUSTER {} in block {} for academic year {}".format(cluster.name, block.name, self.academic_year))
            # Aggregating GP contest data
            gpc_data = data['schools']
            if gpc_data:
                cluster_gpc = {'grades': [{'name': 'Class 4 Assessment',
                                           'values': [{'contest': 'Addition', 'count': 0},
                                                      {'contest': 'Division', 'count': 0},
                                                      {'contest': 'Multiplication', 'count': 0},
                                                      {'contest': 'Number Concept', 'count': 0},
                                                      {'contest': 'Subtraction', 'count': 0},
                                                      {'contest': 'Other Areas', 'count': 0}]},
                                          {'name': 'Class 5 Assessment',
                                           'values': [{'contest': 'Addition', 'count': 0},
                                                      {'contest': 'Division', 'count': 0},
                                                      {'contest': 'Multiplication', 'count': 0},
                                                      {'contest': 'Number Concept', 'count': 0},
                                                      {'contest': 'Subtraction', 'count': 0},
                                                      {'contest': 'Other Areas', 'count': 0}]},
                                          {'name': 'Class 6 Assessment',
                                           'values': [{'contest': 'Addition', 'count': 0},
                                                      {'contest': 'Division', 'count': 0},
                                                      {'contest': 'Multiplication', 'count': 0},
                                                      {'contest': 'Number Concept', 'count': 0},
                                                      {'contest': 'Subtraction', 'count': 0},
                                                      {'contest': 'Other Areas', 'count': 0}]}],
                               'cluster': cluster.name}
                schools_in_data = len(gpc_data)
                for school in gpc_data:
                    if len(school['grades']) == 2:
                        school['grades'].append({'name': 'Class 6 Assessment',
                                                 'values': [{'contest': 'Addition', 'count': 100},
                                                            {'contest': 'Division', 'count': 100},
                                                            {'contest': 'Multiplication', 'count': 100},
                                                            {'contest': 'Number Concept', 'count': 100},
                                                            {'contest': 'Subtraction', 'count': 100},
                                                            {'contest': 'Other Areas', 'count': 100}]})
                    for i,j in zip(cluster_gpc['grades'], school['grades']):
                        for k,l in zip(i['values'], j['values']):
                            k['count']+=l['count']
                for grade in cluster_gpc['grades']:
                    for value in grade['values']:
                        value['count'] = round((value['count']/schools_in_data), 2)
                gpc_clusters.append(cluster_gpc)
            else:
                print("No GPC data for CLUSTER {} in block {} for academic year {}".format(cluster.name, block.name, self.academic_year))

        gka = dict(teachers_trained=round(teachers_trained/num_clusters, 2),  kit_usage=round(kit_usage/num_clusters, 2), group_work=round(group_work/num_clusters, 2))
        household = self.getHouseholdServey(block, dates)
        self.data = {'block':self.block_name.title(), 'district':district, 'academic_year':self.academic_year, 'today':report_generated_on, 'no_schools':num_schools, 'gka':gka, 'gka_clusters':gka_clusters, 'gpc_clusters':gpc_clusters, 'household':household}
        return self.data

    def getHouseholdServey(self,block,date_range):
        #Husehold Survey
        a = AnswerGroup_Institution.objects.filter(institution__admin2=block, entered_at__range=date_range, questiongroup_id__in=[18, 20])
        HHSurvey = []
        if a.exists():
            questions = QuestionGroup.objects.get(id=18).questions.all()

            total_response = a.count()

            for i in questions:
                count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
                count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
                # try:
                HHSurvey.append({'text':i.question_text,'percentage': round((count/total_response)*100, 2)})
                # except ZeroDivisionError:
                #     HHSurvey.append({'text':i.question_text,'percentage':0.0})
        else:
             print("No HH data for BLOCK {} in {} District for academic year {}".format(block.name, block.parent.name, self.academic_year))
        return HHSurvey

class DistrictReport(BaseReport):
    def __init__(self, district_name=None, academic_year=None, **kwargs):
        self.district_name = district_name
        self.academic_year = academic_year
        self.params = dict(district_name=self.district_name,academic_year=self.academic_year)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--district_name', required=True)
        self.parser.add_argument('--academic_year', required=True)
        self._template_path = 'DistrictReport.html'
        self._type = 'DistrictReport'
        self.sms_template ='Hi {}, We at Akshara Foundation are continuously working to provide Gram panchayat math contest report for {}. Please click the link {}'
        super().__init__(**kwargs)

    def parse_args(self, args):
        arguments = self.parser.parse_args(args)
        self.distrct_name = arguments.district_name
        self.academic_year = arguments.academic_year
        self.params = dict(district_name=self.district_name,academic_year=self.academic_year)

    def get_data(self):

        ay = self.academic_year.split('-')
        dates = [ay[0]+'-06-01', ay[1]+'-03-31'] # [2016-06-01, 2017-03-31]

        report_generated_on = datetime.datetime.now().date().isoformat()

        district = Boundary.objects.get(name=self.district_name, boundary_type__char_id='SD')

        AGI = AnswerGroup_Institution.objects.filter(institution__admin1=district, entered_at__range = dates, respondent_type_id='CH', questiongroup__survey_id=2)

        num_boys = AGI.filter(answers__question__key='Gender', answers__answer='Male').count()
        num_girls = AGI.filter(answers__question__key='Gender', answers__answer='Female').count()
        number_of_students = num_boys + num_girls
        num_contests = AGI.values_list('answers__question__key', flat=True).distinct().count()

        blocks  = Boundary.objects.filter(parent=district) # Blocks that belong to the district
        num_blocks = blocks.count()

        num_schools = 0
        teachers_trained, kit_usage, group_work = 0, 0, 0
        gka_blocks = []
        gpc_blocks = []
        gpc_grades = {'Class 4 Assessment':{}, 'Class 5 Assessment':{}, 'Class 6 Assessment':{}}
        for block in blocks:
            # Aggregating number of schools and gka data
            r = BlockReport(block_name=block.name, academic_year=self.academic_year)
            data = r.get_data()
            num_schools += data['no_schools']
            block_gka = data['gka']
            if block_gka:
                teachers_trained += block_gka['teachers_trained']
                kit_usage += block_gka['kit_usage']
                group_work += block_gka['group_work']
                block_gka['block'] = block.name
                gka_blocks.append(block_gka)
            else:
                print("No GKA data for BLOCK {} for academic year {}".format(block.name, self.academic_year))

            gpc_data = data['gpc_clusters']
            if gpc_data:
                block_gpc = {'grades': [{'name': 'Class 4 Assessment',
                                           'values': [{'contest': 'Addition', 'count': 0},
                                                      {'contest': 'Division', 'count': 0},
                                                      {'contest': 'Multiplication', 'count': 0},
                                                      {'contest': 'Number Concept', 'count': 0},
                                                      {'contest': 'Subtraction', 'count': 0},
                                                      {'contest': 'Other Areas', 'count': 0}]},
                                          {'name': 'Class 5 Assessment',
                                           'values': [{'contest': 'Addition', 'count': 0},
                                                      {'contest': 'Division', 'count': 0},
                                                      {'contest': 'Multiplication', 'count': 0},
                                                      {'contest': 'Number Concept', 'count': 0},
                                                      {'contest': 'Subtraction', 'count': 0},
                                                      {'contest': 'Other Areas', 'count': 0}]},
                                          {'name': 'Class 6 Assessment',
                                           'values': [{'contest': 'Addition', 'count': 0},
                                                      {'contest': 'Division', 'count': 0},
                                                      {'contest': 'Multiplication', 'count': 0},
                                                      {'contest': 'Number Concept', 'count': 0},
                                                      {'contest': 'Subtraction', 'count': 0},
                                                      {'contest': 'Other Areas', 'count': 0}]}],
                               'block': block.name}
                clusters_in_data = len(gpc_data)
                for cluster in gpc_data:
                    # if len(school['grades']) == 2:
                    #     school['grades'].append({'name': 'Class 6 Assessment',
                    #                              'values': [{'contest': 'Addition', 'count': 100},
                    #                                         {'contest': 'Division', 'count': 100},
                    #                                         {'contest': 'Multiplication', 'count': 100},
                    #                                         {'contest': 'Number Concept', 'count': 100},
                    #                                         {'contest': 'Subtraction', 'count': 100},
                    #                                         {'contest': 'Other Areas', 'count': 100}]})
                    for i,j in zip(block_gpc['grades'], cluster['grades']):
                        for k,l in zip(i['values'], j['values']):
                            k['count']+=l['count']
                for grade in block_gpc['grades']:
                    for value in grade['values']:
                        value['count'] = round((value['count']/clusters_in_data), 2)
                gpc_blocks.append(block_gpc)
            else:
                print("No GPC data for BLOCK {} for academic year {}".format(block.name, self.academic_year))

        gka = dict(teachers_trained=round(teachers_trained/num_blocks, 2),  kit_usage=round(kit_usage/num_blocks, 2), group_work=round(group_work/num_blocks, 2))
        household = self.getHouseholdServey(district, dates)

        #GPC Gradewise data
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

        self.data = {'academic_year':self.academic_year, 'today':report_generated_on, 'district':self.district_name.title(), 'gka':gka, 'gka_blocks':gka_blocks, 'no_schools':num_schools, 'gpc_blocks':gpc_blocks, 'household':household, 'num_boys':num_boys, 'num_girls':num_girls, 'num_students':number_of_students, 'num_contests':num_contests, 'gpc_grades':gradewise_gpc}
        return self.data

    def getHouseholdServey(self,district,date_range):
        #Husehold Survey
        a = AnswerGroup_Institution.objects.filter(institution__admin1=district, entered_at__range=date_range, questiongroup_id__in=[18, 20])
        HHSurvey = []
        if a.exists():
            questions = QuestionGroup.objects.get(id=18).questions.all()

            total_response = a.count()

            for i in questions:
                count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
                count = a.filter(answers__question__question_text=i.question_text, answers__answer='Yes').count()
                # try:
                HHSurvey.append({'text':i.question_text,'percentage': round((count/total_response)*100, 2)})
                # except ZeroDivisionError:
                #     HHSurvey.append({'text':i.question_text,'percentage':0.0})
        else:
             print("No HH data for District {} for academic year {}".format(block.name, block.parent.name, self.academic_year))
        return HHSurvey

if __name__ == "__main__":
    r= ReportOne();
    r.get_data
