import datetime
from assessments.models import QuestionGroup

def convert_to_yearmonth(from_date_str, to_date_str):
    """ Input date format is 2018-06-01 """
    format_str = '%Y-%m-%d'  # The format
    from_datetime_obj = datetime.datetime.strptime(from_date_str, format_str)
    from_yearmonth = from_datetime_obj.strftime('%Y%m')
    to_datetime_obj = datetime.datetime.strptime(to_date_str, format_str)
    to_yearmonth = to_datetime_obj.strftime('%Y%m')
    return from_yearmonth, to_yearmonth


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
    # First convert the date to an academic year format required
    # by the QuestionGroup table
    academic_year = convert_to_academicyear(from_yearmonth, to_yearmonth)
    """ This returns a list of questiongroup ids for a particular
    academic year and survey.Year has to be of format 1819 or 1718 """
    return QuestionGroup.objects.filter(survey_id=survey_id).filter(
        academic_year_id=str(academic_year)
    ).distinct('id').values_list('id', flat=True)