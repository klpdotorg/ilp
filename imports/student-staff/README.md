# Procedure for importing student and staff related data from existing database (EMS, dubdubdub)
1. Import student data from EMS
    Run import_student_data.py script:
    python import_student_data.py <EMS  db> <unified  db>

2. Update child relations into the student table.
    Run updatechildrelations.py script:
    python updatechildrelations.py <EMS db> <unified db>

3. Import staff data from EMS
    Run import_staff_data.py script:
    python import_staff_data.py <EMS  db> <unified  db>

4. Import StudentGroupRelation table for both staff and student data from EMS
    Run import_studentgrouprelations_data.py script:
    python import_studentgrouprelations_data.py <EMS db> <unified db>
