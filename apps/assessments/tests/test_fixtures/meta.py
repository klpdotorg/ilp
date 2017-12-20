INSTITUTION_ID = 3895

# ./manage.py dump_object assessments.AnswerGroup_Institution --query '{"id__in": [266252, 266253, 266254, 266255, 266256, 266257, 266258, 266259, 266260, 266261]}' > answergroup_institution.json
ANSWERGROUP_INSTITUTION_IDS = [
    266252, 266253, 266254, 266255,
    266256, 266257, 266258, 266259, 266260, 266261
]

# to dump data of AnswerInstitution; filter by above answergroup_ids
# ./manage.py dump_object assessments.AnswerInstitution --query '{"answergroup__in": [266252, 266253, 266254, 266255, 266256, 266257, 266258, 266259, 266260, 266261]}' > answer_institution.json

QUESTIONGROUP_ID = 20
QUESTIONGROUP_QUESTION_COUNT = 10
QUESTIONGROUP_QTYPE = 2
# to dump data of QuestionGroup_Questions; filtered by questiongroup_id 20.
# ./manage.py dump_object assessments.QuestionGroup_Questions --query '{"questiongroup_id": 20}' > qgroup_questions.json

# to dump data of Survey.
# ./manage.py dump_object assessments.survey --query '{"id__in": [2, 3, 7, 6, 5]}' > surveys.json

TEST_ANSWERGROUP_POST_DATA = {
      "group_value": "Subhashini",
      "double_entry": 0,
      "created_by": "",
      "date_of_visit": "2016-08-20T00:00:00Z",
      "respondent_type": "",
      "comments": "",
      "is_verified": "true",
      "status": "IA",
      "sysid": "",
      "entered_at": "2017-06-06T00:00:00Z",
      "answers": [
        {
          "question": 271,
          "answer": "Yes"
        },
        {
          "question": 272,
          "answer": "Yes"
        },
        {
          "question": 273,
          "answer": "No"
        },
        {
          "question": 274,
          "answer": "No"
        },
        {
          "question": 275,
          "answer": "Yes"
        },
        {
          "question": 276,
          "answer": "Yes"
        },
        {
          "question": 277,
          "answer": "Yes"
        },
        {
          "question": 278,
          "answer": "Yes"
        },
        {
          "question": 279,
          "answer": "Yes"
        },
        {
          "question": 280,
          "answer": "Yes"
        },
        {
          "question": 281,
          "answer": "No"
        },
        {
          "question": 282,
          "answer": "Yes"
        },
        {
          "question": 283,
          "answer": "Yes"
        },
        {
          "question": 284,
          "answer": "Yes"
        },
        {
          "question": 285,
          "answer": "Yes"
        },
        {
          "question": 286,
          "answer": "Yes"
        },
        {
          "question": 287,
          "answer": "Yes"
        },
        {
          "question": 288,
          "answer": "Yes"
        },
        {
          "question": 289,
          "answer": "Yes"
        },
        {
          "question": 290,
          "answer": "Yes"
        },
        {
          "question": 130,
          "answer": "4"
        },
        {
          "question": 291,
          "answer": "Female"
        }
      ]
}