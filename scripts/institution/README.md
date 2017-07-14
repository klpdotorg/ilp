# Procedure for importing institution data from existing database (EMS, dubdubdub)
Import Institutuion data from EMS
1. Modify import_inst_data.py script to point to correct database. Change 'fromdatabase' to point to ems database and 'todatabase' to ilp database.
2. Run psql -d <ilpdatabase> -f cleanems.sql (This script will clean up the ems database)
3. Run import_inst_data.py script:
    python import_inst_data.py 1>output 2>error
Check errors to make sure that the scripts have run properly.


Update institution table with data from SSA
1. Modify updateinstitutiondata_ssa.py script to point to correct database. Change 'fromdatabase' to point to dubdubdub database and 'todatabase' to point to ilp database
2. Run updateinstitutiondata_ssa.py script:
    python updateinstitutiondata_ssa.py 1>output 2>error
Check errors to make sure that the script has run properly
