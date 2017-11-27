--Materialized view for surveys
DROP MATERIALIZED VIEW IF EXISTS mvw_survey_summary_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_summary_agg AS
SELECT format('A%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.inst_type_id,to_char(ag.date_of_visit,'YYYY-MM')) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.inst_type_id as institution_type,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    count(distinct ag.institution_id) as num_schools,
    count(ag) as num_assessments,
    case survey.id when 2 then count(ag) else 0 end as num_children
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1,2, 4, 5, 6, 7)
GROUP BY survey.id,
    surveytag.tag_id,
    qg.inst_type_id,
    year_month
union all
SELECT format('A%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.inst_type_id,to_char(ag.date_of_visit,'YYYY-MM')) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.inst_type_id as institution_type,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    count(distinct stu.institution_id) as num_schools,
    count(ag) as num_assessments,
    count(distinct ag.student_id) as num_children
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_surveytagmapping as surveytag,
    schools_student stu
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
GROUP BY survey.id,
    surveytag.tag_id,
    year_month,
    qg.inst_type_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_details_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_details_agg AS
SELECT format('A%s_%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,qg.inst_type_id,to_char(ag.date_of_visit,'YYYY-MM')) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    qg.inst_type_id as institution_type,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    count(distinct ag.institution_id) as num_schools,
    count(ag) as num_assessments,
    case survey.id when 2 then count(ag) else 0 end as num_children,
    count(distinct ag.created_by_id) as num_users,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
GROUP BY survey.id,
    surveytag.tag_id,
    qg.inst_type_id,
    qg.source_id,
    year_month,
    ag.is_verified
union all
SELECT format('A%s_%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,qg.inst_type_id,to_char(ag.date_of_visit,'YYYY-MM')) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    qg.inst_type_id as institution_type,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    count(distinct stu.institution_id) as num_schools,
    count(ag) as num_assessments,
    count(distinct ag.student_id) as num_children,
    count(distinct ag.created_by_id) as num_users,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_surveytagmapping as surveytag,
    schools_student stu
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.inst_type_id,
    year_month,
    qg.source_id,
    ag.is_verified;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_agg AS
SELECT format('A%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,ag.institution_id) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    ag.institution_id as institution_id,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    count(ag) as num_assessments,
    case survey.id when 2 then count(ag) else 0 end as num_children,
    count(distinct ag.created_by_id) as num_users,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    year_month,
    ag.is_verified,
    ag.institution_id
union all
SELECT format('A%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,stu.institution_id) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    stu.institution_id as institution_id,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    count(ag) as num_assessments,
    count(distinct ag.student_id) as num_children,
    count(distinct ag.created_by_id) as num_users,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_surveytagmapping as surveytag,
    schools_student stu
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
GROUP BY survey.id,
    surveytag.tag_id,
    year_month,
    qg.source_id,
    ag.is_verified,
    stu.institution_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_agg AS
SELECT format('A%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,b.id) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    b.id as boundary_id,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    count(ag) as num_assessments,
    case survey.id when 2 then count(ag) else 0 end as num_children,
    count(distinct ag.created_by_id) as num_users,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag,
    schools_institution s,
    boundary_boundary b
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
    and ag.institution_id = s.id
    and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    year_month,
    ag.is_verified,
    b.id
union all
SELECT format('A%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,b.id) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    b.id as boundary_id,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    count(ag) as num_assessments,
    count(distinct ag.student_id) as num_children,
    count(distinct ag.created_by_id) as num_users,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_surveytagmapping as surveytag,
    schools_student stu,
    schools_institution s,
    boundary_boundary b
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
    and stu.institution_id = s.id
    and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
GROUP BY survey.id,
    surveytag.tag_id,
    year_month,
    qg.source_id,
    ag.is_verified,
    b.id;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_electionboundary_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_electionboundary_agg AS
SELECT format('A%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,eb.id) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    eb.id as electionboundary_id,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    count(ag) as num_assessments,
    case survey.id when 2 then count(ag) else 0 end as num_children,
    count(distinct ag.created_by_id) as num_users,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag,
    schools_institution s,
    boundary_electionboundary eb
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
    and ag.institution_id = s.id
    and (s.gp_id = eb.id or s.ward_id = eb.id or s.mla_id = eb.id or s.mp_id = eb.id) 
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    year_month,
    ag.is_verified,
    eb.id
union all
SELECT format('A%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,eb.id) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    eb.id as electionboundary_id,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    count(ag) as num_assessments,
    count(distinct ag.student_id) as num_children,
    count(distinct ag.created_by_id) as num_users,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_surveytagmapping as surveytag,
    schools_student stu,
    schools_institution s,
    boundary_electionboundary eb
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
    and stu.institution_id = s.id
    and (s.gp_id = eb.id or s.ward_id = eb.id or s.mla_id = eb.id or s.mp_id = eb.id) 
GROUP BY survey.id,
    surveytag.tag_id,
    year_month,
    qg.source_id,
    ag.is_verified,
    eb.id;
