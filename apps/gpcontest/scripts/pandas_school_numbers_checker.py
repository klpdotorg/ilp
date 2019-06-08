import pandas as pd
import psycopg2 as pg
import numpy as np
from pandas.util.testing import assert_frame_equal
from gpcontest.reports.school_compute_numbers import *
from assessment.models import SurveyInstitutionQuestionGroupQDetailsAgg

db_name = None
user_name = None
connection_string = None

def set_db_connection_params(dbname, username):
    global db_name 
    db_name = dbname
    global user_name 
    user_name = username
    global connection_string 
    connection_string = "dbname=" + db_name + " user=" + user_name

def check_all_schools_in_gp(gp, from_yearmonth, to_yearmonth):
    total_answers = SurveyInstitutionQuestionGroupQDetailsAgg.objects.filter(
        survey_id=survey_id,
        yearmonth__gte=from_yearmonth,
        yearmonth__lte=to_yearmonth).filter(
            institution_id__gp_id=gp
    )
    schools = total_answers.filter(
        questiongroup_id__in=questiongroup_ids).distinct(
            'institution_id').values_list(
            'institution_id', flat=True)
    for school in schools:
        check_school_numbers(school, from_yearmonth, to_yearmonth)


def check_school_numbers(school_id, from_yearmonth, to_yearmonth):
    # Get this from the reports code
    school_report = get_school_report(school, survey_id, from_yearmonth, to_yearmonth)

    #Get the raw data and start comparing
    connection = pg.connect(connection_string)

    # Header details
    raw_school_info_sql = """
            SELECT DISTINCT
            inst.id as school_id,
            gp.id as gp_id,
            gp.const_ward_name,
            district.name as district_name,
            block.name as block_name,
            cluster.name as cluster_name,
            dise.school_code as dise_code,
            inst.name as school_name
        FROM
            schools_institution inst,
            boundary_boundary district,
            boundary_boundary block,
            boundary_boundary CLUSTER,
            boundary_electionboundary gp,
            dise_basicdata dise
        WHERE
            inst.admin1_id = district.id
            AND inst.admin2_id = block.id
            AND inst.admin3_id = cluster.id
            AND inst.dise_id = dise.id
            AND inst.gp_id = gp.id
            AND inst.id IN ({institution_id}); """
    raw_school_info_sql = raw_school_info_sql.format(institution_id=school_id)
    raw_school_info = pd.read_sql_query(raw_school_info_sql, con=connection)
    print(raw_school_info)
    print(school_report)
    


