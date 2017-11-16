from os import system,sys
import os


if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: python import_dise_data.py klpdise_olap ilp", file=sys.stderr)
    sys.exit()

#Before running this script
#change this to point to the ems database that is used for getting the data
fromdatabase = sys.argv[1]

#change this to ilp db to be populated with
todatabase = sys.argv[2]

basename = "dise"

inputdatafile = basename+"_getdata.sql"
loaddatafile = basename+"_loaddata.sql"

tables=[
    {
        'name': 'dise_basicdata',
        'fixedcolumns': 'academic_year_id',
        'from_columns': 'school_code, school_name, district, block_name, cluster_name, village_name, pincode, rural_urban, medium_of_instruction, distance_brc, distance_crc, yeur_estd, pre_pry_yn, residential_sch_yn, sch_management, lowest_class, highest_class, sch_category, pre_pry_students, school_type, shift_school_yn, no_of_working_days, no_of_acad_inspection, residential_sch_type, pre_pry_teachers, visits_by_brc, visits_by_crc,school_dev_grant_recd, school_dev_grant_expnd, tlm_grant_recd, tlm_grant_expnd, funds_from_students_recd, funds_from_students_expnd, building_status, tot_clrooms, classrooms_in_good_condition, classrooms_require_major_repair, classrooms_require_minor_repair, other_rooms_in_good_cond, other_rooms_need_major_rep, other_rooms_need_minor_rep, toilet_common, toilet_boys, toilet_girls, kitchen_devices_grant, status_of_mdm, computer_aided_learnin_lab, separate_room_for_headmaster, electricity, boundary_wall, library_yn, playground, blackboard, books_in_library, drinking_water, medical_checkup, ramps, no_of_computers, male_tch, female_tch, noresp_tch, head_teacher, graduate_teachers, tch_with_professional_qualification, days_involved_in_non_tch_assgn, teachers_involved_in_non_tch_assgn, centroid, assembly_name, parliament_name, class1_total_enr_boys, class2_total_enr_boys, class3_total_enr_boys, class4_total_enr_boys, class5_total_enr_boys, class6_total_enr_boys, class7_total_enr_boys, class8_total_enr_boys, class1_total_enr_girls, class2_total_enr_girls, class3_total_enr_girls, class4_total_enr_girls, class5_total_enr_girls, class6_total_enr_girls, class7_total_enr_girls, class8_total_enr_girls, total_boys, total_girls, new_pincode, infered_assembly, infered_parliament',
        'to_columns': 'school_code, school_name, district, block_name, cluster_name, village_name, pincode, rural_urban, medium_of_instruction, distance_brc, distance_crc, year_estd, pre_pry_yn, residential_sch_yn, sch_management, lowest_class, highest_class, sch_category, pre_pry_students, school_type, shift_school_yn, no_of_working_days, no_of_acad_inspection, residential_sch_type, pre_pry_teachers, visits_by_brc, visits_by_crc,school_dev_grant_recd, school_dev_grant_expnd, tlm_grant_recd, tlm_grant_expnd, funds_from_students_recd, funds_from_students_expnd, building_status, tot_clrooms, classrooms_in_good_condition, classrooms_require_major_repair, classrooms_require_minor_repair, other_rooms_in_good_cond, other_rooms_need_major_rep, other_rooms_need_minor_rep, toilet_common, toilet_boys, toilet_girls, kitchen_devices_grant, status_of_mdm, computer_aided_learnin_lab, separate_room_for_headmaster, electricity, boundary_wall, library_yn, playground, blackboard, books_in_library, drinking_water, medical_checkup, ramps, no_of_computers, male_tch, female_tch, noresp_tch, head_teacher, graduate_teachers, tch_with_professional_qualification, days_involved_in_non_tch_assgn, teachers_involved_in_non_tch_assgn, centroid, assembly_name, parliament_name, class1_total_enr_boys, class2_total_enr_boys, class3_total_enr_boys, class4_total_enr_boys, class5_total_enr_boys, class6_total_enr_boys, class7_total_enr_boys, class8_total_enr_boys, class1_total_enr_girls, class2_total_enr_girls, class3_total_enr_girls, class4_total_enr_girls, class5_total_enr_girls, class6_total_enr_girls, class7_total_enr_girls, class8_total_enr_girls, total_boys, total_girls, new_pincode, infered_assembly, infered_parliament',
        'query': "\COPY (select replaceyear, replacecolumns from dise_replaceyear_basic_data) TO '$PWD/load/replacefile_replaceyear.csv' NULL 'null' DELIMITER   ',' quote '\\\"' csv;",
    }
]

years=["1213","1314", "1415", "1516"]

#Create directory and files
def init():
    if not os.path.exists("load"):
    	os.makedirs("load")
    inputfile=open(inputdatafile,'wb',0)
    loadfile=open(loaddatafile,'wb',0)


#Create the getdata.sql and loaddata.sql files
# getdata.sql file has the "Copy to" commands for populating the various csv files
# loaddata.sql file has the "copy from" commands for loading the data into the db
def create_sqlfiles():
    #Loop through the tables
    for table in tables:
        for year in years:
            #write into the "copy to" file to get data from ems
            system('echo "'+table['query'].replace('replacecolumns',table['from_columns']).replace('replacefile',table['name']).replace('replaceyear',year)+'\">>'+inputdatafile)

            #write into the "copy from" file to load data into db
            filename=os.getcwd()+'/load/'+table['name']+'_'+year+'.csv'
            open(filename,'wb',0)
            os.chmod(filename,0o666)

            system('echo "\COPY '+table['name']+"("+table['fixedcolumns']+","+table['to_columns']+") from '"+filename+"' with csv NULL 'null';"+'\">>'+loaddatafile)


#Running the "copy to" commands to populate the csvs.
def getdata():
    system("psql -U klp -d "+fromdatabase+" -f "+inputdatafile)


#Running the "copy from" commands for loading the db.
def loaddata():
    system("psql -U klp -d "+todatabase+" -f "+loaddatafile)


#order in which function should be called.
init()
create_sqlfiles()
getdata()
loaddata()
