-- Clear the tables first
DELETE FROM mvw_survey_eboundary_answers_agg;

-- Re-populate the tables

REFRESH MATERIALIZED VIEW CONCURRENTLY mvw_survey_institution_agg


