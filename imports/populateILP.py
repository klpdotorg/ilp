#DBs required:-
#dubdubdub
#ems
#electedrep_new
#klpdise_olap
#ang_infra
#spatial

#ilp

# Populate Boundaries DONE
./boundary/populateBoundaryTables.sh dubdubdub electrep_new checkilp /Users/shivangidesai/Akshara/ilp/imports/boundary/temp
./boundary/updatediseslugs.sh checkilp

#Populate dise tables DONE
python dise/import_dise_data.py klpdise_olap ilp

#Populate Institutions
python institution/import_inst_data.py ems ilp #DONE
python institution/updateinstitution_disecode.py ems ilp #DONE
python institution/updateinstitutiondata.py dubdubdub `pwd`/institution/ssa_details.csv ilp #DONE
python institution/updateinstitutioncoords.py `pwd`/institution/ssa_latlong.csv ilp #DONE
python institution/import_studentgroup_data.py ems ilp #DONE
python institution/updatepreschoolcoords.py dubdubdub ilp #DONE

#Populate Student and Staff data
python student-staff/import_student_data.py ems ilp #pre not done, CHECK STATUS
python student-staff/updatechildrelations.py ems ilp #DONE
python student-staff/import_staff_data.py ems ilp #DONE
python student-staff/import_studentgrouprelations_data.py ems ilp #DONE


#Populate spatial Procedure for updating spatial data ino the election boundary tables
python spatial/updatespatialdata.py spatial ilp #DONE

#Populate aggregates
psql -U klp -d ilp -f aggregates/materialized_views.sql #DONE

#Populate assessments
#Import SYS data
python assessments/import_sys.py dubdubdub ilp #DONE

#Import Mahiti IVRS data
python assessments/import_mahitiivrs.py dubdubdub ilp #DONE

#Import KLP Konnect data
python assessments/import_klpkonnect.py dubdubdub ilp #DONE

#Import GP Contest data
python assessments/import_gp_contest.py dubdubdub ilp #DONE

#Import Community data
#IVRS
python assessments/import_community_basic_ivrs.py dubdubdub ilp #DONE
#Run import_communityfromcsv.py script:
#2015-2016
python assessments/import_communityfromcsv15_16.py `pwd`/assessments/community_survey ilp #DONE
#2014-2015

#2013-2014

#Import GKA data
#Basic
python assessments/import_gkabasicinfo.py ilp #DONE
python assessments/import_gkaassessmentdata.py dubdubdub ilp #DONE 2017-2018
#2016-2017 TBD

#Import Anganwadi Infrastructure Data:
python assessments/import_anganwadi_infra.py ang_infra ilp #DONE
