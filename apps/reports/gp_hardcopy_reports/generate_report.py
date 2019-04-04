from .gp_compute_numbers import *
from assessments.models import (
    SurveyEBoundaryQuestionGroupQuestionKeyAgg,
    QuestionGroup)
import datetime


def convert_to_yearmonth(from_date_str, to_date_str):
    """ Input date format is 2018-06-01 """
    format_str = '%Y-%m-%d'  # The format
    from_datetime_obj = datetime.datetime.strptime(from_date_str, format_str)
    from_yearmonth = from_datetime_obj.strftime('%Y%m')
    to_datetime_obj = datetime.datetime.strptime(to_date_str, format_str)
    to_yearmonth = to_datetime_obj.strftime('%Y%m')
    return from_yearmonth, to_yearmonth


def convert_to_academicyear(from_date_str, to_date_str):
    """ Input date format is 2018-06-01. Combine the from year and to years
    and return a string of the format 1819 or 1920 suitable to query some 
    tables in the DB """
    format_str = '%Y-%m-%d'  # The format
    from_datetime_obj = datetime.datetime.strptime(from_date_str, format_str)
    from_year_only = from_datetime_obj.strftime('%y')
    to_datetime_obj = datetime.datetime.strptime(to_date_str, format_str)
    to_year_only = to_datetime_obj.strftime('%y')
    return from_year_only + to_year_only


def get_questiongroups_survey(survey_id, from_date, to_date):
    # First convert the date to an academic year format required
    # by the QuestionGroup table
    academic_year = convert_to_academicyear(from_date, to_date)
    print(academic_year)
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


def generate_all_reports(gp_survey_id, from_date, to_date):
    
def generate_gp_summary(gp_id, gp_survey_id, from_date, to_date):
    """
        Take a gp contest survey id and date range in the format of
        YYYY-MM-DD and generate a report
    """
    questiongroup_ids = get_questiongroups_survey(gp_survey_id, from_date, to_date)
    from_yearmonth, to_yearmonth = convert_to_yearmonth(from_date, to_date)
    all_score_buckets = get_gradewise_score_buckets(
        gp_id, questiongroup_ids, from_date, to_date)
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
        result["total"] = all_score_buckets[questiongroup]["total"]
        grade_scores[qgroup.name]["competency_scores"] = result
        grade_scores[qgroup.name]["overall_scores"] = all_score_buckets[questiongroup]
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

   