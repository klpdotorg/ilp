import csv
import sys
from io import StringIO

from django.utils import timezone
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from assessments.models import SurveyTag, SurveyTagInstitutionMapping
from common.models import AcademicYear
from boundary.models import Boundary
from schools.models import Institution


class Command(BaseCommand):
   
    help = """python3 manage.py map_surveytag_institution [surveytag='gka'] [boundary=8000,8001] [academic_year=1819]"""

    def add_arguments(self, parser):
        parser.add_argument('surveytag')
        parser.add_argument('boundary')
        parser.add_argument('academic_year')

    def handle(self, *args, **options):
        surveytag = options['surveytag']
        #surveytag = options.get('surveytag')
        boundary_ids = options.get('boundary')
        year = options.get('academic_year')

        try:
            tag = SurveyTag.objects.get(char_id=surveytag)
        except SurveyTag.DoesNotExist:
            print("Invalid surveytag: "+surveytag)
            return

        boundaries = []
        for b in boundary_ids.split(','):
            try:
                print(b)
                boundaries.append(Boundary.objects.get(id=b))
            except Boundary.DoesNotExist:    
                print("Invalid Boundary: "+b)
                return

        try:
            academic_year = AcademicYear.objects.get(char_id=year)
        except AcademicYear.DoesNotExist:
            print("Invalid Academic Year: "+year)
            return

        try:
            institutions = Institution.objects.filter(Q(admin0_id__in = boundaries) | Q(admin1_id__in = boundaries) | Q(admin2_id__in = boundaries) | Q(admin3_id__in=boundaries))
        except Institution.DoesNotExist:
            print("No institutions found for boundary: "+boundaries)


        print(institutions.count())
        for institution in institutions:
            SurveyTagInstitutionMapping.objects.create(
                institution = institution,
                tag = tag,
                academic_year = academic_year)
