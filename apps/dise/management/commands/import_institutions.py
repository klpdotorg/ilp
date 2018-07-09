import os
import sys
import csv
import psycopg2
import re
from django.core.management.base import BaseCommand
from django.core.exceptions import MultipleObjectsReturned
from django.db import transaction
from django.conf import settings
from common.models import Status, InstitutionType, InstitutionGender, Language
from boundary.models import Boundary, BoundaryType, BoundaryStateCode
from dise.models import BasicData
from schools.models import Institution, InstitutionCategory, Management, InstitutionLanguage


class Command(BaseCommand):
    active_status = Status.objects.get(char_id='AC')
    #converting dise categories to unify db categories
    categories =  {1:13, #Primary--> Lower Primary
                   2: 14, #Primary with Upper Primary --> Upper Primary ?
                   3: 15, #Primary with Upper Primary Secondary and Higer --> Secondary
                   4: 14, #Upper Primary --> Upper Primary
                   5: 15, #Upper Primary with Secondary and Higher Secondary -->Secondary?
                   6: 15, #Primary with Upper Primary and Secondary -->Secondary?
                   7: 15, #Upper Primary with Secondary --> Secondary
                   8: 15, #Secondary only -->Secondary
                   10: 15  #Secondary with Higher Secondary -->Secondary
                  }
    #converting dise management ids to unify db management id
    management = {
                   1: 1, #Department of Education = 1, 
                   2: 25, #Tribal/Social Welfare Department = 2, 
                   3: 3, #Local body = 3, 
                   4: 4, #Private Aided = 4, 
                   5: 5, #Private Unaided = 5, 
                   6: 6, #others = 6, 
                   7: 15, #Central Govt. = 7, 
                   8: 24, #Unrecognized = 8, 
                   97: 26, #Madarsa recognized (by Wakf board/Madarsa Board) =97, 
                   98: 27 #Madarsa unrecognized=98
                 }
    gender = {
               1: 'boys', #Boys = 1, 
               2: 'girls', #Girls = 2, 
               3: 'co-ed' #Co-educational = 3
             }

    rural_urban = {
                    1:  'Rural',
                    2: 'Urban'}


    moi = {
            1: 'ass', #Assamese=01, 
            2: 'ben', #Bengali=02, 
            3: 'guj', #Gujarati=03, 
            4: 'hin', #Hindi=04, 
            5: 'kan', #Kannada=05, 
            6: 'kas', #Kashmiri=06, 
            7: 'kon', #Konkani=07, 
            8: 'mal', #Malayalam=08, 
            9: 'man', #Manipuri=09, 
            10: 'mar', #Marathi=10, 
            11: 'nep', #Nepali=11, 
            12: 'ori', #Oriya=12, 
            13: 'pun', #Punjabi=13, 
            14: 'san', #Sanskrit=14, 
            15: 'sin', #Sindhi=15, 
            16: 'tam', #Tamil=16, 
            17: 'tel', #Telugu=17, 
            18: 'urd', #Urdu=18, 
            19: 'eng', #English=19, 
            20: 'bod', #Bodo=20, 
            21: 'dog', #Dogri=22, 
            23: 'kha', #Khasi=23, 
            24: 'gar', #Garo=24, 
            25: 'miz', #Mizo=25, 
            26: 'bhu', #Bhutia=26, 
            27: 'lep', #Lepcha=27, 
            28: 'lim', #Limboo=28, 
            29: 'fre', #French=29, 
            99: 'oth', #Other=99
    }
       
    #help = """Import data from DISE 

    #./manage.py import_institutions state academic_year"""

    def add_arguments(self, parser):
        parser.add_argument('state')
        parser.add_argument('academic_year')


    def insertInstitution(self,schoolData):
        try:
            admin0 = Boundary.objects.get(name__iexact=schoolData.state_name, boundary_type='ST')
        except Boundary.DoesNotExist:
            print("Stat not found "+schoolData.state_namme+" for school code: "+str(schoolData.school_code))
            return

        try:
            admin1 = Boundary.objects.get(name__iexact=schoolData.district, boundary_type='SD')
        except Boundary.DoesNotExist:
            print("District Boundary not found "+schoolData.district+" for school code: "+str(schoolData.school_code))
            return
        except MultipleObjectsReturned:
            print("MULTIPLE FOUND :"+schoolData.district+" "+str(schoolData.school_code))

        try:
            admin2 = Boundary.objects.get(name__iexact=schoolData.block_name , boundary_type='SB', parent__name__iexact=schoolData.district)
        except Boundary.DoesNotExist:
            print("Block Boundary not found "+schoolData.block_name+" for school code: "+str(schoolData.school_code))
            return
        except MultipleObjectsReturned:
            print("MULTIPLE FOUND :"+schoolData.block_name+" "+str(schoolData.school_code))

        try:
            admin3 = Boundary.objects.get(name__iexact=schoolData.cluster_name , boundary_type='SC', parent__name__iexact=schoolData.block_name)
        except Boundary.DoesNotExist:
            print("Cluster Boundary not found "+schoolData.cluster_name+" for school code: "+str(schoolData.school_code))
            return
        except MultipleObjectsReturned:
            print("MULTIPLE FOUND :"+schoolData.cluster_name+" "+str(schoolData.school_code))
     
        school_name = schoolData.school_name

        try:
            school_category = InstitutionCategory.objects.get(id=self.categories[schoolData.sch_category])
        except InstitutionCategory.DoesNotExist:
            print("School category does not exist :"+str(schoolData.sch_category))


        try:
            school_gender = InstitutionGender.objects.get(char_id=self.gender[schoolData.school_type])
        except InstitutionGender.DoesNotExist:
            print("School Gender does not exist :"+str(schoolData.school_type))

        institution_type = InstitutionType.objects.get(char_id='primary')

        try:
            management = Management.objects.get(id=self.management[schoolData.sch_management])
        except Management.DoesNotExist:
            print("School Management does not exist :"+str(schoolData.sch_management))

        status = self.active_status

        institution, created = Institution.objects.get_or_create(
                         name = school_name,
                         year_established = schoolData.year_estd,
                         rural_urban = self.rural_urban[schoolData.rural_urban],
                         village = schoolData.village_name,
                         admin0 = admin0,
                         admin1 = admin1,
                         admin2 = admin2,
                         admin3 = admin3,
                         category = school_category,
                         gender = school_gender,
                         institution_type = institution_type,
                         management = management,
                         status = status)
        print("Institution: "+school_name+", created:"+str(created))
         
        Institution.objects.filter(pk=institution.id).update(dise = schoolData)

        if schoolData.medium_of_instruction in self.moi:
            try:
                language = Language.objects.get(char_id = self.moi[schoolData.medium_of_instruction])
            except InstitutionGender.DoesNotExist:
                print("School Moi does not exist :"+str(schoolData.medium_of_instruction))
        else:
            language_id = BoundaryStateCode.objects.get(boundary=admin0)
            print(language_id.language.char_id)
            language = Language.objects.get(char_id = language_id.language.char_id)
        
        id, created = InstitutionLanguage.objects.get_or_create(
                    moi = language,
                    institution = institution)
                    

                        
    def handle(self, *args, **options):
        state= options['state'].lower()
        academic_year= options['academic_year']
        
        dise_schools = BasicData.objects.filter(
                            state_name=state,
                            academic_year=academic_year)
        for school in dise_schools:
           self.insertInstitution(school)
                               
