INSTITUTION_ID = 3895

# ./manage.py dump_object assessments.AnswerGroup_Institution --query '{"id__in": [266252, 266253, 266254, 266255, 266256, 266257, 266258, 266259, 266260, 266261]}' > answergroup_institution.json
ANSWERGROUP_INSTITUTION_IDS = [
    266252, 266253, 266254, 266255,
    266256, 266257, 266258, 266259, 266260, 266261
]

# to dump data of AnswerInstitution; filter by above answergroup_ids
# ./manage.py dump_object assessments.AnswerInstitution --query '{"answergroup__in": [266252, 266253, 266254, 266255, 266256, 266257, 266258, 266259, 266260, 266261]}' > answer_institution.json

# to dump data of QuestionGroup_Questions; filtered by questiongroup_id 20.
# ./manage.py dump_object assessments.QuestionGroup_Questions --query '{"questiongroup_id": 20}' > qgroup_questions.json

# to dump data of Survey.
# ./manage.py dump_object assessments.survey --query '{"id__in": [2, 3, 7, 6, 5]}' > surveys.json