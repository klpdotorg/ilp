#!/usr/bin/env python
# coding: utf-8

# <h2>Import Pandas and psycopg2</h2>

# In[1]:


import pandas as pd
import psycopg2 as pg
import numpy as np
from pandas.util.testing import assert_frame_equal

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


# In[2]:
def check_gp_numbers(gpid):
    connection = pg.connect(connection_string)
    # ## Get the raw score buckets data

    # In[3]:


    raw_gp_score_buckets = """SELECT
        data.qgid as questiongroup_id,
        data.yearmonth,
        data1.numstu as num_students,
        sum(
            CASE WHEN percentage <= 35 THEN
                1
            END) AS cat_a,
        sum(
            CASE WHEN percentage <= 60
                AND percentage > 35 THEN
                1
            END) AS cat_b,
        sum(
            CASE WHEN percentage > 60
                AND percentage <= 75 THEN
                1
            END) AS cat_c,
        sum(
            CASE WHEN percentage > 75 THEN
                1
            END) AS cat_d
    FROM ( 
        SELECT DISTINCT
            ag.questiongroup_id qgid,
            to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
            ag.id agid,
            ROUND(sum(ans.answer::int) * 100 / 20) percentage
        FROM
            assessments_answergroup_institution ag,
            assessments_answerinstitution ans
        WHERE
            ans.answergroup_id = ag.id
            AND
            ag.date_of_visit BETWEEN {from_date} AND {to_date}
            AND ag.questiongroup_id IN (
                SELECT
                    id
                FROM
                    assessments_questiongroup
                WHERE
                    survey_id = 2)
                AND ag.institution_id IN (
                    SELECT
                        id
                    FROM
                        schools_institution
                    WHERE
                        gp_id = {gp_id})
                AND ans.question_id NOT IN (291, 130)
        GROUP BY
            ag.questiongroup_id,
            ag.id, 
            yearmonth) data,
        ( SELECT DISTINCT
                ag.questiongroup_id qgid,
                to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
                count(DISTINCT ag.id) AS numstu
            FROM
                assessments_answergroup_institution ag
            WHERE
                ag.date_of_visit BETWEEN {from_date} AND {to_date}
                AND ag.questiongroup_id IN (
                    SELECT
                        id
                    FROM
                        assessments_questiongroup
                    WHERE
                        survey_id = 2)
                    AND ag.institution_id IN (
                        SELECT
                            id
                        FROM
                            schools_institution
                        WHERE
                            gp_id = {gp_id})
            GROUP BY
                ag.questiongroup_id, yearmonth) data1
    WHERE
        data.qgid = data1.qgid AND data.yearmonth = data1.yearmonth
    GROUP BY
        data.qgid,
        data.yearmonth,
        data1.numstu
    ORDER BY
        data.qgid, data.yearmonth;
    """
    raw_gp_score_buckets = raw_gp_score_buckets.format(gp_id=gpid, from_date="'2018-06-01'", to_date="'2019-03-31'")


    # In[4]:


    score_buckets = pd.read_sql_query(raw_gp_score_buckets,con=connection)
    score_buckets = score_buckets.replace(np.nan, 0, regex=True)
    score_buckets=score_buckets.round().astype(int)
    score_buckets.sort_values("questiongroup_id", axis = 0, ascending = True, 
                    inplace = True, na_position ='last') 

    # In[5]:


    # In[6]:


    computed_gp_score_buckets = """
    SELECT 
        questiongroup_id, 
        yearmonth, 
        num_students, cat_a, cat_b, cat_c, cat_d from mvw_gpcontest_eboundary_answers_agg WHERE
    gp_id={gp_id} ORDER BY questiongroup_id, yearmonth
    """
    computed_gp_score_buckets = computed_gp_score_buckets.format(gp_id=gpid)
    computed_score_buckets = pd.read_sql_query(computed_gp_score_buckets, con=connection)
    computed_score_buckets.sort_values("questiongroup_id", axis = 0, ascending = True, 
                    inplace = True, na_position ='last') 
    sum_of_all_cats = computed_score_buckets['cat_a'] + computed_score_buckets['cat_b'] +computed_score_buckets['cat_c'] + computed_score_buckets['cat_d']
    if (np.array_equal(sum_of_all_cats.values,computed_score_buckets['num_students'].values)):
        pass
    else:
        print("GP id {gp} sums of num students don't tally with score groups breakdown".format(gp=gpid))
        print(computed_score_buckets)
    if(np.array_equal(score_buckets.values, computed_score_buckets.values)):
        pass
    else:
        print("GP id {gp} dataframes don't match".format(gp=gpid))
        print("RAW Data query yields")
        print("=====================")
        print(score_buckets)
        print("Computed MVW results yields")
        print("=====================")
        print(computed_score_buckets)



    # In[9]:


    competency_percs = """SELECT
        data.key,
        data.qgid,
        data.yearmonth,
        data1.numstu as num_students,
        count(data.agid) as correct_ans,
        (count(data.agid) * 100) / data1.numstu as percentage
    FROM ( SELECT DISTINCT
            qmap.key AS KEY,
            ag.questiongroup_id AS qgid,
            qmap.max_score,
            ag.id AS agid,
            to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
            sum(ans.answer::int) AS answer
        FROM
            assessments_competencyquestionmap qmap,
            assessments_answergroup_institution ag,
            assessments_answerinstitution ans
        WHERE
            ag.id = ans.answergroup_id
            AND ag.questiongroup_id = qmap.questiongroup_id
            AND ans.question_id = qmap.question_id
            AND ag.date_of_visit BETWEEN {from_date} AND {to_date}
            AND ag.institution_id IN (
                SELECT
                    id
                FROM
                    schools_institution
                WHERE
                    gp_id = {gp_id})
            GROUP BY
                qmap.key,
                ag.questiongroup_id,
                qmap.max_score,
                ag.id,
                yearmonth
            HAVING
                sum(ans.answer::int) >= sum(qmap.max_score)) data,
        ( SELECT DISTINCT
                ag.questiongroup_id qgid,
                to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
                count(DISTINCT ag.id) AS numstu
            FROM
                assessments_answergroup_institution ag
            WHERE
                ag.date_of_visit BETWEEN {from_date} AND {to_date}
                AND ag.questiongroup_id IN (
                    SELECT
                        id
                    FROM
                        assessments_questiongroup
                    WHERE
                        survey_id = 2)
                    AND ag.institution_id IN (
                        SELECT
                            id
                        FROM
                            schools_institution
                        WHERE
                            gp_id = {gp_id})
                    GROUP BY
                        ag.questiongroup_id, yearmonth) data1
    WHERE
        data.qgid = data1.qgid AND data.yearmonth = data1.yearmonth
    GROUP BY
        data.key,
        data.qgid,
        data.yearmonth,
        data1.numstu
    ORDER BY
        data.qgid, data.yearmonth;
    """
    competency_percs_raw_sql = competency_percs.format(gp_id=gpid, from_date="'2018-06-01'", to_date="'2019-03-31'")


    # In[14]:


    percs_raw = pd.read_sql_query(competency_percs_raw_sql,con=connection)
    sql_percs_computed = """SELECT eboundary_id, questiongroup_id, question_key, yearmonth, Sum(num_assessments) as correctans FROM mvw_survey_eboundary_questiongroup_questionkey_correctans_agg
    WHERE eboundary_id={gp_id} and yearmonth>=to_char({from_date}::date, 'YYYYMM')::int and 
    yearmonth<=to_char({to_date}::date, 'YYYYMM')::int 
    GROUP BY
    eboundary_id,
    yearmonth,
    questiongroup_id,
    question_key
    ORDER BY
    questiongroup_id,
    yearmonth
    """
    sql_percs_computed = sql_percs_computed.format(gp_id=gpid, from_date="'2018-06-01'", to_date="'2019-03-31'")
    percs_computed = pd.read_sql_query(sql_percs_computed,con=connection)
    percs_computed['correctans'] = percs_computed['correctans'].round().astype(int)
    if(np.array_equal(percs_computed['correctans'], percs_raw['correct_ans'])):
        pass
    else:
        str = "GP id {gp} competency breakdown numbers do not match or there are anomalies. Check". format(gp=gpid)
        print(str)
        print("RAW Data query yields")
        print("=====================")
        print(percs_raw)
        print("Computed MVW results yields")
        print("=====================")
        print(percs_computed)

    if percs_raw['percentage'].values.any() > 100:
        print("Competency percentages exceed hundred! ANOMALY. Check gp id {gp}".format(gp=gpid))
        print(percs_raw['percentage'])

