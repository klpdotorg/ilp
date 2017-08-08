# Procedure for importing institution data from existing database (EMS, dubdubdub)
1. Import Institutuion data from EMS
    Run import_inst_data.py script:
    python import_inst_data.py <EMS  db> <unified  db>

2. Update institution table with data with SSA and electedrep data
    Run updateinstitutiondata.py script:
    python updateinstitutiondata.py <dubdubudb db> <unified db>

3. Update coords in the institution table. It expects a csv file with:dise code, latitude, longitude
    Run updateinstitutiondcoords.py script:
    python updateinstitutioncoords.py <full path of the coords.csv> <unified db>

4. Import StudentGroup data from EMS
    Run import_studentgroup_data.py script:
    python import_inst_data.py <EMS db> <unified db>
