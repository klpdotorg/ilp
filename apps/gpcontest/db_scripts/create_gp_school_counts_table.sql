-- Clear the tables first
DROP MATERIALIZED VIEW IF EXISTS mvw_survey_eboundary_schoolcount_agg CASCADE;
-- Re-populate the tables
CREATE MATERIALIZED VIEW mvw_survey_eboundary_schoolcount_agg AS
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