#DBs required:-
#dubdubdub
#ems
#electrep_new
#klpdise_olap
#ang_infra
#spatial


# Pass ILP db name
if [ $# -eq 0 ]; then
    echo "Please supply unified database name as argument. USAGE: `basename $0` unified_db_name"
    exit 1;
fi
ilp="$1";

# Populate Boundaries 
echo "Populating Boundaries"
./boundary/populateBoundaryTables.sh dubdubdub electrep_new $ilp `pwd`/boundary/temp `pwd`/boundary/sql
./boundary/updateDiseSlugs.sh $ilp
echo "Boundaries done"

#Populate dise tables
echo "Populating Dise tables"
python dise/import_dise_data.py klpdise_olap $ilp
echo "DISE tables done"

#Populate Institutions
echo "Populating Institution tables"
python institution/import_inst_data.py ems $ilp 
python institution/updateinstitution_disecode.py ems $ilp 
python institution/updateinstitutiondata.py dubdubdub `pwd`/institution/ssa_details.csv $ilp 
python institution/updateinstitutioncoords.py `pwd`/institution/ssa_latlong.csv $ilp 
python institution/import_studentgroup_data.py ems $ilp 
python institution/updatepreschoolcoords.py dubdubdub $ilp 
python institution/updateinstitution_pincode.py ems $ilp
python institution/updateinstitutiongpdata.py `pwd`/institution/gp_schoolmapping.csv $ilp
echo "Institution tables done"

#Populate Student and Staff data
echo "Populating Student and staff data"
python student-staff/import_student_data.py ems $ilp 
python student-staff/updatechildrelations.py ems $ilp 
python student-staff/import_staff_data.py ems $ilp 
python student-staff/import_studentgrouprelations_data.py ems $ilp
echo "Student and Staff tables done"


#Populate spatial Procedure for updating spatial data ino the election boundary tables
echo "Populating spatial data"
python spatial/updatespatialdata.py spatial $ilp 
echo "Spatial done"

#Populate assessments
echo "Running Assessments"
#Import SYS data
echo "SYS Assessments"
python assessments/import_sys.py dubdubdub $ilp
python assessments/update_sysquestions.py `pwd`/assessments/sysquestions $ilp

#Import IVRS Community data
echo "Community IVRS"
python assessments/import_community_ivrs.py dubdubdub $ilp

#Import KLP Konnect data
echo "KLP Konnect"
python assessments/import_klpkonnect.py dubdubdub $ilp

#Import GP Contest data
echo "GP Contest"
python assessments/import_gp_contest.py dubdubdub $ilp

#Import GKA Monitoring
echo "GKA Monitoring"
python assessments/import_gka_monitoring.py dubdubdub $ilp

#Import Community data
echo "Community data"
python assessments/import_community_basic.py dubdubdub $ilp
#2015-2016
python assessments/import_communityfromcsv15_16.py `pwd`/assessments/community_survey/15_16 $ilp
#2014-2015 
python assessments/import_communityfromcsv14_15.py `pwd`/assessments/community_survey/14_15 $ilp


#Import GKA data
echo "GKA data"
python assessments/import_gka_basicinfo.py dubdubdub $ilp
python assessments/import_gkaassessmentdata.py dubdubdub $ilp

#Import Anganwadi Infrastructure Data:
echo "Anganwadi Infra"
python assessments/import_anganwadi_infra.py ang_infra $ilp

#update location for answergroups
echo "Updating Locations for AnswerGroups"
python assessments/update_answerlocation.py dubdubdub $ilp

#Import images
echo "Inst images"
python assessments/import_institutionimages.py dubdubdub $ilp

#insert survey to surveytag mapping
psql -U klp -d $ilp -f assessments/insert_survey_tag_mapping.sql

#Mapping institutions to survey tags
psql -U klp -d $ilp -f assessments/insert_surveytag_institution_mapping.sql
psql -U klp -d $ilp -f assessments/insert_surveytag_class_mapping.sql

psql -U klp -d $ilp -f assessments/update_questionscores.sql

psql -U klp -d $ilp -f assessments/insertekstep_questiongroupkey.sql

psql -U klp -d $ilp -f assessments/insert_surveyusertype_mapping.sql

psql -U klp -d $ilp -f assessments/cleanentries.sql
echo "Assessments Done"

#Populate Users
echo "Users"
python users/import_users.py dubdubdub $ilp
psql -U klp -d $ilp -f users/insert_unknownuser.sql
python users/import_usersfromfile.py `pwd`/users/csv_files/ $ilp
python users/update_assessment_userid.py dubdubdub $ilp
echo "Users Done"

#Populate ivrs
echo "IVRS tables"
python ivrs/import_ivrs_data.py dubdubdub $ilp

#Populate Odisha data
echo "Odisha data"
psql -U klp -d $ilp -f odisha/import_odisha_boundary/insert_odisha_district.sql
psql -U klp -d $ilp -f odisha/import_odisha_boundary/insert_odisha_block.sql
psql -U klp -d $ilp -f odisha/import_odisha_boundary/insert_odisha_cluster.sql
psql -U klp -d $ilp -f odisha/import_odisha_schools/insert_odisha_pincode.sql
psql -U klp -d $ilp -f odisha/import_odisha_schools/insert_odisha_schools.sql
psql -U klp -d $ilp -f odisha/import_odisha_schools/insert_odisha_schools_language.sql

#Populate aggregates
echo "Running aggregates"
psql -U klp -d $ilp -f aggregates/materialized_views.sql 
psql -U klp -d $ilp -f aggregates/assessment_materialized_views.sql 
echo "Aggregates Done"
