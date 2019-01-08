import csv

from django.core.management.base import BaseCommand

from assessments.models import Survey
from backoffice.utils import (
    get_assessment_field_data, get_assessment_field_names
)


class Command(BaseCommand):
    help = 'Generates CSV dump for assessment data'

    def handle(self, *args, **options):
        survey = Survey.objects.get(id=11)
        field_names = get_assessment_field_names(survey=survey)
        field_data_dict = get_assessment_field_data(survey=survey)

        with open('assessment_csv_dump.csv', mode='w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writeheader()
            for field_data in field_data_dict:
                writer.writerow(field_data)
