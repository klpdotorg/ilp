import datetime
import argparse

from datetime import datetime, timedelta
from common.utils import post_to_slack, Date
from django.db import transaction
from django.db.models import Count
from django.core.management.base import BaseCommand

from schools.models import Institution

from assessments.models import (
    Survey,AnswerGroup_Institution,QuestionGroup,
    SurveyTagMapping, 
)

class Command(BaseCommand):
    args = ""
    help = """Posts the status of ILP Konnect to Slack.
    ./manage.py konnectstatus --reportdate=YYYY-MM-DD"""
    
    def add_arguments(self, parser):
        parser.add_argument('--reportdate', help='report date')
    

    def get_reportdate(self, report_date):
        date = Date()
        sane = date.check_date_sanity(report_date)
        if not sane:
            print( """
            Error:
            Wrong --from format. Expected YYYY-MM-DD
            """)
            print (self.help)
            return
        else:
            report_date = date.get_datetime(report_date)
        return (report_date)

    @transaction.atomic
    def handle(self, *args, **options):
        report_date = options.get('reportdate', None)
        if not report_date:
            print ("Please specify report date")
            sys.exit()
        report_date = self.get_reportdate(report_date)
        surveytag = SurveyTagMapping.objects.all()
        konnectsurveys = surveytag.filter(tag_id='konnect')
        survey_ids = konnectsurveys.values_list('survey_id', flat=True)

        for s_id in survey_ids:
            survey_name = Survey.objects.filter(id=s_id).values('name')[0]['name']
            questiongroup = QuestionGroup.objects.filter(survey_id=s_id)
            qestgrp_ids = questiongroup.values_list('id', flat=True)
            ansgrps = AnswerGroup_Institution.objects.filter(date_of_visit__gte =report_date).filter(questiongroup_id__in=qestgrp_ids)
            konnect_devices = ansgrps.aggregate(Count('mobile', distinct = True))['mobile__count']
            konnect_schools = ansgrps.aggregate(Count('institution', distinct = True))['institution__count']
            print("Survey_name:",survey_name)            
            print("Total_count:",ansgrps.count())
            print("Total_devices:",konnect_devices)
            print("Total_schools:",konnect_schools)

            author = 'ILP Konnect'
            emoji = ':memo:'
            try:
                post_to_slack(
                    channel='#klp',
                    author=author,
                    message='%s: %s Schools, %s Devices and %s Surveys' %(survey_name, konnect_schools, konnect_devices, ansgrps.count()),
                    emoji=emoji,
                )
            except:
                print ("could not post to slack")
                pass

        
