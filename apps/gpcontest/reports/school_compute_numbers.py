from assessments.models import (
    SurveyInstitutionQuestionGroupQDetailsAgg,
    SurveyInstitutionQuestionGroupQDetailsCorrectAnsAgg,
    QuestionGroup,
    QuestionGroup_Questions,
    AnswerGroup_Institution
)
from schools.models import (
    Institution
)
from django.db.models import (
    When,
    Case, Value, Sum, F, ExpressionWrapper, Count)
from django.db.models.functions import Cast
from django.db import models
from .utils import *

def get_school_report(gp_id, survey_id, from_yearmonth, to_yearmonth):
    """ From and to date is of the format YYYYMM"""
    format_str = '%Y%m'  # The input format
    from_datetime_obj = datetime.datetime.strptime(str(from_yearmonth), format_str)
    to_datetime_obj = datetime.datetime.strptime(str(to_yearmonth), format_str)

    total_answers = SurveyInstitutionQuestionGroupQDetailsAgg.objects.filter(
        survey_id=survey_id,
        yearmonth__gte=from_yearmonth,
        yearmonth__lte=to_yearmonth).filter(
            institution_id__gp_id=gp_id
        )
    correct_answers = \
        SurveyInstitutionQuestionGroupQDetailsCorrectAnsAgg.objects.filter(
            survey_id=survey_id,
            yearmonth__gte=from_yearmonth,
            yearmonth__lte=to_yearmonth).filter(
                institution_id__gp_id=gp_id
            )
    # Get questiongroups applicable for this survey ID for the given year range
    questiongroup_ids = get_questiongroups_survey(
                                                    survey_id,
                                                    from_yearmonth,
                                                    to_yearmonth)
    # distinct_qgroups = total_answers.distinct('questiongroup_id').values_list(
    #     'questiongroup_id', flat=True)
    schools = total_answers.filter(
        questiongroup_id__in=questiongroup_ids).distinct(
            'institution_id').values_list(
            'institution_id', flat=True)
    # schools = AnswerGroup_Institution.objects.filter(
    #             institution__gp_id=gp_id).filter(
    #                 questiongroup__survey_id=survey_id
    #             ).filter(
    #         date_of_visit__year__gte=from_datetime_obj.year).filter(
    #         date_of_visit__year__lte=to_datetime_obj.year).filter(
    #         date_of_visit__month__gte=from_datetime_obj.month).filter(
    #         date_of_visit__month__lte=to_datetime_obj.month).filter(
    #             questiongroup_id__in=distinct_qgroups).distinct(
    #                 'institution_id').values_list(
    #                 'institution_id', flat=True)
    schools_info = {}
    print("Participating Schools count is: ", schools.count())
    for school in schools:
        school_info = Institution.objects.get(id=school)
        result = {}
        result["school_name"] = school_info.name
        result["district_name"] = school_info.admin1.name
        result["block_name"] = school_info.admin2.name
        result["cluster_name"] = school_info.admin3.name
        result["gp_name"] = school_info.gp.const_ward_name 
        num_students = AnswerGroup_Institution.objects.filter(
                institution__id=school).filter(
                    questiongroup__survey_id=survey_id
                ).filter(
            date_of_visit__year__gte=from_datetime_obj.year).filter(
            date_of_visit__year__lte=to_datetime_obj.year).filter(
            date_of_visit__month__gte=from_datetime_obj.month).filter(
            date_of_visit__month__lte=to_datetime_obj.month).filter(
                questiongroup_id__in=questiongroup_ids).count()
        result["num_students"] = num_students
        total_answers = total_answers.filter(institution_id=school)
        correct_answers = correct_answers.filter(institution_id=school)
        for each_class in questiongroup_ids:
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
                else:
                    total = total.num_assessments

                try:
                    correct = correct_answers_for_class.get(
                        microconcept_id=qgroup_question.question.microconcept)
                except:
                    correct = 0
                else:
                    correct = correct.num_assessments
                percent = 0
                if total is not None and total > 0:
                    sum = total
                    percent = round((correct / sum) * 100,2)
                else:
                    sum = 0
                question_answer_details["question"] =\
                    qgroup_question.question.microconcept.char_id
                question_answer_details["num_correct"] = correct
                question_answer_details["percent"] = percent
                class_questions.append(question_answer_details)
            qgroup = QuestionGroup.objects.get(id=each_class)
            result[qgroup.name] = class_questions
        schools_info[school] = result
    return schools_info
            
            
            
        