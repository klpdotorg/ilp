from assessments.models import (
    SurveyInstitutionQuestionGroupQDetailsAgg,
    SurveyInstitutionQuestionGroupQDetailsCorrectAnsAgg,
    QuestionGroup,
    QuestionGroup_Questions
)
from schools.models import (
    Institution
)
from django.db.models import (
    When,
    Case, Value, Sum, F, ExpressionWrapper, Count)
from django.db.models.functions import Cast
from django.db import models


def get_school_report(gp_id, survey_id, from_date, to_date):
    schools = Institution.objects.filter(gp_id=gp_id)
    total_answers = SurveyInstitutionQuestionGroupQDetailsAgg.objects.filter(
        survey_id=survey_id,
        yearmonth__gte=from_date,
        yearmonth__lte=to_date).filter(
            institution_id__gp_id=gp_id
        )
    correct_answers = \
        SurveyInstitutionQuestionGroupQDetailsCorrectAnsAgg.objects.filter(
            survey_id=survey_id,
            yearmonth__gte=from_date,
            yearmonth__lte=to_date).filter(
                institution_id__gp_id=gp_id
            )
    distinct_qgroups = total_answers.distinct('questiongroup_id').values_list(
        'questiongroup_id', flat=True)
    school_level = {}
    for school in schools:
        result = {}
        total_answers = total_answers.filter(institution_id=school.id)
        correct_answers = correct_answers.filter(institution_id=school.id)
        for each_class in distinct_qgroups:
            questions = QuestionGroup_Questions.objects.filter(
                questiongroup_id=each_class).exclude(
                    question__question_text__in=['Gender', 'Class visited']
                    ).order_by('sequence')
            all_answers_for_class = total_answers.filter(
                questiongroup_id=each_class)
            correct_answers_for_class = correct_answers.filter(
                questiongroup_id=each_class)
            class_questions = []
            # for answer in correct_answers_for_class:
            for qgroup_question in questions:
                question_answer_details = {}
                try:
                    total = all_answers_for_class.get(
                        microconcept_id=qgroup_question.question.microconcept)
                except:
                    total = 0
                    print("TOTAL ANSWERS EXCEPTION")
                else:
                    total = total.num_assessments
                    print("TOTAL is: ", total)

                try:
                    correct = correct_answers_for_class.get(
                        microconcept_id=qgroup_question.question.microconcept)
                except:
                    correct = 0
                    print("CORRECT ANSWERS EXCEPTION")
                else:
                    correct = correct.num_assessments
                    print("CORRECT is: ", correct)
                percent = 0
                if total is not None and total > 0:
                    sum = total
                    percent = (correct / sum) * 100
                else:
                    sum = 0
                question_answer_details["question"] =\
                    qgroup_question.question.microconcept
                question_answer_details["num_correct"] = correct
                question_answer_details["percent"] = percent
                class_questions.append(question_answer_details)
            result[each_class] = class_questions
        school_level[school] = result
    return school_level
            
            
            
        