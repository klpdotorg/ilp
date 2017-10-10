# Procedure for importing assessment data from existing database (dubdubdub) and files
1. Import Anganwadi Infrastructure Data:
    Run import_anganwadi_infra.py
    python import_anganwadi_infra.py <anganwadi infra db> <unified  db>

2. Import Mahiti IVRS data
    Run import_mahitiivrs.py script:
    python import_mahitiivrs.py <dubdubudb db> <unified db>

3. Import SYS data
    Run import_sys.py script:
    python import_sys.py <dubdubdub db> <unified db>

4. Import KLP Konnect data 
    Run import_klpkonnect.py script:
    python import_klpkonnect.py <dubdubdub db> <unified db>

5. Import GP Contest data
    Run import_gp_contest.py script:
    python import_gp_contest.py <dubdubdub db> <unified db>

6. Import Community data
    Run import_community.py script:
    python import_community.py <dubdubdub db> <unified db>

    Run import_communityfromcsv.py script:
    python import_communityfromcsv.py <directory of community survey csv files> <unified db>
