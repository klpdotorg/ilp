from abc import ABC, abstractmethod
from jinja2 import Environment, FileSystemLoader
import pdfkit
import os.path
import datetime

from boundary.models import Boundary
from assessments.models import SurveyInstitutionAgg
from schools.models import Institution
from assessments import models as assess_models
from assessments.models import AnswerGroup_Institution
from .models import Reports

class BaseReport(ABC):

    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def get_html(self):
        pass

    @abstractmethod
    def get_pdf(self):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def generate(self):
        pass

class ReportOne(BaseReport):
    def __init__(self, from_date, to_date):
        self.from_date = from_date
        self.to_date = to_date

    def get_data(self):
#        return assess_models.AnswerGroup_Institution.objects.all()[:5]
        return ['name','some','dfdfdfa','dfdafad']

    def get_html(self, output_name):
        env = Environment(loader=FileSystemLoader('apps/reports/report_templates'))
        template = env.get_template('report_one.html')
        data = self.get_data();
        html = template.render(data=data)

        with open('apps/reports/output/{}.html'.format(output_name), 'w') as out_file:
            out_file.write(html)

    def get_pdf(self,output_name):
        if not os.path.exists('apps/reports/output/{}.html'.format(output_name)):
            self.get_html(output_name)
        pdfkit.from_file('apps/reports/output/{}.html'.format(output_name), 'apps/reports/reports_pdf/{}.pdf'.format(output_name))

    def save(self):
        r= Reports(report_type="reportOne",parameters=dict(from_date=self.from_date,to_date=self.to_date))
        r.save()

    def generate(self, report_type, output_name):
        if report_type == 'html':
            self.get_html(output_name)
        elif report_type == 'pdf':
            self.get_pdf(output_name)
        else:
            raise AttributeError('Invalid report format')

class GPMathContestReport(BaseReport):
    def __init__(self, gp_name,academic_year):
        self.gp_name = gp_name
        self.academic_year = academic_year

    def get_data(self):
        print(self.gp_name)
        print(self.academic_year)
        gp = self.gp_name #"peramachanahalli"
        ay = self.academic_year #"2016-2017"

        ay2 = ay.split('-')
        dates = [int(ay2[0]+'06'), int(ay2[1]+'03')] # [201606, 201703]

        report_generated_on = datetime.datetime.now().date()

        try:
            gp_obj = Boundary.objects.get(name=gp) # Take the GP from db
        except Boundary.DoesNotExist:
            print('Gram panchayat {} does not exist'.format(self.gp_name))
            raise ValueError('Invalid Gram Panchayat name')

        block = gp_obj.parent.name           # Block name
        district = gp_obj.parent.parent.name    # District name

        contests = SurveyInstitutionAgg.objects.filter(institution_id__admin3__name = gp, yearmonth__range=dates)

        contest_schools = contests.values('institution_id').distinct().count() # Number of schools in the report
        gp_schools = Institution.objects.filter(admin3__name=gp).count() # Number of schools in GP


        # Get the answergroup_institution from gp name and academic year
        AGI = AnswerGroup_Institution.objects.filter(institution__admin3__name="krishnanagara", entered_at__range = ["2017-06-01", "2018-03-31"], respondent_type_id='CH')

        students = 0
        num_boys = 0
        num_girls = 0
        # Assumes that no student has taken multiple tests
        for i in AGI:
            gender_qstns = i.answers.filter(question__key='Gender')
            num_boys += gender_qstns.filter(answer='Male').count()
            num_girls += gender_qstns.filter(answer='Female').count()

        students = num_boys+num_girls
        return {'gp_name': gp, 'academic_year': ay, 'block':block, 'district':district,'no_schools_gp':gp_schools,'no_students':students,'today':report_generated_on,'boys':num_boys,'girls':num_gilrs}


    def get_html(self, output_name):
        env = Environment(loader=FileSystemLoader('apps/reports/report_templates'))
        template = env.get_template('math_contest_report.html')
        data = self.get_data();
        html = template.render(data=data)

        with open('apps/reports/output/{}.html'.format(output_name), 'w') as out_file:
            out_file.write(html)

    def get_pdf(self,output_name):
        if not os.path.exists('apps/reports/output/{}.html'.format(output_name)):
            self.get_html(output_name)
        pdfkit.from_file('apps/reports/output/{}.html'.format(output_name), 'apps/reports/reports_pdf/{}.pdf'.format(output_name))

    def save(self):
        r= Reports(report_type="GPMathContestReport",parameters=dict(gp_name=self.gp_name,academic_year=self.academic_year))
        r.save()

    def generate(self, report_type, output_name):
        if report_type == 'html':
            self.get_html(output_name)
        elif report_type == 'pdf':
            self.get_pdf(output_name)
        else:
            raise ValueError('Invalid report format')

class ReportTwo(BaseReport):

    def get_data(self):
        return self.value * 42

    def get_html(self):
        return "jgfdjh"

    def get_pdf(self):
         return "jgfdjh"

    def save(self):
        return "iwjhyqh"

    def generate(self, report_type, output_name):
        return 'success'

if __name__ == "__main__":
    r= ReportOne();
    r.get_data
