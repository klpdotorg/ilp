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
from boundary.models import ElectionBoundary
from dise.models import BasicData
from schools.models import Institution


class Command(BaseCommand):
    active_status = Status.objects.get(char_id='AC')
    schools_updated = []
    schoolsid_notupdated = []
    schools_notupdated = []
    dise_notfound = []
    createdandupdated = []
    schoolsalreadyupdated = []
    
    def add_arguments(self, parser):
        parser.add_argument('state')
        parser.add_argument('academicyear')

    def getDise(self, schoolcode, academicyear):
        try:
            dise = BasicData.objects.get(school_code=schoolcode, academic_year=academicyear)
            return dise
        except BasicData.DoesNotExist:
            return None

    def updateDiseIds(self, state, academicyear):
        print(academicyear)
        schools = Institution.objects.select_related('dise').filter(admin0__name__iexact=state,status='AC',dise__isnull=False)
        count = 0
        for school in schools:
            count +=1
            if school.dise.academic_year_id == academicyear:
                self.schoolsalreadyupdated.append(school.id)
                continue
            newdise = self.getDise(school.dise.school_code, academicyear)
            if newdise == None:
                print("Creating new entry")
                self.createDiseEntry(state,academicyear,school)
            else:
                print("Updating entry")
                self.schools_updated.append(school.id)
                school.dise = newdise
                school.save()
        print("Num schools: "+str(count))

    def createDiseEntry(self, state, academicyear, school):
        newdise = school.dise
        newdise.id = None 
        newdise.pk=None
        newdise.academic_year_id=academicyear
        newdise.save()
        try:
           createddise = BasicData.objects.get(school_code=school.dise.school_code,academic_year_id=academicyear)
           school.dise = createddise
           school.save
           self.createdandupdated.append(school.id)
        except BasicData.DoesNotExist:
            print("Could not create dise entry for schoolcode :"+str(school.dise.school_code)+" and academicyear :"+str(academicyear))
            return None

    def handle(self, *args, **options):
        state = options['state']
        academicyear = options['academicyear']
     
        self.updateDiseIds(state, academicyear)

        print("Schools already updated: ("+str(len(self.schoolsalreadyupdated))+"):")
        print("Schools updated: ("+str(len(self.schools_updated))+"):")
        print("DISE created and Schools updated: ("+str(len(self.createdandupdated))+"):")
