-- Clear the tables first
DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_stucount_agg CASCADE;
-- Re-populate the tables
CREATE MATERIALIZED VIEW mvw_survey_institution_stucount_agg AS
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

        

   


