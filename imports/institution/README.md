# Procedure for importing institution data from existing database (EMS, dubdubdub)
1. Import Institutuion data from EMS
    Run import_inst_data.py script:
    python import_inst_data.py <EMS  db> <unified  db>

2. Update institution table with DISE codes.
    Run updateinstitution_disecode.py script:
    python updateinstitution_disecode.py <ems db> <unified db>

3. Update institution table with data with SSA and electrep data
    Run updateinstitutiondata.py script:
    python updateinstitutiondata.py <dubdubudb db> <full path to ssa_details.csv> <unified db>

4. Update coords in the institution table. It expects a csv file with:dise code, latitude, longitude
    Run updateinstitutiondcoords.py script:
    python updateinstitutioncoords.py <full path of the coords.csv> <unified db>

5. Import StudentGroup data from EMS
    Run import_studentgroup_data.py script:
    python import_inst_data.py <EMS db> <unified db>

6. Update coords in the institution table for preschool. 
    Run updatepreschoolcoords.py
    python updatepreschoolcoords.py <dubdubdub db> <unified db>
