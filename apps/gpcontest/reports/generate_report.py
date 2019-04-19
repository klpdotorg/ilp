from .gp_compute_numbers import *
from assessments.models import (
    SurveyEBoundaryQuestionGroupQuestionKeyAgg,
    QuestionGroup)
from .utils import *


def get_questiongroups_survey(survey_id, from_yearmonth, to_yearmonth):
    # First convert the date to an academic year format required
    # by the QuestionGroup table
    academic_year = convert_to_academicyear(from_yearmonth, to_yearmonth)
    """ This returns a list of questiongroup ids for a particular
    academic year and survey.Year has to be of format 1819 or 1718 """
    return QuestionGroup.objects.filter(survey_id=survey_id).filter(
        academic_year_id=academic_year
    ).distinct('id').values_list('id', flat=True)


def get_gps_for_academic_year(gpcontest_survey_id, from_yearmonth, to_yearmonth):
    """ Returns a list of distinct gp_ids for the academic year 
    where gp contest happened """
    return SurveyEBoundaryQuestionGroupQuestionKeyAgg.objects.filter(
        survey_id=gpcontest_survey_id
    ).filter(
        yearmonth__gte=from_yearmonth, yearmonth__lte=to_yearmonth
        ).distinct().values_list('eboundary_id', flat=True)


def generate_all_reports(gp_survey_id, from_yearmonth, to_yearmonth):
    """ Generates reports for ALL GPs in a given time frame for which
    we have data in our DB """
    #from_yearmonth, to_yearmonth = convert_to_yearmonth(from_yearmonth, to_yearmonth)
    gp_ids = get_gps_for_academic_year(gp_survey_id, from_yearmonth,
                                       to_yearmonth)
    schools = Institution.objects.filter(gp_id=gp_ids[0])
    district_name = schools[0].admin1_id.name
    block_name = schools[0].admin2_id.name
    cluster_name = schools[0].admin3_id.name
    all_gps = {
        "district": district_name,
        "block": block_name,
        "cluster": cluster_name,
    }
    for gp in gp_id:
        gp_dict = generate_gp_summary(gp, gp_survey_id, from_yearmonth, to_yearmonth)
        all_gps[gp_id] = gp_dict
        #Call school report code
        #Pass resulting dicts into templates


def generate_gp_summary(gp_id, gp_survey_id, from_yearmonth, to_yearmonth):
    """
        Take a gp contest survey id and date range in the format of
        YYYY-MM-DD and generate a report
    """
    questiongroup_ids = get_questiongroups_survey(gp_survey_id, from_yearmonth, to_yearmonth)
    #from_yearmonth, to_yearmonth = convert_to_yearmonth(from_date, to_date)
    all_score_buckets = get_gradewise_score_buckets(
        gp_id, questiongroup_ids, from_yearmonth, to_yearmonth)
    class4 = None
    class5 = None
    class6 = None
    grade_scores = {}
    for questiongroup in questiongroup_ids:
        qgroup = QuestionGroup.objects.get(id=questiongroup)
        grade_scores[qgroup.name] = {}
        total_answers = get_total_assessments_for_grade(gp_id, questiongroup,
                                                        gp_survey_id,
                                                        from_yearmonth,
                                                        to_yearmonth)
        answers = get_grade_competency_correctscores(
                gp_id, questiongroup, gp_survey_id, from_yearmonth, to_yearmonth
                )
        result = format_answers(total_answers, answers)
        result["total"] = all_score_buckets[qgroup.name]["total"]
        grade_scores[qgroup.name]["competency_scores"] = result
        grade_scores[qgroup.name]["overall_scores"] = all_score_buckets[qgroup.name]
        if "class 6" in qgroup.name.lower():
            percentage = get_grade_competency_percentages(
                                            gp_id, questiongroup,
                                            gp_survey_id,
                                            from_yearmonth, to_yearmonth)
            grade_scores[qgroup.name]["percent_scores"] = percentage
    return grade_scores


def get_total_answers_for_qkey(qkey, queryset):
    return queryset.get(question_key=qkey)["total_answers"]


def format_answers(total_answers_qs, correct_ans_queryset):
    competency_scores = {}
    for each_row in correct_ans_queryset:
        competency_scores[each_row["question_key"]] =\
            each_row["correct_answers"]
    return competency_scores

   