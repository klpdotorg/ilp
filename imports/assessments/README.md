# Procedure for importing assessment data from existing database (dubdubdub) and files
1. Import Mahiti IVRS data
    Run import_mahitiivrs.py script:
    python import_mahitiivrs.py <dubdubudb db> <unified db>

2. Import SYS data
    Run import_sys.py script:
    python import_sys.py <dubdubdub db> <unified db>

3. Import KLP Konnect data 
    Run import_klpkonnect.py script:
    python import_klpkonnect.py <dubdubdub db> <unified db>

4. Import GP Contest data
    Run import_gp_contest.py script:
    python import_gp_contest.py <dubdubdub db> <unified db>

5. Import Community data
    Run import_community.py script:
    python import_community_basic_ivrs.py <dubdubdub db> <unified db>

    Run import_communityfromcsv15_16.py script:
    python import_communityfromcsv15_16.py <directory of community survey csv files> <unified db>

6. Import GKA data
    Run import_gkabasic.py script:
    python import_gkabasicinfo.py <unified db>

    Run import_gka.py script
    python import_gkaassessmentdata.py <dubdubdub db> <unified db>

7. Import Anganwadi Infrastructure Data:
    Run import_anganwadi_infra.py
    python import_anganwadi_infra.py <anganwadi infra db> <unified  db>

