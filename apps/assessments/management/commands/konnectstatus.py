import datetime
import argparse
import sys

from datetime import datetime, timedelta
from common.utils import post_to_slack, Date
from django.db import transaction
from django.db.models import Count
from django.core.management.base import BaseCommand

from schools.models import Institution
from assessments.models import (
    Survey,AnswerGroup_Institution,QuestionGroup,
    SurveyTagMapping, AnswerGroup_Institution)
from boundary.models import Boundary
from users.models import User


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
        gka_flag = False

        for s_id in survey_ids:
            survey_name = Survey.objects.filter(id=s_id).values('name')[0]['name']
            questiongroup = QuestionGroup.objects.filter(survey_id=s_id)
            questgrp_ids = questiongroup.values_list('id', flat=True)
            ansgrps = AnswerGroup_Institution.objects.filter(date_of_visit__gte =report_date).filter(questiongroup_id__in=questgrp_ids)
            assess_survey = Survey.objects.filter(id=s_id)
            admin_id = assess_survey.values_list('admin0', flat=True)
            boundary_name = Boundary.objects.filter(id__in=admin_id).values('name')[0]['name']
            konnect_devices = ansgrps.aggregate(Count('mobile', distinct = True))['mobile__count']
            konnect_schools = ansgrps.aggregate(Count('institution', distinct = True))['institution__count']
            print("survey_name:", survey_name)
            print("boundary_name:",boundary_name )
            print("konnect_schools:",konnect_schools )
            print("konnect_devices:",konnect_devices)
            print("Surveys:", ansgrps.count())
            if s_id in (11,14):
                gka_flag = True

            if gka_flag: 
                user_types = ['CRP', 'AS', 'HM']
                CRP_count = ansgrps.filter(respondent_type = 'CRP').count()  
                AS_count = ansgrps.filter(respondent_type = 'AS').count()
                HM_count = ansgrps.filter(respondent_type = 'HM').count()
                other_count = ansgrps.exclude(respondent_type__in = user_types).count()
                print("CRP_count", CRP_count)
                print("AS_count", AS_count)
                print("HM_count", HM_count)
                print("other_count", other_count)
            author = 'ILP Konnect'
            emoji = ':memo:'
            try:
                post_to_slack(
                    channel='#klp',
                    author=author,
                    message='%s: %s: %s Schools, %s Devices and %s Surveys' %(boundary_name,survey_name, konnect_schools, konnect_devices, ansgrps.count()),
                    emoji=emoji,
                )
            except:
                print ("could not post to slack")
                pass

            if gka_flag:
                try:
                    post_to_slack(
                    channel='#klp',
                    author=author,
                    message='GKA Monitoring: %s Surveys - %s by CRP, %s by AS, %s by HM and %s by others' %( konnect_count, CRP_count, AS_count, HM_count, other_count ),
                    emoji=emoji,
                )
                except:
                    print ("could not post to slack")
                    pass
            gka_flag = False
        
