from os import sys
import psycopg2
import datetime
import os
import inspect
import csv
from django.core.management.base import BaseCommand
from schools.models import Institution
from assessments.models import SurveyTag, SurveyTagInstitutionMapping
from common.models import AcademicYear
from dise.models import BasicData
from django.conf import settings



class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--survey_tag', type=str)
        parser.add_argument(
            '--acadyear',
            help='Academic year for which mapping has to happen', type=str)
        parser.add_argument(
            '-f', '--file',
            help='CSV file with institution DISE codes'
        )

    def handle(self, *args, **options):
        csvfile = options['file']
        academic_year_id = options['acadyear']
        survey_tag_id = options['survey_tag']
        f = open(csvfile, 'r')
        csv_f = csv.reader(f)
        count = 0

        # Validate the survey tag
        try:
            tag = SurveyTag.objects.get(char_id=survey_tag_id)
        except SurveyTag.DoesNotExist:
            print("Invalid surveytag: " + survey_tag_id)
            return

        # Validate the academic year
        try:
            academic_year = AcademicYear.objects.get(char_id=academic_year_id)
        except AcademicYear.DoesNotExist:
            print("Invalid Academic Year: ", academic_year_id)
            return
        dise_acad_year = settings.DISE_ACADEMIC_YEAR
        dise_acad_year = dise_acad_year.replace('-','')
        instmap = []
        # Start mapping the KLP ID of schools to survey tag
        for file_row in csv_f:
            data = file_row[0].strip("'")
            data = int(data.strip())
            try:
                school = Institution.objects.filter(dise__academic_year=settings.DISE_ACADEMIC_YEAR).get(dise__school_code=data)
            except Institution.DoesNotExist:
                print("School with DISE code %s does not exist" %data)
            else:
                stinst, created = SurveyTagInstitutionMapping.objects.get_or_create(
                                                institution = school,
                                                tag = tag,
                                                academic_year=academic_year)
                if created:
                    instmap.append(stinst)
                else:
                    pass
                    # print("School already mapped")
                
        print("%s schools successfully mapped" % len(instmap))
        print("Exiting...")
