-- Clear the tables first
DROP MATERIALIZED VIEW IF EXISTS mvw_survey_eboundary_answers_agg CASCADE;
-- Re-populate the tables
CREATE MATERIALIZED VIEW mvw_survey_eboundary_answers_agg AS
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
                answergroup.date_of_visit BETWEEN '2018-06-01' AND '2019-03-31' AND
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
    GROUP BY id,gp_id, questiongroup_id

        

   


