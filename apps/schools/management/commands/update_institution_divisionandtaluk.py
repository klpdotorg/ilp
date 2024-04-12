import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from boundary.models import Boundary
from schools.models import Institution


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('filename')

    def handle(self, *args, **options):
        file_name = options['filename']

        if not file_name:
            self.stdout.write(self.style.ERROR("Please specify a filename with the --filename argument"))
            return False

        with open(file_name, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                gp_id = row['gp_id']
                taluk_id = row['taluk_id']
                division_id = row['division_id']

                institutions = Institution.objects.filter(gp_id=gp_id)
                if institutions.exists():
                    for institution in institutions:
                        institution.admin4 = Boundary.objects.get(id=taluk_id)
                        institution.admin5 = Boundary.objects.get(id=division_id)
                        institution.save()
                    self.stdout.write(self.style.SUCCESS(
                        f"Updated admin4_id and admin5_id for {institutions.count()} Institution(s) with gp_id {gp_id}"))
                else:
                    self.stdout.write(self.style.WARNING(f"No Institution found with gp_id {gp_id}"))
