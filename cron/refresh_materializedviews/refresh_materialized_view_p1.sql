\timing
select now();

CREATE UNIQUE INDEX ON mvw_institution_aggregations (id,gender,mt,religion,category);
REFRESH MATERIALIZED VIEW CONCURRENTLY mvw_institution_aggregations;                                                 
CREATE UNIQUE INDEX ON mvw_survey_boundary_questiongroup_ans_agg(id,survey_tag);
REFRESH MATERIALIZED VIEW CONCURRENTLY mvw_survey_boundary_questiongroup_ans_agg;

select now();
