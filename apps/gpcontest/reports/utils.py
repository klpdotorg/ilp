import datetime
import calendar
from assessments.models import QuestionGroup

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
    from_datetime_obj = datetime.datetime.strptime(str(from_yearmonth), format_str)
    from_datetime_obj = from_datetime_obj.replace(day=1)
    to_datetime_obj = datetime.datetime.strptime(str(to_yearmonth), format_str)
    last_day = calendar.monthrange(to_datetime_obj.year, to_datetime_obj.month)[1]
    to_datetime_obj = to_datetime_obj.replace(day=last_day)
    return from_datetime_obj, to_datetime_obj

def convert_to_academicyear(from_yearmonth_str, to_yearmonth_str):
    """ Input date format is 201806. Combine the from year and to years
    and return a string of the format 1819 or 1920 suitable to query some 
    tables in the DB """
    format_str = '%Y%m'  # The input format
    from_datetime_obj = datetime.datetime.strptime(from_yearmonth_str, format_str)
    from_year_only = from_datetime_obj.strftime('%y')
    to_datetime_obj = datetime.datetime.strptime(to_yearmonth_str, format_str)
    to_year_only = to_datetime_obj.strftime('%y')
    if int(to_year_only) == int(from_year_only):
        to_year_only = int(from_year_only) + 1
    result = str(from_year_only) + str(to_year_only)
    return result


def get_questiongroups_survey(survey_id, from_yearmonth, to_yearmonth):
        # Return only questiongroup IDS for which we have assessments
        # available. Will cut down on processing costs later on
        return SurveyEBoundaryQuestionGroupQuestionKeyAgg.objects.filter(
                        survey_id=survey_id).filter(
                                yearmonth__gte=from_yearmonth).filter(
                                const_ward_type='GP').filter(
                                yearmonth__lte=to_yearmonth).order_by(
                                'questiongroup_id').distinct().values_list(
                                'questiongroup_id', flat=True)


def get_questiongroup_names_survey(survey_id, from_yearmonth, to_yearmonth):
        return SurveyEBoundaryQuestionGroupQuestionKeyAgg.objects.filter(
                                survey_id=survey_id).filter(
                                        yearmonth__gte=from_yearmonth).filter(
                                        const_ward_type='GP').filter(
                                        yearmonth__lte=to_yearmonth).order_by(
                                        'questiongroup_name').distinct()\
                                        .values_list(
                                        'questiongroup_name', flat=True)

