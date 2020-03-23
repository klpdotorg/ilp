import datetime
import calendar
from assessments.models import (
    QuestionGroup,
    SurveyEBoundaryQuestionGroupQuestionKeyAgg,
    AnswerGroup_Institution)
from django.utils import timezone
from django.conf import settings
import pytz

def convert_to_yearmonth(from_date_str, to_date_str):
    """ Input date format is 2018-06-01 """
    format_str = '%Y-%m-%d'  # The format
    from_datetime_obj = datetime.datetime.strptime(from_date_str, format_str)
    from_yearmonth = from_datetime_obj.strftime('%Y%m')
    to_datetime_obj = datetime.datetime.strptime(to_date_str, format_str)
    to_yearmonth = to_datetime_obj.strftime('%Y%m')
    return from_yearmonth, to_yearmonth


def convert_yearmonth_to_fulldate(from_yearmonth, to_yearmonth):
    format_str = '%Y%m'  # The input format
    from_datetime_obj = datetime.datetime.strptime(
        str(from_yearmonth), format_str)
    from_datetime_obj = from_datetime_obj.replace(day=1)
    to_datetime_obj = datetime.datetime.strptime(str(to_yearmonth), format_str)
    from_datetime_obj = pytz.timezone(timezone.get_default_timezone_name()).localize(from_datetime_obj)
    to_datetime_obj = pytz.timezone(timezone.get_default_timezone_name()).localize(to_datetime_obj)
    last_day = calendar.monthrange(
        to_datetime_obj.year, to_datetime_obj.month)[1]
    to_datetime_obj = to_datetime_obj.replace(day=last_day)
    return from_datetime_obj, to_datetime_obj


def convert_to_academicyear(from_yearmonth_str, to_yearmonth_str):
    """ Input date format is 201806. Combine the from year and to years
    and return a string of the format 1819 or 1920 suitable to query some 
    tables in the DB """
    format_str = '%Y%m'  # The input format
    from_datetime_obj = datetime.datetime.strptime(
        str(from_yearmonth_str), format_str)
    from_year_only = from_datetime_obj.strftime('%y')
    to_datetime_obj = datetime.datetime.strptime(str(to_yearmonth_str), format_str)
    to_year_only = to_datetime_obj.strftime('%y')
    if int(to_year_only) == int(from_year_only):
        to_year_only = int(from_year_only) + 1
    result = str(from_year_only) + str(to_year_only)
    return result


def get_all_qgroups_survey(survey_id, from_yearmonth, to_yearmonth):
    return QuestionGroup.objects.filter(
        survey_id=survey_id).values_list(
        'id', flat=True)


def get_questiongroups_survey_for_contestdate(survey_id, gp_id,contest_date_yearmonth):
    return SurveyEBoundaryQuestionGroupQuestionKeyAgg.objects\
        .filter(survey_id=survey_id,
                eboundary_id=gp_id, survey_tag='gka')\
        .filter(yearmonth=contest_date_yearmonth)\
        .distinct('questiongroup_id').values_list(
            'questiongroup_id', flat=True)


def get_questiongroup_names_survey(survey_id, from_yearmonth, to_yearmonth):
    return QuestionGroup.objects.filter(survey_id=survey_id).distinct(
        'name').values_list('name', flat=True)


def get_date_of_contest(gp_survey_id, from_yearmonth, to_yearmonth, school_id=None, gp_id=None):
    """ Method returns dates of contest for both school and gp depending
    on which is passed in """
    from_date, to_date = convert_yearmonth_to_fulldate(
        from_yearmonth, to_yearmonth)
    if gp_id is not None:
        dates_of_contest = AnswerGroup_Institution.objects.filter(institution__gp_id=gp_id).filter(
            questiongroup__survey_id=gp_survey_id).filter(
            date_of_visit__range=[from_date, to_date]
        ).distinct('date_of_visit').values_list('date_of_visit', flat=True)
    elif school_id is not None:
        dates_of_contest = AnswerGroup_Institution.objects.filter(institution_id=school_id).filter(
            questiongroup__survey_id=gp_survey_id).filter(
            date_of_visit__range=[from_date, to_date]
        ).distinct('date_of_visit').values_list('date_of_visit', flat=True)
    localized_dates_of_contests = []
    if dates_of_contest is not None:
       for date in dates_of_contest:
           localized_dates_of_contests.append(timezone.localtime(date))
    formatted_full_dates = []
    yearmonth_dates = []
    for date in localized_dates_of_contests:
        formatted_full_dates.append(date.strftime('%d/%m/%Y'))
        yearmonth_dates.append(date.strftime('%Y%m'))

    print(formatted_full_dates)
    return formatted_full_dates, yearmonth_dates
