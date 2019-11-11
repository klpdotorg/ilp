from datetime import date

from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from easyaudit.models import CRUDEvent
from users.models import User
from backoffice.surveyutils import utilsData


class Command(BaseCommand, utilsData.commonAssessmentDataUtils):
    help = 'Gets entered data for a survey'
    surveyinfo = None

    def add_arguments(self, parser):
        parser.add_argument('surveyid')
        parser.add_argument('filename', nargs='?')
        parser.add_argument('--startyearmonth', nargs='?')
        parser.add_argument('--endyearmonth', nargs='?')
        parser.add_argument('--districtid', nargs='?')
        parser.add_argument('--blockid', nargs='?')
        parser.add_argument('--clusterid', nargs='?')
        parser.add_argument('--schoolid', nargs='?')
        parser.add_argument('--gpid', nargs='?')

    def validateParams(self, options):
        self.surveyinfo = self.validateSurvey(options.get('surveyid',None))
        if self.surveyinfo == None:
            print("Pass valid surveyid")
            return False
        return True
        

    def handle(self, *args, **options):
        if not self.validateParams(options):
            return

        questioninfo, numquestions = self.getQuestionData(options.get('surveyid'))
        if questioninfo == None:
            return
        from_date = options.get('from', None)
        to_date = options.get('to', None)
        #If no to_date is specified, then assume today is the last
        if to_date is None:
            to_date = date.today()
        assessmentdata = self.getAssessmentData(self.surveyinfo, questioninfo, from_date, to_date)
        now = date.today()
        if options.get('filename'):
            filename = options.get('filename')
        else:
            filename = self.surveyinfo.name.replace(' ','')+"_"+str(now)
        self.createXLS(self.surveyinfo, questioninfo, numquestions, assessmentdata, filename)
        return filename
