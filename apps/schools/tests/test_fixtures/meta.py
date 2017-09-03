# ./manage.py dump_object schools.Institution 29539 36172 > institution.json
INSTITUTION_COUNT = 2
INSTITUTION_ID_1 = 29539
INSTITUTION_ID_2 = 36172

# ./manage.py dump_object schools.StudentGroup 3486429 > studentgroup.json
# (Institution_id=INSTITUTION_ID_2)
STUDENTGROUP_ID = 3486429

# ./manage.py dump_object schools.Student
# 1667626 1667628 1667629 1667630 1668934 > student.json
STUDENT_COUNT = 5
STUDENT_IDS = [1667626, 1667628, 1667629, 1667630, 1668934]

# ./manage.py dump_object schools.StudentStudentGroupRelation
# --query '{"student__in": [1668934, 1667630, 1667629, 1667628, 1667626]}'
# > studentgrouprelation.json
STUDENT_GROUP_RELATION = '*'
