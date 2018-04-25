from abc import ABC, abstractmethod
from jinja2 import Environment, FileSystemLoader
import pdfkit
import os.path

from assessments import models as assess_models
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
    
