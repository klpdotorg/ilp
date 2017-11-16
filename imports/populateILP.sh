#DBs required:-
#dubdubdub
#ems
#electedrep_new
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
./boundary/populateBoundaryTables.sh dubdubdub electrep_new $ilp `pwd`/boundary/temp `pwd`/boundary/sql
./boundary/updateDiseSlugs.sh $ilp

#Populate dise tables
python dise/import_dise_data.py klpdise_olap $ilp

#Populate Institutions
python institution/import_inst_data.py ems $ilp 
python institution/updateinstitution_disecode.py ems $ilp 
python institution/updateinstitutiondata.py dubdubdub `pwd`/institution/ssa_details.csv $ilp 
python institution/updateinstitutioncoords.py `pwd`/institution/ssa_latlong.csv $ilp 
python institution/import_studentgroup_data.py ems $ilp 
python institution/updatepreschoolcoords.py dubdubdub $ilp 

#Populate Student and Staff data
python student-staff/import_student_data.py ems $ilp 
python student-staff/updatechildrelations.py ems $ilp 
python student-staff/import_staff_data.py ems $ilp 
python student-staff/import_studentgrouprelations_data.py ems $ilp


#Populate spatial Procedure for updating spatial data ino the election boundary tables
python spatial/updatespatialdata.py spatial $ilp 

#Populate aggregates
psql -U klp -d $ilp -f aggregates/materialized_views.sql 

#Populate assessments
#Import SYS data
python assessments/import_sys.py dubdubdub $ilp

#Import Mahiti IVRS data
python assessments/import_mahitiivrs.py dubdubdub $ilp

#Import KLP Konnect data
python assessments/import_klpkonnect.py dubdubdub $ilp

#Import GP Contest data
python assessments/import_gp_contest.py dubdubdub $ilp

#Import Community data
#IVRS
python assessments/import_community_basic_ivrs.py dubdubdub $ilp
#Run import_communityfromcsv15_16.py script:
#2015-2016
python assessments/import_communityfromcsv15_16.py `pwd`/assessments/community_survey $ilp
#2014-2015 TBD

#2013-2014 TBD

#Import GKA data
#Basic
python assessments/import_gkabasicinfo.py $ilp
python assessments/import_gkaassessmentdata.py dubdubdub $ilp
#2016-2017 TBD

#Import Anganwadi Infrastructure Data:
python assessments/import_anganwadi_infra.py ang_infra $ilp
