import os
import sys
import csv
import psycopg2
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
    gpid = 0
    gpname = 1
    disecode = 2
    schoolname = 3
    schoolmapped = []
    schoolalreadymapped = []
    schoolnotmapped = []
    gpNewMapped = []
    gpAlreadyMapped = []
    gpMapCheck = []
    
    def add_arguments(self, parser):
        parser.add_argument('filename')

    def validateSchool(self,count, row, disecode, schoolname):
        try:
            school = Institution.objects.get(
                    dise__school_code=disecode,
                    name__iexact=schoolname)
            return school
        except Institution.DoesNotExist:
            print(str(count)+"|"+str(row)+"| Error: Institution object does not exist")
            return None


    def createNewGP(self, gpid, gpname):
        gptype = BoundaryType.objects.get(char_id='GP')
        try:
            gp = ElectionBoundary.objects.create(id=gpid, const_ward_name=gpname, const_ward_type=gptype, status= self.active_status, state_id=3)
            return gp
        except Exception as e:
            print(e)
            return None

    def getGP(self, gpid, gpname):
        try:
            gp = ElectionBoundary.objects.get(id=gpid, const_ward_name__iexact=gpname, const_ward_type='GP')
        except ElectionBoundary.DoesNotExist:
            print("GPID: "+str(gpid)+", GPName: "+gpname+" Does not exist, Creating new one.")
            gp = self.createNewGP(gpid, gpname)
        return gp

    def assignGP(self, school, gp):
        if school.gp == None or school.gp == "":
            self.gpNewMapped.append({school.id:gp.id})
            school.gp = gp
            school.save()
            return True
        if school.gp.id == gp.id:
            self.gpAlreadyMapped.append({school.id:gp.id})
            return False
        else:
            self.gpMapCheck.append({school.id:gp.id})
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
            gpid = row[self.gpid]
            gpname = row[self.gpname].strip().lower()
            disecode = row[self.disecode]
            schoolname = row[self.schoolname].strip().lower()

            school = self.validateSchool(count, row, disecode, schoolname)
            if school == None:
                continue
            gp = self.getGP(gpid, gpname)
            if gp == None:
                continue
            assigned = self.assignGP(school, gp)

    def printData(self):
        print("List of GP's already mapped:")
        print("School , GP")
        for schoolinfo in self.gpAlreadyMapped:
            (school, gp), = schoolinfo.items()
            print(str(school)+","+str(gp))

        print("List of GP's newly mapped:")
        print("School , GP")
        for schoolinfo in self.gpNewMapped:
            (school, gp), = schoolinfo.items()
            print(str(school)+","+str(gp))

        

        print("List of Schools for which GP mapping has to be changed so Check")
        print("School , GP")
        for schoolinfo in self.gpMapCheck:
            (school, gp), = schoolinfo.items()
            print(str(school)+","+str(gp))


    def handle(self, *args, **options):
        file_name = options['filename']
     
        if not file_name:
            print ("Please specify a filename with the --filename argument")
            return False

        self.parseFile(file_name)
        self.printData()


