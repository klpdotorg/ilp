\timing
select now();

CREATE UNIQUE INDEX ON mvw_survey_eboundary_questiongroup_ans_agg(id);
REFRESH MATERIALIZED VIEW CONCURRENTLY mvw_survey_eboundary_questiongroup_ans_agg;
CREATE UNIQUE INDEX ON mvw_survey_boundary_questiongroup_qdetails_agg(id);                                   
REFRESH MATERIALIZED VIEW CONCURRENTLY mvw_survey_boundary_questiongroup_qdetails_agg;   
CREATE UNIQUE INDEX ON mvw_survey_institution_questiongroup_ans_agg(id,survey_tag);
REFRESH MATERIALIZED VIEW CONCURRENTLY mvw_survey_institution_questiongroup_ans_agg;
CREATE UNIQUE INDEX ON mvw_survey_boundary_qdetails_agg(id);
REFRESH MATERIALIZED VIEW CONCURRENTLY mvw_survey_boundary_qdetails_agg;                                             
CREATE UNIQUE INDEX ON mvw_boundary_school_category_agg(id);
REFRESH MATERIALIZED VIEW CONCURRENTLY mvw_boundary_school_category_agg;   
CREATE UNIQUE INDEX ON mvw_boundary_school_mgmt_agg(id);                                          
REFRESH MATERIALIZED VIEW CONCURRENTLY mvw_boundary_school_mgmt_agg;                                                 
CREATE UNIQUE INDEX ON mvw_boundary_student_mt_agg(id);
REFRESH MATERIALIZED VIEW CONCURRENTLY mvw_boundary_student_mt_agg;
CREATE UNIQUE INDEX ON mvw_boundary_school_gender_agg(id);                                                  
REFRESH MATERIALIZED VIEW CONCURRENTLY mvw_boundary_school_gender_agg;  
CREATE UNIQUE INDEX ON mvw_boundary_basic_agg(id);
REFRESH MATERIALIZED VIEW CONCURRENTLY mvw_boundary_basic_agg;  
CREATE UNIQUE INDEX ON mvw_boundary_school_moi_agg(id);          
REFRESH MATERIALIZED VIEW CONCURRENTLY mvw_boundary_school_moi_agg;                                                  

select now();
