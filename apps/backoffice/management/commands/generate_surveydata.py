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
        parser.add_argument('--skipxls', action='store_true', help='Skip creating an excel version')
        parser.add_argument('--from', nargs='?')
        parser.add_argument('--to', nargs='?')
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
        # Add validations for district/block/cluster etc..
        self.district = options.get('districtid', None)
        self.block = options.get('blockid', None)
        self.cluster = options.get('clusterid', None)
        self.startyearmonth = options.get('startyearmonth', None)
        self.endyearmonth = options.get('endyearmonth', None)
        return True
        

    def handle(self, *args, **options):
        if not self.validateParams(options):
            return
        survey_id = options.get('surveyid')
        from_yearmonth = options.get('from', None)
        to_yearmonth = options.get('to', None)
        skip_xls_creation = options.get('skipxls', False)
        #If no to_date is specified, then assume today is the last
        if from_yearmonth is not None and to_yearmonth is None:
            today = date.today()
            year = str(today.year)
            month = str(today.month)
            to_yearmonth = year + month
       
        now = date.today()
        if options.get('filename'):
            filename = options.get('filename')
        else:
            filename = self.surveyinfo.name.replace(' ', '') # + "_" + str(now)
        self.dumpData(self.surveyinfo, from_yearmonth, to_yearmonth, filename, skip_xls_creation)
        return filename
