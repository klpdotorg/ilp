from assessments.models import (
    SurveyInstitutionQuestionGroupQDetailsAgg,
    SurveyInstitutionQuestionGroupQDetailsCorrectAnsAgg,
    SurveyInstitutionQuestionGroupQuestionKeyAgg,
    SurveyInstitutionQuestionGroupQuestionKeyCorrectAnsAgg,
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
from heapq import nsmallest


def compute_deficient_competencies(school_id, survey_id, from_yearmonth, to_yearmonth):
    """
        Return a dictionary with the questiongroup_name and
        array of 3 question keys (competencies) less than 60%
        that the class is most deficient in. 
    """
    deficiency_by_grade = {}
    dates = [from_yearmonth, to_yearmonth]
    correct_answers_agg =\
        SurveyInstitutionQuestionGroupQuestionKeyCorrectAnsAgg.objects.filter(
            survey_id=survey_id,
            institution_id=school_id, yearmonth__range=dates).values(
                'question_key', 'questiongroup_name',
                'num_assessments').annotate(total=Sum('num_assessments'))
    total_assessments = SurveyInstitutionQuestionGroupQuestionKeyAgg.objects\
        .filter(survey_id=survey_id, institution_id=school_id, yearmonth__range=dates)\
        .values('question_key', 'questiongroup_name', 'num_assessments')\
        .annotate(Sum('num_assessments'))
    competency_map = {}
    for each_row in total_assessments:
        sum_total = each_row['num_assessments__sum']
        percent = 0
        total = 0
        total_correct_answers = 0
        try:
            sum_correct_ans = correct_answers_agg.filter(question_key=each_row['question_key'])\
                .get(questiongroup_name=each_row['questiongroup_name'])
            if sum_total is not None:
                total = sum_total
            if sum_correct_ans is None or sum_correct_ans['total'] is None:
                total_correct_answers = 0
            else:
                total_correct_answers = sum_correct_ans['total']
        except Exception as e:
            pass

        if total is not None and total > 0:
            percent = round(total_correct_answers / total * 100, 2)
        # We are only interested in competencies below 60% to call them
        # deficient. Ignore percentages above 60
        if percent < 60.00:
            competency_map[each_row['question_key']] = percent
        three_smallest = nsmallest(3, competency_map, key=competency_map.get)
        deficiency_by_grade[each_row['questiongroup_name']] = three_smallest
    print(deficiency_by_grade)
    return deficiency_by_grade


def get_school_report(gp_id, survey_id, from_yearmonth, to_yearmonth):
    """ From and to date is of the format YYYYMM"""
    format_str = '%Y%m'  # The input format
    from_datetime_obj = datetime.datetime.strptime(
        str(from_yearmonth), format_str)
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
        # Find the lowest 3 competencies below 60% for each class of this
        # school
        deficiencies = compute_deficient_competencies(
                            school, survey_id,
                            from_yearmonth, to_yearmonth)
        school_info = Institution.objects.get(id=school)

        result = {}
        result["school_id"] = school_info.id
        result["school_name"] = school_info.name
        if school_info.dise is not None:
            result["dise_code"] = school_info.dise.school_code
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
            class_details = {}
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
                    percent = round((correct / sum) * 100, 2)
                else:
                    sum = 0
                question_answer_details["question"] =\
                    qgroup_question.question.microconcept.char_id
                question_answer_details["lang_name"] = \
                    qgroup_question.question.lang_name
                question_answer_details["num_correct"] = correct
                question_answer_details["percent"] = percent
                class_questions.append(question_answer_details)
            class_details["question_answers"] = class_questions
            qgroup = QuestionGroup.objects.get(id=each_class)
            # Check if a class exists because sometimes it might not
            if qgroup.name in deficiencies:
                class_details["deficiencies"] = deficiencies[qgroup.name]
            result[qgroup.name] = class_details
        schools_info[school] = result
    return schools_info
