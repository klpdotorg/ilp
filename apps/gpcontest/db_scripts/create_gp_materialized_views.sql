-- Input: 
-- from_date, to_date -- Format is YYYY-MM-DD
-- from_yearmonth, to_yearmonth -- Format is YYYYMM

--  mvw_gpcontest_eboundary_answers_agg -- Stores student scoring
-- categories at the class level per GP
-- Clear the tables first
DROP MATERIALIZED VIEW IF EXISTS mvw_gpcontest_eboundary_answers_agg CASCADE;
-- Re-populate the tables
CREATE MATERIALIZED VIEW mvw_gpcontest_eboundary_answers_agg AS
    WITH subquery1 AS
        (
            SELECT
                format('A%s_%s_%s', 2,eboundary.id,questiongroup.id) as id,
                eboundary.id as gp_id,
                answers.answergroup_id as answergroup_id,
                questiongroup.id as questiongroup_id,
                SUM(
                    CASE WHEN answers.answer~'^\d+(\.\d+)?$' THEN CASE WHEN answers.answer::decimal>0 then answers.answer::decimal ELSE 0
                END ELSE 0 END) AS total_score, 
                (SUM(CASE WHEN answers.answer~'^\d+(\.\d+)?$' THEN CASE
                    WHEN answers.answer::decimal>0 THEN answers.answer::decimal ELSE 0 END ELSE 0 END)/20)*100 AS total_percent
            FROM
                assessments_questiongroup as questiongroup,
                assessments_answerinstitution as answers,
                assessments_answergroup_institution as answergroup,
                boundary_electionboundary as eboundary,
                schools_institution as schools
            WHERE
                questiongroup.survey_id = 2 AND
                questiongroup.id = answergroup.questiongroup_id AND
                answers.answergroup_id = answergroup.id AND
                answergroup.date_of_visit BETWEEN :from_date AND :to_date AND
                answergroup.institution_id = schools.id AND
                schools.gp_id = eboundary.id AND
                answers.question_id NOT IN (130,291)
            GROUP BY
                questiongroup.id,
                answers.answergroup_id,
                eboundary.id
        )
    SELECT id, gp_id, questiongroup_id, 
                    COUNT(*) as num_students,
                    COUNT(1) FILTER (WHERE ROUND(total_percent,2)<36.00) AS cat_a,
                    COUNT(1) FILTER (WHERE ROUND(total_percent,2)>36.00 AND ROUND(total_percent,2)<61.00) as cat_b,
                    COUNT(1) FILTER (WHERE ROUND(total_percent,2)>60.00 AND ROUND(total_percent,2)<76.00) as cat_c,
                    COUNT(1) FILTER (WHERE ROUND(total_percent,2)>75.00 AND ROUND(total_percent,2)<101.00) as cat_d
    FROM subquery1
    GROUP BY id,gp_id, questiongroup_id;
-- END mvw_gpcontest_eboundary_answers_agg

-- mvw_gpcontest_eboundary_schoolcount_agg --> Stores scool counts/GP
-- Clear the tables first
DROP MATERIALIZED VIEW IF EXISTS mvw_gpcontest_eboundary_schoolcount_agg CASCADE;
-- Re-populate the tables
CREATE MATERIALIZED VIEW mvw_gpcontest_eboundary_schoolcount_agg AS
   SELECT 
        format('A%s_%s', 2,eboundary.id) as id,
        eboundary.id as gp_id,
        Count(distinct ag.institution_id) as num_schools 
    FROM 
        boundary_electionboundary as eboundary,
        assessments_answergroup_institution as ag,
        assessments_questiongroup as qg,
        schools_institution as schools
    WHERE 
        qg.survey_id=2 AND 
        qg.id=ag.questiongroup_id AND 
        ag.date_of_visit BETWEEN :from_date AND :to_date AND
        ag.institution_id=schools.id AND
        schools.gp_id=eboundary.id
    GROUP BY eboundary.id;
-- END mvw_gpcontest_eboundary_schoolcount_agg

-- NOTE: Below mvw requires two other materialized views to be pre-populated
-- Assumption is they would already be populated and ready with the data before
-- this is run

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
    t1.yearmonth>=:from_yearmonth and t1.yearmonth<=:to_yearmonth;
-- END
-- mvw_gpcontest_institution_stucount_agg - Stores student count per class
-- Clear the tables first
DROP MATERIALIZED VIEW IF EXISTS mvw_gpcontest_institution_stucount_agg CASCADE;
-- Re-populate the tables
CREATE MATERIALIZED VIEW mvw_gpcontest_institution_stucount_agg AS
   SELECT 
        format('A%s_%s_%s', 2,ag.institution_id,qg.id) as id,
        ag.institution_id as institution_id, 
        qg.id as questiongroup_id, 
        count(distinct ag.id) as num_students 
    FROM 
        assessments_answergroup_institution ag,
        assessments_questiongroup qg 
    WHERE 
        qg.survey_id=2 AND 
        ag.questiongroup_id=qg.id AND 
        ag.date_of_visit BETWEEN :from_date AND :to_date 
    GROUP BY ag.institution_id, qg.id;



        

   


