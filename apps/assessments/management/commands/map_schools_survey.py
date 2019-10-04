from os import sys
import psycopg2
import datetime
import os
import inspect
import csv
from django.core.management.base import BaseCommand
from schools.models import Institution
from dise.models import BasicData

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--survey_tag', type=str)
        parser.add_argument(
            '--acadyear',
            help='Academic year for which mapping has to happen')
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
        for file_row in csv_f:
            data = file_row[0].strip("'")
            data = int(data.strip())
            print("dise code is: ", data)
            try:
                school = Institution.models.filter(dise__academic_year='1617').get(dise__school_code=data)
            catch Institution.DoesNotExist:
                print("School with DISE code %s does not exist" %)
            else:
                surveytag_school_mapping = \
                    SurveyTagInstitutionMapping(tag=survey_tag_id, institution=school.id, academic_year=str(academic_year_id))
                try:
                    surveytag_school_mapping.save()
                except Exception:
                    print("Problem mapping institution %s to %s for academic year %s" % (school.id, survey_tag_id, academic_year_id))
                else:
                    count = count+1
        print("%s schools successfully mapped" % count)
        print("Exiting...")
