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
        parser.add_argument('academic_year')
        parser.add_argument('institutions')

    def handle(self, *args, **options):
        surveytag = options.get('surveytag')
        year = options.get('academic_year')
        fname = options.get('institutions', None)
        f = open(fname, encoding='utf-8')
        institutions_file = csv.reader(f,delimiter='|')
 
        try:
            tag = SurveyTag.objects.get(char_id=surveytag)
        except SurveyTag.DoesNotExist:
            print("Invalid surveytag: "+surveytag)
            return

        try:
            academic_year = AcademicYear.objects.get(char_id=year)
        except AcademicYear.DoesNotExist:
            print("Invalid Academic Year: "+year)
            return

        instmap = []
        for row in institutions_file:
            try:
                institution = Institution.objects.get(pk=row[0])
            except Institution.DoesNotExist:
                print("No institutions found with id: "+row[0])
            else:
                stinst, created = SurveyTagInstitutionMapping.objects.get_or_create(
                                                institution = institution,
                                                tag = tag,
                                                academic_year = academic_year)
                instmap.append(stinst)
        print("Number of Institutions tagged with %s: %d" %(surveytag,len(instmap)))
