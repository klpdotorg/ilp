--Materialized view for surveys
DROP MATERIALIZED VIEW IF EXISTS mvw_survey_summary_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_summary_agg AS
SELECT format('A%s_%s_%s_%s_%s', survey_id,survey_tag,institution_type,year, month) as id,
    survey_id,
    survey_tag,
    institution_type,
    year,
    month,
    num_schools,
    num_assessments,
    num_children
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.inst_type_id as institution_type,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.institution_id) as num_schools,
    count(distinct ag.id) as num_assessments,
    case survey.id when 2 then count(distinct ag.id) else 0 end as num_children
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1,2, 4, 5, 6, 7)
    and surveytag.tag_id = st_instmap.tag_id
    and ag.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.inst_type_id,
    year,month)data
union
SELECT format('A%s_%s_%s_%s_%s', survey_id,survey_tag,institution_type,year, month) as id,
    survey_id,
    survey_tag,
    institution_type,
    year,
    month,
    num_schools,
    num_assessments,
    num_children
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.inst_type_id as institution_type,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.institution_id) as num_schools,
    count(distinct ag.id) as num_assessments,
    case survey.id when 2 then count(distinct ag.id) else 0 end as num_children
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
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s', survey_id,survey_tag,institution_type,year, month) as id,
    survey_id,
    survey_tag,
    institution_type,
    year,
    month,
    num_schools,
    num_assessments,
    num_children
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.inst_type_id as institution_type,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct stu.institution_id) as num_schools,
    count(distinct ag.id) as num_assessments,
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
    qg.inst_type_id,
    year, month)data
union 
SELECT format('A%s_%s_%s_%s_%s', survey_id,survey_tag,institution_type,year, month) as id,
    survey_id,
    survey_tag,
    institution_type,
    year,
    month,
    num_schools,
    num_assessments,
    num_children
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.inst_type_id as institution_type,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct stu.institution_id) as num_schools,
    count(distinct ag.id) as num_assessments,
    count(distinct ag.student_id) as num_children
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_surveytagmapping as surveytag,
    schools_student stu,
    assessments_surveytaginstitutionmapping st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
    and surveytag.tag_id = st_instmap.tag_id
    and stu.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.inst_type_id,
    year,month)data;



DROP MATERIALIZED VIEW IF EXISTS mvw_survey_details_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_details_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,institution_type,year, month) as id,
    survey_id,
    survey_tag,
    source,
    institution_type,
    year,
    month,
    num_schools,
    num_assessments,
    num_children
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    qg.inst_type_id as institution_type,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.institution_id) as num_schools,
    count(distinct ag.id) as num_assessments,
    case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
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
    ag.is_verified,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,institution_type,year, month) as id,
    survey_id,
    survey_tag,
    source,
    institution_type,
    year,
    month,
    num_schools,
    num_assessments,
    num_children
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    qg.inst_type_id as institution_type,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.institution_id) as num_schools,
    count(distinct ag.id) as num_assessments,
    case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
    count(distinct ag.created_by_id) as num_users,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
    and surveytag.tag_id = st_instmap.tag_id
    and ag.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.inst_type_id,
    qg.source_id,
    ag.is_verified,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,institution_type,year, month) as id,
    survey_id,
    survey_tag,
    source,
    institution_type,
    year,
    month,
    num_schools,
    num_assessments,
    num_children
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    qg.inst_type_id as institution_type,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct stu.institution_id) as num_schools,
    count(distinct ag.id) as num_assessments,
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
    qg.source_id,
    ag.is_verified,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,institution_type,year, month) as id,
    survey_id,
    survey_tag,
    source,
    institution_type,
    year,
    month,
    num_schools,
    num_assessments,
    num_children
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    qg.inst_type_id as institution_type,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct stu.institution_id) as num_schools,
    count(distinct ag.id) as num_assessments,
    count(distinct ag.student_id) as num_children,
    count(distinct ag.created_by_id) as num_users,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_surveytagmapping as surveytag,
    schools_student stu,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
    and surveytag.tag_id = st_instmap.tag_id
    and stu.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.inst_type_id,
    qg.source_id,
    ag.is_verified,
    year,month)data;



DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,institution_id,year, month) as id,
    survey_id,
    survey_tag,
    source,
    institution_id,
    year,
    month,
    num_assessments,
    num_children,
    num_users,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    ag.institution_id as institution_id,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
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
    ag.is_verified,
    ag.institution_id, 
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,institution_id,year, month) as id,
    survey_id,
    survey_tag,
    source,
    institution_id,
    year,
    month,
    num_assessments,
    num_children,
    num_users,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    ag.institution_id as institution_id,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
    count(distinct ag.created_by_id) as num_users,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
    and surveytag.tag_id = st_instmap.tag_id
    and ag.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ag.is_verified,
    ag.institution_id, 
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,institution_id,year, month) as id,
    survey_id,
    survey_tag,
    source,
    institution_id,
    year,
    month,
    num_assessments,
    num_children,
    num_users,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    stu.institution_id as institution_id,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
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
    qg.source_id,
    ag.is_verified,
    stu.institution_id,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,institution_id,year, month) as id,
    survey_id,
    survey_tag,
    source,
    institution_id,
    year,
    month,
    num_assessments,
    num_children,
    num_users,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    stu.institution_id as institution_id,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    count(distinct ag.student_id) as num_children,
    count(distinct ag.created_by_id) as num_users,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_surveytagmapping as surveytag,
    schools_student stu,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
    and surveytag.tag_id = st_instmap.tag_id
    and stu.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ag.is_verified,
    stu.institution_id,
    year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,boundary_id,year, month) as id,
    survey_id,
    survey_tag,
    source,
    boundary_id,
    year,
    month,
    num_assessments,
    num_children,
    num_users,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    b.id as boundary_id,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    count(distinct ag.institution_id) as num_schools,
    case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
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
    ag.is_verified,
    b.id,
    year,month)data
union
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,boundary_id,year, month) as id,
    survey_id,
    survey_tag,
    source,
    boundary_id,
    year,
    month,
    num_assessments,
    num_children,
    num_users,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    b.id as boundary_id,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    count(distinct ag.institution_id) as num_schools,
    case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
    count(distinct ag.created_by_id) as num_users,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag,
    schools_institution s,
    boundary_boundary b,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
    and ag.institution_id = s.id
    and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    and surveytag.tag_id = st_instmap.tag_id
    and ag.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ag.is_verified,
    b.id,
    year,month)data
union
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,boundary_id,year, month) as id,
    survey_id,
    survey_tag,
    source,
    boundary_id,
    year,
    month,
    num_assessments,
    num_children,
    num_users,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    b.id as boundary_id,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    count(distinct stu.institution_id) as num_schools,
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
    qg.source_id,
    ag.is_verified,
    b.id,
    year,month)data
union
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,boundary_id,year, month) as id,
    survey_id,
    survey_tag,
    source,
    boundary_id,
    year,
    month,
    num_assessments,
    num_children,
    num_users,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    b.id as boundary_id,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    count(distinct stu.institution_id) as num_schools,
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
    boundary_boundary b,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
    and stu.institution_id = s.id
    and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    and surveytag.tag_id = st_instmap.tag_id
    and stu.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ag.is_verified,
    b.id,
    year,month)data ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_electionboundary_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_electionboundary_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,electionboundary_id,year, month) as id,
    survey_id,
    survey_tag,
    source,
    electionboundary_id,
    year,
    month,
    num_assessments,
    num_children,
    num_users,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    eb.id as electionboundary_id,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    count(distinct ag.institution_id) as num_schools,
    case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
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
    ag.is_verified,
    eb.id,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,electionboundary_id,year, month) as id,
    survey_id,
    survey_tag,
    source,
    electionboundary_id,
    year,
    month,
    num_assessments,
    num_children,
    num_users,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    eb.id as electionboundary_id,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    count(distinct ag.institution_id) as num_schools,
    case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
    count(distinct ag.created_by_id) as num_users,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag,
    schools_institution s,
    boundary_electionboundary eb,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
    and ag.institution_id = s.id
    and (s.gp_id = eb.id or s.ward_id = eb.id or s.mla_id = eb.id or s.mp_id = eb.id) 
    and surveytag.tag_id = st_instmap.tag_id
    and ag.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ag.is_verified,
    eb.id,
    year,month)data
union
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,electionboundary_id,year, month) as id,
    survey_id,
    survey_tag,
    source,
    electionboundary_id,
    year,
    month,
    num_assessments,
    num_children,
    num_users,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    eb.id as electionboundary_id,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    count(distinct stu.institution_id) as num_schools,
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
    qg.source_id,
    ag.is_verified,
    eb.id,
    year,month)data
union
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,electionboundary_id,year, month) as id,
    survey_id,
    survey_tag,
    source,
    electionboundary_id,
    year,
    month,
    num_assessments,
    num_children,
    num_users,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    eb.id as electionboundary_id,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    count(distinct stu.institution_id) as num_schools,
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
    boundary_electionboundary eb,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
    and stu.institution_id = s.id
    and (s.gp_id = eb.id or s.ward_id = eb.id or s.mla_id = eb.id or s.mp_id = eb.id) 
    and surveytag.tag_id = st_instmap.tag_id
    and stu.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ag.is_verified,
    eb.id,
    year,month)data ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_respondenttype_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_respondenttype_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,respondent_type,year, month) as id,
    survey_id,
    survey_tag,
    source,
    respondent_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    rt.name as respondent_type,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    count(distinct ag.institution_id) as num_schools,
    case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag,
    assessments_respondenttype rt
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
    and ag.respondent_type_id = rt.char_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ag.is_verified,
    rt.name,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,respondent_type,year, month) as id,
    survey_id,
    survey_tag,
    source,
    respondent_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    rt.name as respondent_type,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    count(distinct ag.institution_id) as num_schools,
    case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag,
    assessments_respondenttype rt,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
    and ag.respondent_type_id = rt.char_id
    and surveytag.tag_id = st_instmap.tag_id
    and ag.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ag.is_verified,
    rt.name,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,respondent_type,year, month) as id,
    survey_id,
    survey_tag,
    source,
    respondent_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    rt.name as respondent_type,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    count(distinct stu.institution_id) as num_schools,
    count(distinct ag.student_id) as num_children,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_surveytagmapping as surveytag,
    schools_student stu,
    assessments_respondenttype rt
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
    and ag.respondent_type_id = rt.char_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ag.is_verified,
    rt.name,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,respondent_type,year, month) as id,
    survey_id,
    survey_tag,
    source,
    respondent_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    rt.name as respondent_type,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    count(distinct stu.institution_id) as num_schools,
    count(distinct ag.student_id) as num_children,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_surveytagmapping as surveytag,
    schools_student stu,
    assessments_respondenttype rt,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
    and ag.respondent_type_id = rt.char_id
    and surveytag.tag_id = st_instmap.tag_id
    and stu.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ag.is_verified,
    rt.name,
    year,month)data ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_usertype_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_usertype_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,user_type,year, month) as id,
    survey_id,
    survey_tag,
    source,
    user_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    ut.user_type as user_type,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    count(distinct ag.institution_id) as num_schools,
    case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag,
    users_user ut
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
    and ag.created_by_id = ut.id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ag.is_verified,
    ut.user_type,
    year,month)data
union
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,user_type,year, month) as id,
    survey_id,
    survey_tag,
    source,
    user_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    ut.user_type as user_type,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    count(distinct ag.institution_id) as num_schools,
    case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag,
    users_user ut,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
    and ag.created_by_id = ut.id
    and surveytag.tag_id = st_instmap.tag_id
    and ag.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ag.is_verified,
    ut.user_type,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,user_type,year, month) as id,
    survey_id,
    survey_tag,
    source,
    user_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    ut.user_type as user_type,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    count(distinct stu.institution_id) as num_schools,
    count(distinct ag.student_id) as num_children,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_surveytagmapping as surveytag,
    schools_student stu,
    users_user ut
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
    and ag.created_by_id = ut.id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ag.is_verified,
    ut.user_type,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,user_type,year, month) as id,
    survey_id,
    survey_tag,
    source,
    user_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    num_verified_assessments,
    last_assessment
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    ut.user_type as user_type,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    count(distinct ag.id) as num_assessments,
    count(distinct stu.institution_id) as num_schools,
    count(distinct ag.student_id) as num_children,
    case ag.is_verified when true then count(1) end as num_verified_assessments,
    max(ag.date_of_visit) as last_assessment
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_surveytagmapping as surveytag,
    schools_student stu,
    users_user ut,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
    and ag.created_by_id = ut.id
    and surveytag.tag_id = st_instmap.tag_id
    and stu.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ag.is_verified,
    ut.user_type,
    year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_ans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_ans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    source,
    year,
    month,
    question_id,
    answer_option,
    num_answers
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    ans.question_id as question_id,
    ans.answer as answer_option,
    count(ans) as num_answers
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag,
    assessments_answerinstitution ans
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
    and ag.id = ans.answergroup_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ans.question_id,
    ans.answer,
    year,month)data
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    source,
    year,
    month,
    question_id,
    answer_option,
    num_answers
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    ans.question_id as question_id,
    ans.answer as answer_option,
    count(ans) as num_answers
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag,
    assessments_answerinstitution ans,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
    and ag.id = ans.answergroup_id
    and surveytag.tag_id = st_instmap.tag_id
    and ag.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ans.question_id,
    ans.answer,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    source,
    year,
    month,
    question_id,
    answer_option,
    num_answers
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    ans.question_id as question_id,
    ans.answer as answer_option,
    count(ans) as num_answers
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_surveytagmapping as surveytag,
    assessments_answerstudent ans
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.id = ans.answergroup_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ans.question_id,
    ans.answer,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    source,
    year,
    month,
    question_id,
    answer_option,
    num_answers
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    ans.question_id as question_id,
    ans.answer as answer_option,
    count(ans) as num_answers
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_surveytagmapping as surveytag,
    assessments_answerstudent ans,
    schools_student stu,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.id = ans.answergroup_id
    and surveytag.tag_id = st_instmap.tag_id
    and ag.student_id = stu.id
    and stu.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    ans.question_id,
    ans.answer,
    year,month)data ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,question_key,year, month) as id,
    survey_id,
    survey_tag,
    source,
    year,
    month,
    question_key,
    num_assessments,
    num_correct_assessments
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    q.key as question_key,
    count(distinct ag.id) as num_assessments,
    0 as num_correct_assessments
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag,
    assessments_answerinstitution ans,
    assessments_question q
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
    and ag.id = ans.answergroup_id
    and ans.question_id = q.id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    q.key,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,question_key,year, month) as id,
    survey_id,
    survey_tag,
    source,
    year,
    month,
    question_key,
    num_assessments,
    num_correct_assessments
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    q.key as question_key,
    count(distinct ag.id) as num_assessments,
    0 as num_correct_assessments
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag,
    assessments_answerinstitution ans,
    assessments_question q,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
    and ag.id = ans.answergroup_id
    and ans.question_id = q.id
    and surveytag.tag_id = st_instmap.tag_id
    and ag.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    q.key,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,question_key,year, month) as id,
    survey_id,
    survey_tag,
    source,
    year,
    month,
    question_key,
    num_assessments,
    num_correct_assessments
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    q.key as question_key,
    count(distinct ag.id) as num_assessments,
    count(correct.*) as num_correct_assessments
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag left outer join (select distinct ans.answergroup_id id from assessments_answerstudent ans, assessments_question q where ans.question_id=q.id group by ans.answergroup_id having count(case ans.answer=q.pass_score when true then 1 end)=count(ans.*))correct on (correct.id=ag.id),
    assessments_surveytagmapping as surveytag,
    assessments_answerstudent ans,
    assessments_question q
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.id = ans.answergroup_id
    and ans.question_id = q.id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    q.key,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,question_key,year, month) as id,
    survey_id,
    survey_tag,
    source,
    year,
    month,
    question_key,
    num_assessments,
    num_correct_assessments
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    q.key as question_key,
    count(distinct ag.id) as num_assessments,
    count(correct.*) as num_correct_assessments
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag left outer join (select distinct ans.answergroup_id id from assessments_answerstudent ans, assessments_question q where ans.question_id=q.id group by ans.answergroup_id having count(case ans.answer=q.pass_score when true then 1 end)=count(ans.*))correct on (correct.id=ag.id),
    assessments_surveytagmapping as surveytag,
    assessments_answerstudent ans,
    assessments_question q,
    schools_student stu,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.id = ans.answergroup_id
    and ans.question_id = q.id
    and surveytag.tag_id = st_instmap.tag_id
    and ag.student_id = stu.id
    and stu.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    q.key,
    year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_questiongroup_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_questiongroup_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,questiongroup_id,question_key,year, month) as id,
    survey_id,
    survey_tag,
    source,
    questiongroup_id,
    questiongroup_name,
    year,
    month,
    question_key,
    num_assessments,
    num_correct_assessments
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    qg.id as questiongroup_id,
    qg.name as questiongroup_name,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    q.key as question_key,
    count(distinct ag.id) as num_assessments,
    0 as num_correct_assessments
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag,
    assessments_answerinstitution ans,
    assessments_question q
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
    and ag.id = ans.answergroup_id
    and ans.question_id = q.id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    qg.name,qg.id,
    q.key,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,questiongroup_id,question_key,year, month) as id,
    survey_id,
    survey_tag,
    source,
    questiongroup_id,
    questiongroup_name,
    year,
    month,
    question_key,
    num_assessments,
    num_correct_assessments
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    qg.id as questiongroup_id,
    qg.name as questiongroup_name,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    q.key as question_key,
    count(distinct ag.id) as num_assessments,
    0 as num_correct_assessments
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_institution as ag,
    assessments_surveytagmapping as surveytag,
    assessments_answerinstitution ans,
    assessments_question q,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (1, 2, 4, 5, 6, 7)
    and ag.id = ans.answergroup_id
    and ans.question_id = q.id
    and surveytag.tag_id = st_instmap.tag_id
    and ag.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    qg.name,qg.id,
    q.key,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,questiongroup_id,question_key,year, month) as id,
    survey_id,
    survey_tag,
    source,
    questiongroup_id,
    questiongroup_name,
    year,
    month,
    question_key,
    num_assessments,
    num_correct_assessments
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    qg.id as questiongroup_id,
    qg.name as questiongroup_name,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    q.key as question_key,
    count(distinct ag.id) as num_assessments,
    count(correct.*) as num_correct_assessments
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag left outer join (select distinct ans.answergroup_id id from assessments_answerstudent ans, assessments_question q where ans.question_id=q.id group by ans.answergroup_id having count(case ans.answer=q.pass_score when true then 1 end)=count(ans.*))correct on (correct.id=ag.id),
    assessments_surveytagmapping as surveytag,
    assessments_answerstudent ans,
    assessments_question q
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.id = ans.answergroup_id
    and ans.question_id = q.id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    qg.name,qg.id,
    q.key,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,questiongroup_id,question_key,year, month) as id,
    survey_id,
    survey_tag,
    source,
    questiongroup_id,
    questiongroup_name,
    year,
    month,
    question_key,
    num_assessments,
    num_correct_assessments
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    qg.id as questiongroup_id,
    qg.name as questiongroup_name,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    q.key as question_key,
    count(distinct ag.id) as num_assessments,
    count(correct.*) as num_correct_assessments
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag left outer join (select distinct ans.answergroup_id id from assessments_answerstudent ans, assessments_question q where ans.question_id=q.id group by ans.answergroup_id having count(case ans.answer=q.pass_score when true then 1 end)=count(ans.*))correct on (correct.id=ag.id),
    assessments_surveytagmapping as surveytag,
    assessments_answerstudent ans,
    assessments_question q,
    schools_student stu,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.id = ans.answergroup_id
    and ans.question_id = q.id
    and surveytag.tag_id = st_instmap.tag_id
    and ag.student_id = stu.id
    and stu.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    qg.name,qg.id,
    q.key,
    year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_class_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_class_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,sg_name,question_key,year, month) as id,
    survey_id,
    survey_tag,
    source,
    sg_name,
    year,
    month,
    question_key,
    num_assessments,
    num_correct_assessments
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    sg.name as sg_name,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    q.key as question_key,
    count(distinct ag.id) as num_assessments,
    count(correct.*) as num_correct_assessments
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag left outer join (select distinct ans.answergroup_id id from assessments_answerstudent ans, assessments_question q where ans.question_id=q.id group by ans.answergroup_id having count(case ans.answer=q.pass_score when true then 1 end)=count(ans.*))correct on (correct.id=ag.id),
    assessments_surveytagmapping as surveytag,
    assessments_answerstudent ans,
    assessments_question q,
    schools_student stu,
    schools_studentstudentgrouprelation stusg,
    schools_studentgroup sg
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.id = ans.answergroup_id
    and ans.question_id = q.id
    and ag.student_id = stu.id
    and stu.id = stusg.student_id
    and stusg.student_group_id = sg.id
    and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,sg.name,
    q.key,
    year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,sg_name,question_key,year, month) as id,
    survey_id,
    survey_tag,
    source,
    sg_name,
    year,
    month,
    question_key,
    num_assessments,
    num_correct_assessments
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    sg.name as sg_name,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    q.key as question_key,
    count(distinct ag.id) as num_assessments,
    count(correct.*) as num_correct_assessments
FROM assessments_survey survey,
    assessments_questiongroup qg,
    assessments_answergroup_student as ag left outer join (select distinct ans.answergroup_id id from assessments_answerstudent ans, assessments_question q where ans.question_id=q.id group by ans.answergroup_id having count(case ans.answer=q.pass_score when true then 1 end)=count(ans.*))correct on (correct.id=ag.id),
    assessments_surveytagmapping surveytag,
    assessments_answerstudent ans,
    assessments_question q,
    schools_student stu,
    assessments_surveytaginstitutionmapping st_instmap,
    schools_studentstudentgrouprelation stusg,
    schools_studentgroup sg
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.id = ans.answergroup_id
    and ans.question_id = q.id
    and surveytag.tag_id = st_instmap.tag_id
    and ag.student_id = stu.id
    and stu.institution_id = st_instmap.institution_id
    and stu.id = stusg.student_id
    and stusg.student_group_id = sg.id
    and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    q.key,sg.name,
    year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_class_gender_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_class_gender_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,sg_name,gender,year, month) as id,
    survey_id,
    survey_tag,
    source,
    year,
    month,
    sg_name,
    gender,
    num_assessments,
    num_correct_assessments
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    sg.name as sg_name,
    stu.gender_id as gender,
    count(distinct ag.id) as num_assessments,
    count(ag) as num_correct_assessments
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_surveytagmapping as surveytag,
    schools_student stu,
    schools_studentstudentgrouprelation stusg,
    schools_studentgroup sg
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
    and stu.id = stusg.student_id
    and stusg.student_group_id = sg.id
    and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    sg.name,
    stu.gender_id,
    year,month)data
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,sg_name,gender,year, month) as id,
    survey_id,
    survey_tag,
    source,
    year,
    month,
    sg_name,
    gender,
    num_assessments,
    num_correct_assessments
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    sg.name as sg_name,
    stu.gender_id as gender,
    count(distinct ag.id) as num_assessments,
    count(ag) as num_correct_assessments
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_surveytagmapping as surveytag,
    schools_student stu,
    schools_studentstudentgrouprelation stusg,
    schools_studentgroup sg,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
    and stu.id = stusg.student_id
    and stusg.student_group_id = sg.id
    and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
    and surveytag.tag_id = st_instmap.tag_id
    and stu.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    sg.name,
    stu.gender_id,
    year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_class_ans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_class_ans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,sg_name,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    source,
    year,
    month,
    sg_name,
    question_id,
    answer_option,
    num_answers
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    sg.name as sg_name,
    ans.question_id as question_id,
    ans.answer as answer_option,
    count(ans) as num_answers
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_answerstudent ans,
    assessments_surveytagmapping as surveytag,
    schools_student stu,
    schools_studentstudentgrouprelation stusg,
    schools_studentgroup sg
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and ag.id = ans.answergroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
    and stu.id = stusg.student_id
    and stusg.student_group_id = sg.id
    and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    sg.name,
    ans.question_id,
    ans.answer,
    year,month)data
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,sg_name,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    source,
    year,
    month,
    sg_name,
    question_id,
    answer_option,
    num_answers
FROM(
    SELECT
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY')::int as year,
    to_char(ag.date_of_visit,'MM')::int as month,
    sg.name as sg_name,
    ans.question_id as question_id,
    ans.answer as answer_option,
    count(ans) as num_answers
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
    assessments_answerstudent ans,
    assessments_surveytagmapping as surveytag,
    schools_student stu,
    schools_studentstudentgrouprelation stusg,
    schools_studentgroup sg,
    assessments_surveytaginstitutionmapping as st_instmap
WHERE 
    survey.id = qg.survey_id
    and qg.id = ag.questiongroup_id
    and ag.id = ans.answergroup_id
    and survey.id = surveytag.survey_id
    and survey.id in (3)
    and ag.student_id = stu.id
    and stu.id = stusg.student_id
    and stusg.student_group_id = sg.id
    and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
    and surveytag.tag_id = st_instmap.tag_id
    and stu.institution_id = st_instmap.institution_id
GROUP BY survey.id,
    surveytag.tag_id,
    qg.source_id,
    sg.name,
    ans.question_id,
    ans.answer,
    year,month)data;
