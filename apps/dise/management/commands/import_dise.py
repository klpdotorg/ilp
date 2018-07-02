from os import system, sys
import os
import inspect
import csv
import psycopg2
import re
import io
from django.core.management.base import BaseCommand
from django.db import connection
from django.core.exceptions import MultipleObjectsReturned
from django.db import transaction
from django.conf import settings


class Command(BaseCommand):
    output =  io.StringIO()
    scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    get_query = "\COPY (select 'replacestate', replaceyear, replacecolumns from dise_replaceyear_basic_data where lower(state_name)='replacestate' and sch_category<=10) TO 'replacefilename' NULL 'null' DELIMITER   '|' quote '\\\"' csv;"
    from_columns = 'school_code, school_name, district, block_name, cluster_name, village_name, pincode, rural_urban, medium_of_instruction, distance_brc, distance_crc, yeur_estd, pre_pry_yn, residential_sch_yn, sch_management, lowest_class, highest_class, sch_category, pre_pry_students, school_type, shift_school_yn, no_of_working_days, no_of_acad_inspection, residential_sch_type, pre_pry_teachers, visits_by_brc, visits_by_crc,school_dev_grant_recd, school_dev_grant_expnd, tlm_grant_recd, tlm_grant_expnd, funds_from_students_recd, funds_from_students_expnd, building_status, tot_clrooms, classrooms_in_good_condition, classrooms_require_major_repair, classrooms_require_minor_repair, other_rooms_in_good_cond, other_rooms_need_major_rep, other_rooms_need_minor_rep, toilet_common, toilet_boys, toilet_girls, kitchen_devices_grant, status_of_mdm, computer_aided_learnin_lab, separate_room_for_headmaster, electricity, boundary_wall, library_yn, playground, blackboard, books_in_library, drinking_water, medical_checkup, ramps, no_of_computers, male_tch, female_tch, noresp_tch, head_teacher, graduate_teachers, tch_with_professional_qualification, days_involved_in_non_tch_assgn, teachers_involved_in_non_tch_assgn, assembly_name, parliament_name, class1_total_enr_boys, class2_total_enr_boys, class3_total_enr_boys, class4_total_enr_boys, class5_total_enr_boys, class6_total_enr_boys, class7_total_enr_boys, class8_total_enr_boys, class1_total_enr_girls, class2_total_enr_girls, class3_total_enr_girls, class4_total_enr_girls, class5_total_enr_girls, class6_total_enr_girls, class7_total_enr_girls, class8_total_enr_girls, total_boys, total_girls, new_pincode, infered_assembly, infered_parliament, centroid'
    to_columns =  ['state_name','academic_year_id','school_code','school_name','district','block_name','cluster_name','village_name','pincode','rural_urban','medium_of_instruction','distance_brc','distance_crc','year_estd','pre_pry_yn','residential_sch_yn','sch_management','lowest_class','highest_class','sch_category','pre_pry_students','school_type','shift_school_yn','no_of_working_days','no_of_acad_inspection','residential_sch_type','pre_pry_teachers','visits_by_brc','visits_by_crc','school_dev_grant_recd','school_dev_grant_expnd','tlm_grant_recd','tlm_grant_expnd','funds_from_students_recd','funds_from_students_expnd','building_status','tot_clrooms','classrooms_in_good_condition','classrooms_require_major_repair','classrooms_require_minor_repair','other_rooms_in_good_cond','other_rooms_need_major_rep','other_rooms_need_minor_rep','toilet_common','toilet_boys','toilet_girls','kitchen_devices_grant','status_of_mdm','computer_aided_learnin_lab','separate_room_for_headmaster','electricity','boundary_wall','library_yn','playground','blackboard','books_in_library','drinking_water','medical_checkup','ramps','no_of_computers','male_tch','female_tch','noresp_tch','head_teacher','graduate_teachers','tch_with_professional_qualification','days_involved_in_non_tch_assgn','teachers_involved_in_non_tch_assgn','assembly_name','parliament_name','class1_total_enr_boys','class2_total_enr_boys','class3_total_enr_boys','class4_total_enr_boys','class5_total_enr_boys','class6_total_enr_boys','class7_total_enr_boys','class8_total_enr_boys','class1_total_enr_girls','class2_total_enr_girls','class3_total_enr_girls','class4_total_enr_girls','class5_total_enr_girls','class6_total_enr_girls','class7_total_enr_girls','class8_total_enr_girls','total_boys','total_girls','new_pincode','infered_assembly','infered_parliament','centroid']

    def add_arguments(self, parser):
        parser.add_argument('dbname')
        parser.add_argument('user')
        parser.add_argument('passwd')
        parser.add_argument('host')
        parser.add_argument('state')
        parser.add_argument('academic_year')

    def connectDISE(self,dbname,user,passwd,host):
        connectionstring = "dbname="+dbname+" user="+user+" password="+passwd+" host="+host
        connection = psycopg2.connect(connectionstring)
        cursor = connection.cursor()
        return connection, cursor

    def handle(self, *args, **options):
        state= options['state'].lower()
        academic_year= options['academic_year']
        
        if not os.path.exists(self.scriptdir+"/load"):
            os.makedirs(self.scriptdir+"/load")
        copyto_file = self.scriptdir+"/load/dise_input_"+academic_year+"_"+state+".csv"
        copyfrom_file = self.scriptdir+"/load/dise_output_"+academic_year+"_"+state+".csv"
        file_obj=open(copyto_file, 'wb', 0)
        get_query = self.get_query.replace("replacecolumns",self.from_columns).replace("replaceyear",academic_year).replace("replacestate",state).replace("replacefilename",copyto_file)
        inputdatafile=self.scriptdir+"/getdata.sql"
        open(inputdatafile, 'wb', 0)
        system('echo "'+get_query+'\">>'+inputdatafile)
        system("PGPASSWORD="+options["passwd"]+" psql -U "+options["user"]+" -d "+options["dbname"]+" -f "+inputdatafile)
        file_obj.close()
        file_obj = open(copyto_file, 'r', encoding='utf-8')
        output = open(copyfrom_file, 'w', encoding='utf8')
        w = csv.writer(output,delimiter='|')
        for row in csv.reader(file_obj,delimiter='|'):
            w.writerow(tuple(s.replace("\n", '') for s in row))

        output.close()
        output= open(copyfrom_file, 'r', encoding='utf-8')
        with connection.cursor() as cursor:
            cursor.copy_from(output,"dise_basicdata",sep='|', columns=self.to_columns,null='null')
