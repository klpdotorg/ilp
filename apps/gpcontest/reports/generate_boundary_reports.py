from gpcontest.models import (
    BoundaryStudentScoreGroups,
    BoundaryCountsAgg
)
from assessments.models import (
    SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg,
    SurveyBoundaryQuestionGroupQuestionKeyAgg
)
from django.db.models import ( Sum )
from collections import OrderedDict


def generate_multiple_bound_reports(
    gp_survey_id, list_boundary_ids, from_yearmonth, to_yearmonth):
    final_report = {}
    for boundary in list_boundary_ids:
        boundary_dict = generate_boundary_report(gp_survey_id, 
                                 boundary, from_yearmonth, to_yearmonth)
        final_report[boundary] = boundary_dict
    return final_report

def generate_boundary_report(
                            gp_survey_id, boundary_id,
                            from_yearmonth, to_yearmonth):
    """
        Returns a report dict for one boundary
    """
    # Identify the type of boundary - SD(district) or SB (block)
    boundary_report = {}
    boundary_stu_score_groups =\
        BoundaryStudentScoreGroups.objects.filter(boundary_id=boundary_id)
    boundary_counts = BoundaryCountsAgg.objects.get(boundary_id=boundary_id)
   
    boundary_report["num_blocks"] = boundary_counts.num_blocks
    boundary_report["num_gps"] = boundary_counts.num_gps
    boundary_report["num_schools"] = boundary_counts.num_schools
    boundary_report["num_students"] = boundary_counts.num_students
    boundary_report["boundary_name"] = boundary_counts.boundary_name
    boundary_report["boundary_id"] = boundary_counts.boundary_id.id
    boundary_report["boundary_type"] = boundary_counts.boundary_type_id.char_id

    competency_scores = get_competency_scores_for_all_qgroups(
        gp_survey_id, boundary_id, from_yearmonth, to_yearmonth
    )
    # Each row is basically a questiongroup or class
    for each_row in boundary_stu_score_groups:
        boundary_report[each_row.questiongroup_name] = {}
        overall_scores = {}
        overall_scores["total"] = each_row.num_students
        overall_scores["below35"] = each_row.cat_a
        overall_scores["35to60"] = each_row.cat_b
        overall_scores["60to75"] = each_row.cat_c
        overall_scores["75to100"] = each_row.cat_d
        boundary_report[each_row.questiongroup_name]["overall_scores"] = overall_scores

        # Find the competency scores
        competencies = competency_scores.filter(
                            questiongroup_name=each_row.questiongroup_name)
        concept_scores = format_competency_answers(competencies)
        boundary_report[each_row.questiongroup_name]["competency_scores"] = \
            concept_scores

        if each_row.questiongroup_name == "Class 6 Assessment":
            percs = get_grade_competency_percentages(
                competency_scores, boundary_id, each_row.questiongroup_name,
                gp_survey_id, from_yearmonth, to_yearmonth)
            boundary_report[each_row.questiongroup_name]["percentage_scores"] = percs
    return boundary_report


def get_grade_competency_percentages(
        correct_answers_qset, boundary_id, qgroup_name, gpcontest_survey_id,
        report_from, report_to):
    """
        Computes the percentage of students who are fluent in a competency
        in the given time frame, survey_id and the Gram Panchayat
        id. Returns a queryset which can be further filtered or manipulated
    """
    correct_answers_agg = correct_answers_qset
    total_assessments = get_total_assessments_for_grade(boundary_id, qgroup_name,
                                                        gpcontest_survey_id,
                                                        report_from,
                                                        report_to)
    results_by_date = {}
    concept_scores = {
            "Number Recognition": 0,
            "Place Value": 'NA',
            "Addition": 0,
            "Subtraction": 0,
            "Multiplication": 0,
            "Division": 0
        }
    if total_assessments is not None and correct_answers_agg is not None: 
        correct_ans_for_date = correct_answers_agg.filter(questiongroup_name=qgroup_name)
        for each_row in total_assessments:
            current_question_key = each_row['question_key']
            sum_total = each_row['total_answers']
            try:
                sum_correct_ans = correct_ans_for_date.get(
                    question_key=current_question_key)['correct_answers']
            except:
                sum_correct_ans = None
            if sum_correct_ans is None:
                sum_correct_ans = 0
            percentage = 0
            if sum_total is not None:
                percentage = round((sum_correct_ans / sum_total)*100, 2)
            else:
                percentage = 0
            concept_scores[current_question_key] = percentage
    return concept_scores


def get_competency_scores_for_all_qgroups(
        gpcontest_survey_id, boundary_id, from_yearmonth, to_yearmonth):
    """
        Returns competency correct score queryset for all grades for a given
        boundary id. Filter the relevant grade (questiongroup name) from here
        for usage.report_from and report_to are
        yearmonth formats
    """
    correct_answers_agg = None
    try:
        correct_answers_agg = \
            SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.objects\
            .filter(survey_id=gpcontest_survey_id,
                    boundary_id=boundary_id, survey_tag='gka')\
            .filter(yearmonth__gte=from_yearmonth)\
            .filter(yearmonth__lte=to_yearmonth)\
            .values('question_key', 'questiongroup_name')\
            .annotate(correct_answers=Sum('num_assessments'))
    except SurveyBoundaryQuestionGroupQuestionKeyCorrectAnsAgg.DoesNotExist:
        pass
    return correct_answers_agg


def get_total_assessments_for_grade(boundary_id, qgroup_name, gpcontest_survey_id,
                                    report_from, report_to):
    """
        Returns total assessments for a given questiongroup name or class. 
        Currently only computed for Class 6 (qgroup_name param). report_from 
        and report_to are yearmonth formats
    """
    total_assessments = None
    try:
        total_assessments = SurveyBoundaryQuestionGroupQuestionKeyAgg.objects\
                .filter(survey_id=gpcontest_survey_id,
                        boundary_id=boundary_id, survey_tag='gka')\
                .filter(questiongroup_name=qgroup_name)\
                .filter(yearmonth__gte=report_from)\
                .filter(yearmonth__lte=report_to)\
                .values('question_key')\
                .annotate(total_answers=Sum('num_assessments'))
    except SurveyBoundaryQuestionGroupQuestionKeyAgg.DoesNotExist:
        pass
    return total_assessments


def format_competency_answers(correct_ans_queryset):
    # Note that below set of competencies is hardcoded. If the template
    # changes we would need to change this. Doing this in lieu of a mat view
    # that will contain rows of competencies taht didn't have a correct ans
    # score.
    competencies = ["Addition", "Subtraction", "Number Recognition",
                    "Place Value", "Multiplication", "Division"]
    competency_scores = {
                "Number Recognition": 0,
                "Place Value": 'NA',
                "Addition": 0,
                "Subtraction": 0,
                "Multiplication": 0,
                "Division": 0
    }
    for competency in competencies:
        try:
            each_row = correct_ans_queryset.get(question_key=competency)
        except:
            each_row = None
        if each_row is not None:
            correctans = each_row["correct_answers"]
            if correctans is None:
                correctans = 0
            competency_scores[competency] =\
                correctans
        # No one got this answer right, send 0 back
        else:
            competency_scores[competency] = 0
    return competency_scores

        
