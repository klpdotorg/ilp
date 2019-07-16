import pandas as pd
import psycopg2 as pg
import numpy as np
from pandas.util.testing import assert_frame_equal
from gpcontest.reports.school_compute_numbers import *
from assessments.models import SurveyInstitutionQuestionGroupQDetailsAgg
from gpcontest.reports.generate_report import get_gps_for_academic_year

db_name = None
user_name = None
connection_string = None

def run():
    set_db_connection_params("ilp", "klp")
    #gps = get_gps_for_academic_year(2, 201806, 201903)
    gps = [1035]
    for gp in gps:
        check_all_schools_in_gp(gp, 201806, 201903)

def set_db_connection_params(dbname, username):
    global db_name 
    db_name = dbname
    global user_name 
    user_name = username
    global connection_string 
    connection_string = "dbname=" + db_name + " user=" + user_name

def check_all_schools_in_gp(gp, from_yearmonth, to_yearmonth):
    total_answers = SurveyInstitutionQuestionGroupQDetailsAgg.objects.filter(
        survey_id=2,
        yearmonth__gte=from_yearmonth,
        yearmonth__lte=to_yearmonth).filter(
            institution_id__gp_id=gp
    )
    schools = total_answers.filter(
        questiongroup_id__in=[21,22,23,45,46,47]).distinct(
            'institution_id').values_list(
            'institution_id', flat=True)
    for school in schools:
        check_school_numbers(school, from_yearmonth, to_yearmonth)


def check_school_numbers(school_id, from_yearmonth, to_yearmonth):
    # Get this from the reports code
    school_report = get_school_report(school_id, 2, from_yearmonth, to_yearmonth)
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
            REGEXP_REPLACE(inst.name,'[^a-zA-Z0-9]+',' ', 'g') as school_name
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
    computed_school_info = pd.DataFrame.from_dict(
                           school_report)
    num_contests = len(computed_school_info.columns)
    # CHECK DISTRICT/BLOCK/CLUSTER/GP ids and names
    if ((raw_school_info["school_name"] == computed_school_info.loc["school_name",computed_school_info.columns[0]]).all()
        and (raw_school_info["district_name"] == computed_school_info.loc["district_name",computed_school_info.columns[0]]).all()
        and (raw_school_info["block_name"] == computed_school_info.loc["block_name",computed_school_info.columns[0]]).all()
        and (raw_school_info["gp_id"] == computed_school_info.loc["gp_id",computed_school_info.columns[0]]).all()
        and (raw_school_info["const_ward_name"] == computed_school_info.loc["gp_name",computed_school_info.columns[0]]).all()):
        pass
    else:
        print("RAW and COMPUTED values do not match for school_id %s" % school_id)
        print("RAW data is:")
        print(raw_school_info)
        print("Computed data is:")
        print(computed_school_info)
    print(school_report)
    # Check the qn answers sequence and scores
    qn_ans_percs_sql_raw = """
    SELECT
        temp.instid as institution_id,
        temp.dateofvisit as date_of_visit,
        temp.qgid as questiongroup_id,
        temp.qgname as questiongroup_name,
        temp.sequence as sequence,
        temp.numcorrect as num_correct,
        (temp.numcorrect * 100) / count(DISTINCT ag.id) AS percentage
    FROM
        assessments_answergroup_institution ag,
        ( SELECT DISTINCT
                ag.institution_id AS instid,
                to_char(ag.date_of_visit, 'DD/MM/YYYY') AS dateofvisit,
                qg.id AS qgid,
                qg.name AS qgname,
                qgq.sequence AS SEQUENCE,
                count(ag.id) AS numcorrect
            FROM
                assessments_answergroup_institution ag,
                assessments_questiongroup qg,
                assessments_questiongroup_questions qgq,
                assessments_answerinstitution ans
            WHERE
                ag.questiongroup_id = qg.id
                AND qg.survey_id = 2
                AND to_char(ag.date_of_visit, 'YYYYMM')::int >= :startyearmonth
                AND to_char(ag.date_of_visit, 'YYYYMM')::int <= :endyearmonth
                AND ag.institution_id = {institution_id}
                AND ans.answergroup_id = ag.id
                AND ans.question_id = qgq.question_id
                AND ag.questiongroup_id = qgq.questiongroup_id
            GROUP BY
                ag.institution_id,
                ag.date_of_visit,
                qg.id,
                qg.name,
                qgq.sequence,
                ans.answer
            HAVING
                ans.answer = '1') temp
    WHERE
        temp.qgid = ag.questiongroup_id
        AND temp.dateofvisit = to_char(ag.date_of_visit, 'DD/MM/YYYY')
        AND ag.institution_id = temp.instid
    GROUP BY
        temp.instid,
        temp.dateofvisit,
        temp.qgid,
        temp.qgname,
        temp.sequence,
        temp.numcorrect
    ORDER BY institution_id, questiongroup_id, sequence
"""
    qn_ans_percs_sql_raw = qn_ans_percs.format(institution_id=school_id)
    raw_qn_ans_percs = pd.read_sql_query(qn_ans_percs_sql_raw, con=connection)
    class4_scores = pd.DataFrame.from_dict(
                           school_report['Class 4 Assessment']['question_answers'])