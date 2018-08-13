import os
import sys
import csv
import psycopg2
import re
from django.core.management.base import BaseCommand
from django.core.exceptions import MultipleObjectsReturned
from django.db import transaction
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from common.models import Status, InstitutionType, InstitutionGender, Language
from boundary.models import Boundary, BoundaryType, BoundaryStateCode
from dise.models import BasicData
from schools.models import Institution, InstitutionCategory, Management, InstitutionLanguage


class Command(BaseCommand):
    active_status = Status.objects.get(char_id='AC')
       
    def add_arguments(self, parser):
        parser.add_argument('state')
        parser.add_argument('coords')

    def updateInstitutionCoords(self, dise_code, state,  latitude, longitude):
        pnt = GEOSGeometry('POINT(%s %s)'%(longitude, latitude))
        
        try:
            institutionobj = Institution.objects.get(dise__school_code = dise_code, admin0__name=state)
        except Institution.DoesNotExist:
            print("No institution found for state: "+state+" and dise_code: "+dise_code)
            return
        institutionobj.coord = pnt
        institutionobj.save()
        
        


    def getDecimalDegree(self, degrees, minutes, seconds):
        dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60)
        return dd


    def getValidFloatValues(self, value):
        return 0 if value=='' else value

                        
    def handle(self, *args, **options):
        state= options['state']
        file_name = options['coords']
     
        try:
            state_boundary = Boundary.objects.get(name=state)
        except Boundary.DoesNotExist:
            print("Invalid state: "+state)
            return
      
        if not file_name:
            print ("Please specify a filename with the --coords argument")
            return False
        f = open(file_name, encoding='utf-8')
        file_reader = csv.reader(f, delimiter='|')
        count = 0
        for row in file_reader:
            if count == 0:
                count += 1
                continue
            count += 1
            dise_code = row[0].strip()
            try:
                dise_object = BasicData.objects.get(school_code = dise_code)
            except BasicData.DoesNotExist:
                print("Dise code does not exist :"+dise_code+".") 
                continue
   
            latitudeDD = row[1].strip()
            longitudeDD = row[2].strip()
           
            if latitudeDD == '0':
                print("latitude is 0 for dise_code :"+dise_code)
                continue

            self.updateInstitutionCoords(dise_code, state, latitudeDD, longitudeDD) 
