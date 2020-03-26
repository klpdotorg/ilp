-- Input: 
-- from_date, to_date -- Format is YYYY-MM-DD
--  mvw_gpcontest_eboundary_answers_agg -- Stores student scoring
-- categories at the class level per GP
-- Clear the tables first
-- Re-populate the tables
CREATE MATERIALIZED VIEW mvw_gpcontest_eboundary_answers_agg AS
    WITH subquery1 AS
        (
            SELECT
                format('A%s_%s_%s',questiongroup.survey_id,eboundary.id,questiongroup.id) as id,
                questiongroup.survey_id as survey_id,
                eboundary.id as gp_id,
                answers.answergroup_id as answergroup_id,
                questiongroup.id as questiongroup_id,
                to_char(answergroup.date_of_visit,'YYYYMM')::int as yearmonth,
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
                questiongroup.survey_id IN (2,18) AND
                questiongroup.id = answergroup.questiongroup_id AND
                answers.answergroup_id = answergroup.id AND
                answergroup.date_of_visit BETWEEN :from_date AND :to_date AND
                answergroup.institution_id = schools.id AND
                schools.gp_id = eboundary.id AND
                answers.question_id NOT IN (130,291)
            GROUP BY
                questiongroup.survey_id,
                questiongroup.id,
                answers.answergroup_id,
                eboundary.id,
                answergroup.date_of_visit
        )
    SELECT id, survey_id,gp_id, questiongroup_id, yearmonth,
                    COUNT(*) as num_students,
                    COUNT(1) FILTER (WHERE ROUND(total_percent,2)<35.00) AS cat_a,
                    COUNT(1) FILTER (WHERE ROUND(total_percent,2)>=35.00 AND ROUND(total_percent,2)<=59.00) as cat_b,
                    COUNT(1) FILTER (WHERE ROUND(total_percent,2)>=60.00 AND ROUND(total_percent,2)<=74.00) as cat_c,
                    COUNT(1) FILTER (WHERE ROUND(total_percent,2)>=75.00 AND ROUND(total_percent,2)<=100.00) as cat_d
    FROM subquery1
    GROUP BY id,survey_id, gp_id, questiongroup_id, yearmonth;
-- END mvw_gpcontest_eboundary_answers_agg

-- mvw_gpcontest_eboundary_schoolcount_agg --> Stores scool counts/GP
-- Clear the tables first
-- Re-populate the tables
CREATE MATERIALIZED VIEW mvw_gpcontest_eboundary_schoolcount_agg AS
   SELECT 
        format('A%s_%s', qg.survey_id,eboundary.id) as id,
        qg.survey_id as survey_id,
        eboundary.id as gp_id,
        Count(distinct ag.institution_id) as num_schools,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth
    FROM 
        boundary_electionboundary as eboundary,
        assessments_answergroup_institution as ag,
        assessments_questiongroup as qg,
        schools_institution as schools
    WHERE 
        qg.survey_id IN (2,18) AND 
        qg.id=ag.questiongroup_id AND 
        ag.date_of_visit BETWEEN :from_date AND :to_date AND
        ag.institution_id=schools.id AND
        schools.gp_id=eboundary.id
    GROUP BY survey_id, eboundary.id, ag.date_of_visit;
-- END mvw_gpcontest_eboundary_schoolcount_agg

-- MVW to calculate aggregates for all answers 
-- DROP MATERIALIZED VIEW IF EXISTS mvw_gpcontest_institution_questiongroup_qdetails_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_gpcontest_institution_questiongroup_qdetails_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,question_id,concept,microconcept_group,microconcept,yearmonth) as id,
    survey_id, 
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    question_id,
    concept,
    microconcept_group,
    microconcept,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        ag.institution_id as institution_id,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        q.id as question_id,
        q.concept_id as concept,
        q.microconcept_group_id as microconcept_group,
        q.microconcept_id as microconcept,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag,
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and ag.date_of_visit BETWEEN :from_date AND :to_date
        and qg.survey_id IN (2,18)
        and q.id NOT IN (130,291)
        and ans.question_id=q.id
        and stmap.survey_id=qg.survey_id
        and ag.is_verified=true
    GROUP BY q.concept_id,q.microconcept_group_id,q.microconcept_id,q.id,ag.id,qg.survey_id,stmap.tag_id,ag.date_of_visit,source,qg.id,qg.name,ag.institution_id
    having sum(case ans.answer when 'Yes'then 1 when 'No' then 0 when '1' then 1 when '0' then 0 end)>0)correctans
GROUP BY survey_id, survey_tag,institution_id,source,yearmonth,concept,microconcept_group,microconcept,question_id,questiongroup_id,questiongroup_name;

-- NOTE: Below mvw requires two other materialized views to be pre-populated
-- Assumption is they would already be populated and ready with the data before
-- this is run

-- Drop the tables first
--DROP MATERIALIZED VIEW IF EXISTS mvw_gpcontest_institution_qdetails_percentages_agg;
-- Recreate materialized view
CREATE MATERIALIZED VIEW mvw_gpcontest_institution_qdetails_percentages_agg AS
WITH table1 as (
    SELECT
        format('A%s_%s_%s_%s', t1.institution_id,t1.questiongroup_id,t1.question_id,t1.microconcept) as id,
        t1.survey_id as survey_id,
        t1.institution_id as institution_id,
        t1.question_id as question_id,
        t1.questiongroup_id as questiongroup_id,
        t1.microconcept as microconcept_id,
        t1.num_assessments as total_answers,
        t1.yearmonth as yearmonth,
        CASE WHEN t2.num_assessments IS NULL THEN 0 ELSE t2.num_assessments::int END as correct_answers,
        CASE WHEN t2.num_assessments is NULL THEN 0 ELSE ROUND(100*(t2.num_assessments*1.0/t1.num_assessments*1.0),2) END as percent_score
    FROM
        mvw_survey_institution_questiongroup_qdetails_agg t1
    LEFT JOIN
        mvw_gpcontest_institution_questiongroup_qdetails_correctans_agg t2
    ON t1.id=t2.id
    WHERE
        t1.survey_id IN (2,18) and
        t1.yearmonth>=to_char(:from_date::date,'YYYYMM')::int and 
        t1.yearmonth<=to_char(:to_date::date,'YYYYMM')::int
)
SELECT 
    table1.id as id,
    table1.survey_id as survey_id,
    table1.institution_id as institution_id,
    table1.questiongroup_id as questiongroup_id,
    table1.microconcept_id as microconcept_id,
    table1.total_answers as total_answers,
    table1.correct_answers as correct_answers,
    table1.percent_score as percent_score,
    table1.yearmonth,
    q.id as question_id,
    q.lang_name as question_lang_name,
    qg_qns.sequence as question_sequence
FROM
    table1, 
    assessments_questiongroup_questions qg_qns,
    assessments_question q
WHERE
    qg_qns.question_id=table1.question_id and
    table1.question_id=q.id and
    table1.questiongroup_id= qg_qns.questiongroup_id;

-- END
-- mvw_gpcontest_institution_stucount_agg - Stores student count per class
-- Aggregated by YEARMONTH
-- DROP MATERIALIZED VIEW IF EXISTS mvw_gpcontest_institution_stucount_agg CASCADE;
-- Re-populate the tables
CREATE MATERIALIZED VIEW mvw_gpcontest_institution_stucount_agg AS
   SELECT 
        format('A%s_%s_%s', qg.survey_id,ag.institution_id,qg.id) as id,
        ag.institution_id as institution_id, 
        qg.id as questiongroup_id, 
        qg.name as questiongroup_name,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        count(distinct ag.id) as num_students 
    FROM 
        assessments_answergroup_institution ag,
        assessments_questiongroup qg 
    WHERE 
        qg.survey_id IN (2,18) AND 
        ag.questiongroup_id=qg.id AND 
        ag.date_of_visit BETWEEN :from_date AND :to_date 
    GROUP BY ag.institution_id, qg.id, yearmonth;

---- CREATE THE DEFICIENCY COMPUTATION TABLES-----------
-- Drop the tables first
-- DROP MATERIALIZED VIEW IF EXISTS mvw_gpcontest_concept_percentages_agg;
CREATE MATERIALIZED VIEW mvw_gpcontest_concept_percentages_agg AS
--- Create a subquery with total answers and correct answers -- 
WITH subquery1 AS (
    SELECT
        format('A%s_%s_%s', t1.institution_id,t1.questiongroup_id,t1.question_key) as id,
        t1.institution_id as institution_id,
        t1.questiongroup_id as questiongroup_id,
        t1.question_key as question_key,
        t1.lang_question_key as lang_question_key,
        t1.yearmonth as yearmonth,
        SUM(t1.num_assessments) as total_answers,
        SUM(CASE WHEN t2.num_assessments IS NULL THEN 0 ELSE t2.num_assessments::int END) as correct_answers
    FROM
        mvw_survey_institution_questiongroup_questionkey_agg t1
    LEFT JOIN
        mvw_survey_institution_questiongroup_questionkey_correctans_agg t2
    ON t1.id=t2.id
    WHERE
        t1.survey_id IN (2,18) and
        t1.yearmonth>=to_char(:from_date::date,'YYYYMM')::int and 
        t1.yearmonth<=to_char(:to_date::date,'YYYYMM')::int
    GROUP BY t1.institution_id, t1.questiongroup_id, t1.question_key, t1.lang_question_key, t1.yearmonth
)
-- Now compute percent scores from the above subquery and select only
-- those percentages below 60%
SELECT 
    *, to_char(:from_date::date,'YY') || to_char(:to_date::date,'YY') as year, ROUND((correct_answers*1.0/total_answers*1.0)*100,2) AS percent_score 
FROM subquery1
WHERE ROUND((correct_answers*1.0/total_answers*1.0)*100,2)<60.00;

---MAT VIEW THAT AGGREGATES ALL SCHOOL RELATED INFO IN ONE PLACE TO MINIMIZE
-- QUERIES --
-- DROP MATERIALIZED VIEW IF EXISTS mvw_gpcontest_school_details;
CREATE MATERIALIZED VIEW mvw_gpcontest_school_details AS
    SELECT 
        table1.institution_id as institution_id,
        table1.id as id,
        table1.institution_name as institution_name,
        dise.school_code as dise_code,
        table1.district_name as district_name,
        table1.district_lang_name as district_lang_name,
        table1.block_name as block_name,
        table1.block_lang_name as block_lang_name,
        table1.cluster_name as cluster_name,
        table1.gp_id as gp_id,
        table1.gp_name as gp_name,
        table1.gp_lang_name as gp_lang_name
    FROM
        (SELECT 
            distinct schools.id as institution_id,
            format('A%s_%s', schools.id, schools.dise_id) as id,
            REGEXP_REPLACE(schools.name,'[^a-zA-Z0-9]+',' ', 'g') as institution_name,
            schools.dise_id as dise_id,
            boundary1.name as district_name,
            boundary1.lang_name as district_lang_name,
            boundary2.name as block_name,
            boundary2.lang_name as block_lang_name,
            boundary3.name as cluster_name,
            eboundary.id as gp_id,
            eboundary.const_ward_name as gp_name,
            eboundary.const_ward_lang_name as gp_lang_name
        FROM
            assessments_questiongroup as questiongroup,
            assessments_answergroup_institution as answergroup,
            boundary_electionboundary as eboundary,
            boundary_boundary as boundary1,
            boundary_boundary as boundary2,
            boundary_boundary as boundary3,
            schools_institution as schools
        WHERE
            questiongroup.survey_id IN (2,18) AND
            questiongroup.id = answergroup.questiongroup_id AND
            answergroup.date_of_visit BETWEEN :from_date AND :to_date AND
            answergroup.institution_id = schools.id AND
            schools.gp_id = eboundary.id AND
            schools.admin1_id = boundary1.id AND
            schools.admin2_id = boundary2.id AND
            schools.admin3_id = boundary3.id
        )table1
    LEFT JOIN
        dise_basicdata dise
    ON
        table1.dise_id = dise.id;

---- BOUNDARY LEVEL AGGREGATIONS ---------------------
-- DROP MATERIALIZED VIEW IF EXISTS mvw_gpcontest_boundary_answers_agg CASCADE;
-- Re-populate the tables
CREATE MATERIALIZED VIEW mvw_gpcontest_boundary_answers_agg AS
    WITH subquery1 AS
        (
            SELECT
                format('A%s_%s_%s',questiongroup.survey_id ,boundary.id,questiongroup.id) as id,
                boundary.id as boundary_id,
                boundary.name as boundary_name,
                boundary.boundary_type_id as boundary_type_id,
                answers.answergroup_id as answergroup_id,
                questiongroup.survey_id as survey_id,
                questiongroup.id as questiongroup_id,
                questiongroup.name as questiongroup_name,
                SUM(
                    CASE WHEN answers.answer~'^\d+(\.\d+)?$' THEN CASE WHEN answers.answer::decimal>0 then answers.answer::decimal ELSE 0
                END ELSE 0 END) AS total_score, 
                (SUM(CASE WHEN answers.answer~'^\d+(\.\d+)?$' THEN CASE
                    WHEN answers.answer::decimal>0 THEN answers.answer::decimal ELSE 0 END ELSE 0 END)/20)*100 AS total_percent
            FROM
                assessments_questiongroup as questiongroup,
                assessments_answerinstitution as answers,
                assessments_answergroup_institution as answergroup,
                boundary_boundary as boundary,
                schools_institution as schools
            WHERE
                questiongroup.survey_id IN (2,18) AND
                questiongroup.id = answergroup.questiongroup_id AND
                answers.answergroup_id = answergroup.id AND
                answergroup.date_of_visit BETWEEN :from_date AND :to_date AND
                answergroup.institution_id = schools.id AND
                (schools.admin0_id = boundary.id or schools.admin1_id = boundary.id or schools.admin2_id = boundary.id or schools.admin3_id = boundary.id) AND
                answers.question_id NOT IN (130,291)
            GROUP BY
                questiongroup.id,
                questiongroup.name,
                answers.answergroup_id,
                boundary.id
        )
    SELECT id, survey_id,boundary_id, boundary_type_id, to_char(:from_date::date,'YY') || to_char(:to_date::date,'YY') as year, questiongroup_id, questiongroup_name, boundary_name,
                    COUNT(*) as num_students,
                    COUNT(1) FILTER (WHERE ROUND(total_percent,2)<35.00) AS cat_a,
                    COUNT(1) FILTER (WHERE ROUND(total_percent,2)>=35.00 AND ROUND(total_percent,2)<=59.00) as cat_b,
                    COUNT(1) FILTER (WHERE ROUND(total_percent,2)>=60.00 AND ROUND(total_percent,2)<=74.00) as cat_c,
                    COUNT(1) FILTER (WHERE ROUND(total_percent,2)>=75.00 AND ROUND(total_percent,2)<=100.00) as cat_d
    FROM subquery1
    GROUP BY id,survey_id, boundary_id, boundary_type_id, questiongroup_id, questiongroup_name,boundary_name,year;
-- END mvw_gpcontest_boundary_answers_agg
-- mvw_gpcontest_boundary_counts_agg --> Stores block/GP/schools/num_students count
-- Clear the tables first
-- DROP MATERIALIZED VIEW IF EXISTS mvw_gpcontest_boundary_counts_agg CASCADE;
-- Re-populate the tables
CREATE MATERIALIZED VIEW mvw_gpcontest_boundary_counts_agg AS
WITH schools_count AS (
   SELECT 
        format('A%s_%s',qg.survey_id,boundary.id) as id,
        boundary.id as boundary_id,
        boundary.name as boundary_name,
        boundary.lang_name as boundary_lang_name,
        boundary.boundary_type_id as boundary_type_id,
        to_char(:from_date::date,'YY') || to_char(:to_date::date,'YY') as year,
        Count(distinct ag.institution_id) as num_schools,
        Count(distinct ag.id) as num_students,
	    Count(distinct schools.gp_id) as num_gps,
	(CASE WHEN boundary.boundary_type_id = 'SD' THEN Count(distinct schools.admin2_id) ELSE 0 END) as num_blocks
    FROM 
        boundary_boundary as boundary,
        assessments_answergroup_institution as ag,
        assessments_questiongroup as qg,
        schools_institution as schools
    WHERE 
        qg.survey_id IN (2,18) AND 
        qg.id=ag.questiongroup_id AND 
        ag.date_of_visit BETWEEN :from_date AND :to_date AND
        ag.institution_id=schools.id AND
        (schools.admin0_id = boundary.id or schools.admin1_id = boundary.id or schools.admin2_id = boundary.id or schools.admin3_id = boundary.id)
    GROUP BY qg.survey_id,boundary.id, yearmonth
)
SELECT 
   id, year, boundary_id, boundary_name, boundary_lang_name, boundary_type_id, num_schools, num_students, num_gps, num_blocks
FROM schools_count;

-- END mvw_gpcontest_eboundary_schoolcount_agg
