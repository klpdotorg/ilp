import os
import sys
import csv
import re
from django.core.management.base import BaseCommand
from django.core.exceptions import MultipleObjectsReturned
from django.db import transaction
from django.conf import settings
from common.models import Status
from boundary.models import ElectionBoundary, BoundaryType
from dise.models import BasicData
from schools.models import Institution


class Command(BaseCommand):
    active_status = Status.objects.get(char_id='AC')
    disecode = 9
    schoolid = 8
    schoolname = 6
    village = 10
    villageNewMapped = []
    villageAlreadyMapped = []
    villageMapCheck = []
    
    def add_arguments(self, parser):
        parser.add_argument('--filename')
    
    def handle(self, *args, **options):
        file_name = options['filename']
        if not file_name:
            print("Please specify a filename with the --filename argument")
            return False
        self.parseFile(file_name)
        self.printData()
        
    def validateSchool(self, count, row, disecode, schoolname):
        try:
            school = Institution.objects.get(
                    dise__school_code=disecode)
            return school
        except Institution.DoesNotExist:
            print(str(count)+"|"+str(row)+"| Error: Institution object does not exist")
            return None


    def assignVillage(self, school, village):
        if school.village is None or school.village is "":
            self.villageNewMapped.append({school.id: village})
            school.village = village
            school.save()
            return True
        if school.village.lower() == village.lower():
            self.villageAlreadyMapped.append({school.id: village})
            return False
        else:
            self.villageMapCheck.append({school.id: village})
            return False

    def parseFile(self, file_name):
        f = open(file_name, encoding='utf-8')
        file_reader = csv.reader(f, delimiter=',')
        count = 0
        for row in file_reader:
            if count == 0:
                count += 1
                continue
            count += 1
            schoolid = row[self.schoolid]
            village = row[self.village].strip().lower()
            disecode = row[self.disecode]
            schoolname = row[self.schoolname].strip().lower()

            school = self.validateSchool(count, row, disecode, schoolname)
            if school is None:
                continue
            assigned = self.assignVillage(school, village)

    def printData(self):
        print("List of Villages already mapped:")
        print("School , Village")
        for schoolinfo in self.villageAlreadyMapped:
            (school, village), = schoolinfo.items()
            print(str(school)+","+str(village))

        print("List of villages newly mapped:")
        print("School , Village")
        for schoolinfo in self.villageNewMapped:
            (school, village), = schoolinfo.items()
            print(str(school)+","+str(village))
        print("List of Schools for which Village mapping has to be changed so Check")
        print("School , village")
        for schoolinfo in self.villageMapCheck:
            (school, village), = schoolinfo.items()
            print(str(school)+","+str(village))

    

