-- Input to this script is a from_yearmonth and a to_yearmonth of the format 
-- YYYYMM
-- Drop the tables first
DROP MATERIALIZED VIEW IF EXISTS mvw_gpcontest_institution_qdetails_percentages_agg;
-- Recreate materialized view
CREATE MATERIALIZED VIEW mvw_gpcontest_institution_qdetails_percentages_agg AS
SELECT
    format('A%s_%s_%s', t1.institution_id,t1.questiongroup_id,t1.microconcept) as id,
    t1.institution_id as institution_id,
    t1.questiongroup_id as questiongroup_id,
    t1.microconcept as microconcept_id,
    t1.num_assessments as total_answers,
    CASE WHEN t2.num_assessments IS NULL THEN 0 ELSE t2.num_assessments::decimal END as correct_answers,
    CASE WHEN t2.num_assessments is NULL THEN 0 ELSE ROUND(100*(t2.num_assessments*1.0/t1.num_assessments*1.0),2) END as percent_score
FROM
    mvw_survey_institution_questiongroup_qdetails_agg t1
LEFT JOIN
    mvw_survey_institution_questiongroup_qdetails_correctans_agg t2
ON t1.id=t2.id
WHERE
    t1.survey_id=2 and
    t1.yearmonth>=:from_yearmonth and t1.yearmonth<=:to_yearmonth

    