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
    num_children,
    num_users
FROM(SELECT survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.inst_type_id as institution_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.institution_id) as num_schools,
        count(distinct ag.id) as num_assessments,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        count(distinct ag.created_by_id) as num_users
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1,2, 4, 5, 6, 7, 11)
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ag.is_verified=true
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
    num_children,
    num_users
FROM(SELECT survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.inst_type_id as institution_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.institution_id) as num_schools,
        count(distinct ag.id) as num_assessments,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        count(distinct ag.created_by_id) as num_users
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1,2, 4, 5, 6, 7, 11)
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
    num_children,
    num_users
FROM(SELECT 
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.inst_type_id as institution_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct stu.institution_id) as num_schools,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.student_id) as num_children,
        count(distinct ag.created_by_id) as num_users
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
    num_children,
    num_users
FROM(SELECT 
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.inst_type_id as institution_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct stu.institution_id) as num_schools,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.student_id) as num_children,
        count(distinct ag.created_by_id) as num_users
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
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
        and ag.is_verified=true
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
    num_children,
    last_assessment
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
    num_children,
    last_assessment
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ag.is_verified=true
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
    num_children,
    last_assessment
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
    num_children,
    last_assessment
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.inst_type_id,
        qg.source_id,
        ag.is_verified,
        year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_questiongroup_info_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_questiongroup_info_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,questiongroup_id,institution_type,year, month) as id,
    survey_id,
    survey_tag,
    source,
    questiongroup_id,
    institution_type,
    year,
    month,
    num_schools,
    num_assessments,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.source_id as source,
        qg.id as questiongroup_id,
        qg.inst_type_id as institution_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.institution_id) as num_schools,
        count(distinct ag.id) as num_assessments,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        count(distinct ag.created_by_id) as num_users,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.inst_type_id,
        qg.source_id,
        qg.id,
        ag.is_verified,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,questiongroup_id,institution_type,year, month) as id,
    survey_id,
    survey_tag,
    source,
    questiongroup_id,
    institution_type,
    year,
    month,
    num_schools,
    num_assessments,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.source_id as source,
        qg.id as questiongroup_id,
        qg.inst_type_id as institution_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.institution_id) as num_schools,
        count(distinct ag.id) as num_assessments,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        count(distinct ag.created_by_id) as num_users,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.inst_type_id,
        qg.source_id,
        qg.id,
        ag.is_verified,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,questiongroup_id,institution_type,year, month) as id,
    survey_id,
    survey_tag,
    source,
    questiongroup_id,
    institution_type,
    year,
    month,
    num_schools,
    num_assessments,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.source_id as source,
        qg.id as questiongroup_id,
        qg.inst_type_id as institution_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct stu.institution_id) as num_schools,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.student_id) as num_children,
        count(distinct ag.created_by_id) as num_users,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.inst_type_id,
        qg.source_id,
        qg.id,
        ag.is_verified,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,questiongroup_id,institution_type,year, month) as id,
    survey_id,
    survey_tag,
    source,
    questiongroup_id,
    institution_type,
    year,
    month,
    num_schools,
    num_assessments,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.source_id as source,
        qg.id as questiongroup_id,
        qg.inst_type_id as institution_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct stu.institution_id) as num_schools,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.student_id) as num_children,
        count(distinct ag.created_by_id) as num_users,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.inst_type_id,
        qg.source_id,
        qg.id,
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ag.is_verified=true
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
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
        and ag.is_verified=true
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
    num_schools,
    num_children,
    num_users,
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
    num_schools,
    num_children,
    num_users,
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        schools_institution s,
        boundary_boundary b,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ag.is_verified=true
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
    num_schools,
    num_children,
    num_users,
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
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
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
    num_schools,
    num_children,
    num_users,
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        schools_institution s,
        boundary_boundary b,
        assessments_surveytaginstitutionmapping st_instmap
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
        and ag.is_verified=true
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
    num_schools,
    num_children,
    num_users,
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        schools_institution s,
        boundary_electionboundary eb
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.institution_id = s.id
        and (s.gp_id = eb.id or s.ward_id = eb.id or s.mla_id = eb.id or s.mp_id = eb.id) 
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
    num_schools,
    num_children,
    num_users,
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        schools_institution s,
        boundary_electionboundary eb,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.institution_id = s.id
        and (s.gp_id = eb.id or s.ward_id = eb.id or s.mla_id = eb.id or s.mp_id = eb.id) 
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ag.is_verified=true
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
    num_schools,
    num_children,
    num_users,
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
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
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
    num_schools,
    num_children,
    num_users,
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        schools_institution s,
        boundary_electionboundary eb,
        assessments_surveytaginstitutionmapping st_instmap
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        ag.is_verified,
        eb.id,
        year,month)data ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_respondenttype_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_respondenttype_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,respondent_type,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    respondent_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        rt.name as respondent_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.institution_id) as num_schools,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        common_respondenttype rt,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.respondent_type_id = rt.char_id
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        ag.is_verified,
        rt.name,
        b.id,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,respondent_type,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    respondent_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        rt.name as respondent_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.institution_id) as num_schools,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        common_respondenttype rt,
        assessments_surveytaginstitutionmapping st_instmap,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.respondent_type_id = rt.char_id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        ag.is_verified,
        rt.name,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,respondent_type,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    respondent_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        rt.name as respondent_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct stu.institution_id) as num_schools,
        count(distinct ag.student_id) as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        common_respondenttype rt,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and ag.respondent_type_id = rt.char_id
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and stu.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        ag.is_verified,
        rt.name,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,respondent_type,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    respondent_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        rt.name as respondent_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct stu.institution_id) as num_schools,
        count(distinct ag.student_id) as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        common_respondenttype rt,
        assessments_surveytaginstitutionmapping st_instmap,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and ag.respondent_type_id = rt.char_id
        and surveytag.tag_id = st_instmap.tag_id
        and stu.institution_id = st_instmap.institution_id
        and ag.is_verified=true
        and stu.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        b.id,
        ag.is_verified,
        rt.name,
        year,month)data ;



DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_respondenttype_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_respondenttype_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,respondent_type,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    respondent_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        ag.institution_id as institution_id,
        qg.source_id as source,
        rt.name as respondent_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.institution_id) as num_schools,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        common_respondenttype rt
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.respondent_type_id = rt.char_id
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        ag.institution_id,
        qg.source_id,
        ag.is_verified,
        rt.name,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,respondent_type,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    respondent_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        ag.institution_id as institution_id,
        qg.source_id as source,
        rt.name as respondent_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.institution_id) as num_schools,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        common_respondenttype rt,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.respondent_type_id = rt.char_id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        ag.institution_id,
        qg.source_id,
        ag.is_verified,
        rt.name,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,respondent_type,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    respondent_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        stu.institution_id as institution_id,
        qg.source_id as source,
        rt.name as respondent_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct stu.institution_id) as num_schools,
        count(distinct ag.student_id) as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        common_respondenttype rt
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and ag.respondent_type_id = rt.char_id
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        stu.institution_id,
        qg.source_id,
        ag.is_verified,
        rt.name,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,respondent_type,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    respondent_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        stu.institution_id as institution_id,
        qg.source_id as source,
        rt.name as respondent_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct stu.institution_id) as num_schools,
        count(distinct ag.student_id) as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        common_respondenttype rt,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and ag.respondent_type_id = rt.char_id
        and surveytag.tag_id = st_instmap.tag_id
        and stu.institution_id = st_instmap.institution_id
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        stu.institution_id,
        qg.source_id,
        ag.is_verified,
        rt.name,
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        common_respondenttype rt
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.respondent_type_id = rt.char_id
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        common_respondenttype rt,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.respondent_type_id = rt.char_id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ag.is_verified=true
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        common_respondenttype rt
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and ag.respondent_type_id = rt.char_id
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        common_respondenttype rt,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and ag.respondent_type_id = rt.char_id
        and surveytag.tag_id = st_instmap.tag_id
        and stu.institution_id = st_instmap.institution_id
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        ag.is_verified,
        rt.name,
        year,month)data ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_usertype_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_usertype_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,boundary_id,survey_tag,source,user_type,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    user_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        users.user_type_id as user_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.institution_id) as num_schools,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        users_user users,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.created_by_id = users.id
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        ag.is_verified,
	users.user_type_id,
        year,month)data
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,boundary_id,survey_tag,source,user_type,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    user_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        users.user_type_id as user_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.institution_id) as num_schools,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        users_user users,
        assessments_surveytaginstitutionmapping st_instmap,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.created_by_id = users.id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        ag.is_verified,
	users.user_type_id,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,boundary_id,survey_tag,source,user_type,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    user_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        users.user_type_id as user_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct stu.institution_id) as num_schools,
        count(distinct ag.student_id) as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        users_user users,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and ag.created_by_id = users.id
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and stu.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        ag.is_verified,
	users.user_type_id,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,boundary_id,survey_tag,source,user_type,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    user_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        users.user_type_id as user_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct stu.institution_id) as num_schools,
        count(distinct ag.student_id) as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        users_user users,
        assessments_surveytaginstitutionmapping st_instmap,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and ag.created_by_id = users.id
        and surveytag.tag_id = st_instmap.tag_id
        and stu.institution_id = st_instmap.institution_id
        and ag.is_verified=true
        and stu.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        ag.is_verified,
	users.user_type_id,
        year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_usertype_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_usertype_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,user_type,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    user_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        ag.institution_id as institution_id,
        qg.source_id as source,
        ut.user_type_id as user_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.institution_id) as num_schools,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        users_user ut
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.created_by_id = ut.id
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        ag.institution_id,
        qg.source_id,
        ag.is_verified,
        ut.user_type_id,
        year,month)data
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,user_type,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    user_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        ag.institution_id as institution_id,
        qg.source_id as source,
        ut.user_type_id as user_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.institution_id) as num_schools,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        users_user ut,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.created_by_id = ut.id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        ag.institution_id,
        qg.source_id,
        ag.is_verified,
        ut.user_type_id,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,user_type,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    user_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        stu.institution_id as institution_id,
        qg.source_id as source,
        ut.user_type_id as user_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct stu.institution_id) as num_schools,
        count(distinct ag.student_id) as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        users_user ut
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and ag.created_by_id = ut.id
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        stu.institution_id,
        qg.source_id,
        ag.is_verified,
        ut.user_type_id,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,user_type,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    user_type,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        stu.institution_id as institution_id,
        qg.source_id as source,
        ut.user_type_id as user_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct stu.institution_id) as num_schools,
        count(distinct ag.student_id) as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        users_user ut,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and ag.created_by_id = ut.id
        and surveytag.tag_id = st_instmap.tag_id
        and stu.institution_id = st_instmap.institution_id
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        stu.institution_id,
        qg.source_id,
        ag.is_verified,
        ut.user_type_id,
        year,month)data;


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
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.source_id as source,
        ut.user_type_id as user_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.institution_id) as num_schools,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        users_user ut
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.created_by_id = ut.id
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        ag.is_verified,
        ut.user_type_id,
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
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.source_id as source,
        ut.user_type_id as user_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.institution_id) as num_schools,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        users_user ut,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.created_by_id = ut.id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        ag.is_verified,
        ut.user_type_id,
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
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.source_id as source,
        ut.user_type_id as user_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct stu.institution_id) as num_schools,
        count(distinct ag.student_id) as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        users_user ut
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and ag.created_by_id = ut.id
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        ag.is_verified,
        ut.user_type_id,
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
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.source_id as source,
        ut.user_type_id as user_type,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct stu.institution_id) as num_schools,
        count(distinct ag.student_id) as num_children,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        users_user ut,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and ag.created_by_id = ut.id
        and surveytag.tag_id = st_instmap.tag_id
        and stu.institution_id = st_instmap.institution_id
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        ag.is_verified,
        ut.user_type_id,
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
        assessments_question q,
        assessments_answerinstitution ans
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ans.question_id = q.id
        and q.is_featured = true
        and ag.is_verified=true
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
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_question q,
        assessments_answerstudent ans
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        schools_student stu,
        assessments_question q,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.id = ans.answergroup_id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.student_id = stu.id
        and stu.institution_id = st_instmap.institution_id
        and ans.question_id = q.id
        and q.is_featured = true
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        ans.question_id,
        ans.answer,
        year,month)data ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,question_key,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id, 
    source,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        q.key,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,question_key,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id, 
    source,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q,
        assessments_surveytaginstitutionmapping st_instmap,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and q.is_featured = true
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        q.key,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,question_key,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id, 
    source,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        schools_student stu,
        assessments_question q,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and ag.student_id = stu.id
        and stu.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        q.key,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,question_key,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id, 
    source,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        assessments_question q,
        schools_student stu,
        assessments_surveytaginstitutionmapping st_instmap,
        schools_institution s,
        boundary_boundary b
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
        and q.is_featured = true
        and ag.is_verified=true
        and stu.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        q.key,
        year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,question_key,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        ag.institution_id as institution_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        ag.institution_id,
        surveytag.tag_id,
        qg.source_id,
        q.key,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,question_key,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        ag.institution_id as institution_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and q.is_featured = true
        and ag.is_verified=true
    GROUP BY survey.id,
        ag.institution_id,
        surveytag.tag_id,
        qg.source_id,
        q.key,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,question_key,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        stu.institution_id as institution_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        assessments_question q,
        schools_student stu
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and ag.student_id = stu.id
    GROUP BY survey.id,
        surveytag.tag_id,
        stu.institution_id,
        qg.source_id,
        q.key,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,question_key,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        stu.institution_id as institution_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        assessments_question q,
        schools_student stu,
        assessments_surveytaginstitutionmapping st_instmap
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
        and q.is_featured = true
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        stu.institution_id,
        qg.source_id,
        q.key,
        year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,question_key,year, month) as id,
    survey_id,
    survey_tag,
    source,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and q.is_featured = true
        and ag.is_verified=true
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
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        assessments_question q
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        assessments_question q,
        schools_student stu,
        assessments_surveytaginstitutionmapping st_instmap
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
        and q.is_featured = true
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        q.key,
        year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questiongroup_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questiongroup_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,questiongroup_id,question_key,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        qg.name,qg.id,
        q.key,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,questiongroup_id,question_key,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q,
        assessments_surveytaginstitutionmapping st_instmap,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and q.is_featured = true
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        qg.name,qg.id,
        q.key,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,questiongroup_id,question_key,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        assessments_question q,
        schools_institution s,
        boundary_boundary b,
        schools_student stu
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and ag.student_id = stu.id
        and stu.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        qg.name,qg.id,
        q.key,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,questiongroup_id,question_key,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        assessments_question q,
        schools_student stu,
        assessments_surveytaginstitutionmapping st_instmap,
        schools_institution s,
        boundary_boundary b
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
        and q.is_featured = true
        and ag.is_verified=true
        and stu.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        qg.name,qg.id,
        q.key,
        year,month)data;

DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questiongroup_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questiongroup_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,question_key,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        ag.institution_id as institution_id,
        qg.source_id as source,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        ag.institution_id,
        qg.source_id,
        qg.name,qg.id,
        q.key,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,question_key,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        ag.institution_id as institution_id,
        qg.source_id as source,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and q.is_featured = true
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        ag.institution_id,
        qg.source_id,
        qg.name,qg.id,
        q.key,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,question_key,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        stu.institution_id as institution_id,
        qg.source_id as source,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        assessments_question q,
        schools_student stu
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and ag.student_id = stu.id
    GROUP BY survey.id,
        surveytag.tag_id,
        stu.institution_id,
        qg.source_id,
        qg.name,qg.id,
        q.key,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,question_key,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        stu.institution_id as institution_id,
        qg.source_id as source,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        assessments_question q,
        schools_student stu,
        assessments_surveytaginstitutionmapping st_instmap
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
        and q.is_featured = true
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        stu.institution_id,
        qg.source_id,
        qg.name,qg.id,
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
    num_assessments
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
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
    num_assessments
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
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and q.is_featured = true
        and ag.is_verified=true
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
    num_assessments
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
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        assessments_question q
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
    num_assessments
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
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        assessments_question q,
        schools_student stu,
        assessments_surveytaginstitutionmapping st_instmap
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
        and q.is_featured = true
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        qg.name,qg.id,
        q.key,
        year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questiongroup_gender_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questiongroup_gender_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,questiongroup_id,gender,year,month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    gender,
    year,
    month,
    count(ag_id) as num_assessments
from
    (select distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        b.id as boundary_id,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        ans1.answer as gender,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    from assessments_answergroup_institution ag inner join assessments_answerinstitution ans1 on (ag.id=ans1.answergroup_id and ans1.question_id=291),
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        schools_institution s,
        boundary_boundary b
    where
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and ans.question_id=q.id
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.survey_id=2
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    group by ag.id,qg.survey_id,b.id,stmap.tag_id,year,month,source,qg.id, ans1.answer)data
GROUP BY survey_id, survey_tag,boundary_id,source,year,month,questiongroup_id,questiongroup_name,gender ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questiongroup_gender_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questiongroup_gender_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,gender,year,month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    gender,
    year,
    month,
    count(ag_id) as num_assessments
from
    (select distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        ag.institution_id as institution_id,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        ans1.answer as gender,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    from assessments_answergroup_institution ag inner join assessments_answerinstitution ans1 on (ag.id=ans1.answergroup_id and ans1.question_id=291),
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q
    where
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and ans.question_id=q.id
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.survey_id=2
    group by ag.id,qg.survey_id,stmap.tag_id,ag.institution_id,year,month,source,qg.id, ans1.answer)data
GROUP BY survey_id, survey_tag,institution_id,source,year,month,questiongroup_id,questiongroup_name,gender ;



DROP MATERIALIZED VIEW IF EXISTS mvw_survey_questiongroup_gender_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_questiongroup_gender_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,questiongroup_id,gender,year,month) as id,
    survey_id,
    survey_tag,
    source,
    questiongroup_id,
    questiongroup_name,
    gender,
    year,
    month,
    count(ag_id) as num_assessments
from
    (select distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        ans1.answer as gender,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    from assessments_answergroup_institution ag inner join assessments_answerinstitution ans1 on (ag.id=ans1.answergroup_id and ans1.question_id=291),
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q
    where
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and ans.question_id=q.id
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.survey_id=2
    group by ag.id,qg.survey_id,stmap.tag_id,year,month,source,qg.id, ans1.answer)data
GROUP BY survey_id, survey_tag,source,year,month,questiongroup_id,questiongroup_name,gender ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_class_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_class_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,sg_name,question_key,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    sg_name,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        sg.name as sg_name,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        assessments_question q,
        schools_student stu,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        schools_institution s,
        boundary_boundary b
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
        and q.is_featured = true
        and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and sg.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,sg.name,
        q.key,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,sg_name,question_key,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    sg_name,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        sg.name as sg_name,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        assessments_question q,
        schools_student stu,
        assessments_surveytaginstitutionmapping st_instmap,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id = st_instmap.tag_id
        and ag.student_id = stu.id
        and stu.institution_id = st_instmap.institution_id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
        and ag.is_verified=true
        and sg.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        q.key,sg.name,
        year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_class_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_class_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,sg_name,question_key,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    sg_name,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        sg.institution_id as institution_id,
        qg.source_id as source,
        sg.name as sg_name,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
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
        and q.is_featured = true
        and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        sg.institution_id,
        qg.source_id,sg.name,
        q.key,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,sg_name,question_key,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    sg_name,
    year,
    month,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        sg.institution_id as institution_id,
        qg.source_id as source,
        sg.name as sg_name,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
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
        and q.is_featured = true
        and surveytag.tag_id = st_instmap.tag_id
        and ag.student_id = stu.id
        and stu.institution_id = st_instmap.institution_id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        sg.institution_id,
        qg.source_id,
        q.key,sg.name,
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
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.source_id as source,
        sg.name as sg_name,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
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
        and q.is_featured = true
        and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.source_id as source,
        sg.name as sg_name,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        q.key as question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
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
        and q.is_featured = true
        and surveytag.tag_id = st_instmap.tag_id
        and ag.student_id = stu.id
        and stu.institution_id = st_instmap.institution_id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        q.key,sg.name,
        year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_class_gender_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boudary_class_gender_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,sg_name,gender,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    year,
    month,
    sg_name,
    gender,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        sg.name as sg_name,
        stu.gender_id as gender,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and sg.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        sg.name,
        stu.gender_id,
        year,month)data
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,sg_name,gender,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    year,
    month,
    sg_name,
    gender,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        sg.name as sg_name,
        stu.gender_id as gender,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        assessments_surveytaginstitutionmapping st_instmap,
        schools_institution s,
        boundary_boundary b
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
        and ag.is_verified=true
        and sg.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        sg.name,
        stu.gender_id,
        year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_class_gender_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_class_gender_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,sg_name,gender,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    year,
    month,
    sg_name,
    gender,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        sg.institution_id as institution_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        sg.name as sg_name,
        stu.gender_id as gender,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
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
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        sg.institution_id,
        qg.source_id,
        sg.name,
        stu.gender_id,
        year,month)data
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,sg_name,gender,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    year,
    month,
    sg_name,
    gender,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        sg.institution_id as institution_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        sg.name as sg_name,
        stu.gender_id as gender,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        assessments_surveytaginstitutionmapping st_instmap
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        sg.institution_id,
        qg.source_id,
        sg.name,
        stu.gender_id,
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
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        sg.name as sg_name,
        stu.gender_id as gender,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
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
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        sg.name as sg_name,
        stu.gender_id as gender,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        assessments_surveytaginstitutionmapping st_instmap
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        sg.name,
        stu.gender_id,
        year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_class_ans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_class_ans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,sg_name,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    sg_name,
    question_id,
    answer_option,
    year,
    month,
    num_answers
FROM(SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        sg.name as sg_name,
        ans.question_id as question_id,
        ans.answer as answer_option,
        count(ans) as num_answers
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_question q,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and sg.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        b.id,
        sg.name,
        ans.question_id,
        ans.answer,
        year,month)data
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,sg_name,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    sg_name,
    question_id,
    answer_option,
    year,
    month,
    num_answers
FROM(SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        sg.name as sg_name,
        ans.question_id as question_id,
        ans.answer as answer_option,
        count(ans) as num_answers
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        assessments_question q,
        assessments_surveytaginstitutionmapping st_instmap,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
        and surveytag.tag_id = st_instmap.tag_id
        and stu.institution_id = st_instmap.institution_id
        and ag.is_verified=true
        and sg.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        sg.name,
        ans.question_id,
        ans.answer,
        year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_class_ans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_class_ans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,sg_name,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    sg_name,
    question_id,
    answer_option,
    year,
    month,
    num_answers
FROM(SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        sg.institution_id as institution_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        sg.name as sg_name,
        ans.question_id as question_id,
        ans.answer as answer_option,
        count(ans) as num_answers
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_question q,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        sg.institution_id,
        qg.source_id,
        sg.name,
        ans.question_id,
        ans.answer,
        year,month)data
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,sg_name,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    sg_name,
    question_id,
    answer_option,
    year,
    month,
    num_answers
FROM(SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        sg.institution_id as institution_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        sg.name as sg_name,
        ans.question_id as question_id,
        ans.answer as answer_option,
        count(ans) as num_answers
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        assessments_question q,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
        and surveytag.tag_id = st_instmap.tag_id
        and stu.institution_id = st_instmap.institution_id
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        sg.institution_id,
        qg.source_id,
        sg.name,
        ans.question_id,
        ans.answer,
        year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_class_ans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_class_ans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,sg_name,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    source,
    sg_name,
    question_id,
    answer_option,
    year,
    month,
    num_answers
FROM(SELECT
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
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_question q,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
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
    sg_name,
    question_id,
    answer_option,
    year,
    month,
    num_answers
FROM(SELECT
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
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        assessments_question q,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and stusg.academic_year_id = case when to_char(ag.date_of_visit,'MM')::int >5 then to_char(ag.date_of_visit,'YY')||to_char(ag.date_of_visit,'YY')::int+1 else to_char(ag.date_of_visit,'YY')::int-1||to_char(ag.date_of_visit,'YY') end
        and surveytag.tag_id = st_instmap.tag_id
        and stu.institution_id = st_instmap.institution_id
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        sg.name,
        ans.question_id,
        ans.answer,
        year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,question_key,year, month) as id,
    survey_id, 
    survey_tag,
    boundary_id,
    source,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        b.id as boundary_id,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            sum(q.max_score) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is not null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score,
        schools_student stu,
        schools_institution s,
        boundary_boundary b
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.is_verified=true
        and ag.student_id = stu.id
        and stu.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
        GROUP BY q.key,ag.id,b.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source
        having sum(ans.answer::int)=max_score.maxscore)correctanswers
GROUP BY survey_id,survey_tag,boundary_id,source,year,month,question_key
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,question_key,year, month) as id,
    survey_id, 
    survey_tag,
    boundary_id,
    source,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        b.id as boundary_id,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag,
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            count(q.id) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
            and qg.type_id='assessment'
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score,
        schools_institution s,
        boundary_boundary b
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY q.key,ag.id,b.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source
    having count(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id,survey_tag,boundary_id,source,year,month,question_key ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,question_key,year, month) as id,
    survey_id, 
    survey_tag,
    institution_id,
    source,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        stu.institution_id as institution_id,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            sum(q.max_score) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is not null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
            and qg.type_id='assessment'
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score,
        schools_student stu
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.is_verified=true
        and ag.student_id = stu.id
        GROUP BY q.key,ag.id,stu.institution_id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source
        having sum(ans.answer::int)=max_score.maxscore)correctanswers
GROUP BY survey_id,survey_tag,institution_id,source,year,month,question_key
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,question_key,year, month) as id,
    survey_id, 
    survey_tag,
    institution_id,
    source,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        ag.institution_id as institution_id,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag,
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            count(q.id) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
            and qg.type_id='assessment'
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.is_verified=true
    GROUP BY q.key,ag.id,ag.institution_id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source
    having count(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id,survey_tag,institution_id,source,year,month,question_key ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,question_key,year, month) as id,
    survey_id, 
    survey_tag,
    source,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            sum(q.max_score) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is not null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.is_verified=true
        GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source
        having sum(ans.answer::int)=max_score.maxscore)correctanswers
GROUP BY survey_id,survey_tag,source,year,month,question_key
union
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,question_key,year, month) as id,
    survey_id, 
    survey_tag,
    source,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag,
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            count(q.id) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
            and qg.type_id='assessment'
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.is_verified=true
    GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source
    having count(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id,survey_tag,source,year,month,question_key ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questiongroup_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questiongroup_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,questiongroup_id,question_key,year, month) as id,
    survey_id, 
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        b.id as boundary_id,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            sum(q.max_score) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is not null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score,
        schools_student stu,
        schools_institution s,
        boundary_boundary b
    WHERE
    ans.answergroup_id=ag.id
    and ag.questiongroup_id=qg.id
    and qg.id=max_score.qgid
    and ans.question_id=q.id
    and q.key=max_score.key
    and q.is_featured=true
    and stmap.survey_id=qg.survey_id
    and qg.type_id='assessment'
    and ag.is_verified=true
    and ag.student_id = stu.id
    and stu.institution_id = s.id
    and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY q.key,ag.id,b.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source,qg.id,qg.name
    having sum(ans.answer::int)=max_score.maxscore)correctanswers
GROUP BY survey_id,survey_tag,boundary_id,source,year,month,question_key,questiongroup_id,questiongroup_name
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,questiongroup_id,question_key,year, month) as id,
    survey_id, 
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        b.id as boundary_id,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag,
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            count(q.id) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
            and qg.type_id='assessment'
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score,
        schools_institution s,
        boundary_boundary b
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY q.key,ag.id,b.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source,qg.id,qg.name
    having count(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,boundary_id,source,year,month,question_key,questiongroup_id,questiongroup_name;



DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questiongroup_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questiongroup_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,question_key,year, month) as id,
    survey_id, 
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        stu.institution_id as institution_id,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            sum(q.max_score) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is not null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score,
        schools_student stu
    WHERE
    ans.answergroup_id=ag.id
    and ag.questiongroup_id=qg.id
    and qg.id=max_score.qgid
    and ans.question_id=q.id
    and q.key=max_score.key
    and q.is_featured=true
    and stmap.survey_id=qg.survey_id
    and qg.type_id='assessment'
    and ag.is_verified=true
    and ag.student_id = stu.id
    GROUP BY q.key,ag.id,stu.institution_id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source,qg.id,qg.name
    having sum(ans.answer::int)=max_score.maxscore)correctanswers
GROUP BY survey_id,survey_tag,institution_id,source,year,month,question_key,questiongroup_id,questiongroup_name
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,question_key,year, month) as id,
    survey_id, 
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        ag.institution_id as institution_id,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag,
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            count(q.id) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
            and qg.type_id='assessment'
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.is_verified=true
    GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source,qg.id,qg.name,ag.institution_id
    having count(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,institution_id,source,year,month,question_key,questiongroup_id,questiongroup_name;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_questiongroup_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_questiongroup_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag ,source,questiongroup_id,question_key,year, month) as id,
    survey_id, 
    survey_tag,
    source,
    questiongroup_id,
    questiongroup_name,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            sum(q.max_score) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is not null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score
    WHERE
    ans.answergroup_id=ag.id
    and ag.questiongroup_id=qg.id
    and qg.id=max_score.qgid
    and ans.question_id=q.id
    and q.key=max_score.key
    and q.is_featured=true
    and stmap.survey_id=qg.survey_id
    and qg.type_id='assessment'
    and ag.is_verified=true
    GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source,qg.id,qg.name
    having sum(ans.answer::int)=max_score.maxscore)correctanswers
GROUP BY survey_id,survey_tag,source,year,month,question_key,questiongroup_id,questiongroup_name
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag ,source,questiongroup_id,question_key,year, month) as id,
    survey_id, 
    survey_tag,
    source,
    questiongroup_id,
    questiongroup_name,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag,
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            count(q.id) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
            and qg.type_id='assessment'
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.is_verified=true
    GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source,qg.id,qg.name
    having count(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,source,year,month,question_key,questiongroup_id,questiongroup_name;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questiongroup_gender_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questiongroup_gender_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,questiongroup_id,gender,question_key,year,month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    gender,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        b.id as boundary_id,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        ans1.answer as gender,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag inner join assessments_answerinstitution ans1 on (ag.id=ans1.answergroup_id and ans1.question_id=291),
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            count(q.id) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
            and qg.survey_id = 2 
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score,
        schools_institution s,
        boundary_boundary b
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.survey_id=2
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY q.key,ag.id,b.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source,qg.id, ans1.answer,qg.name
    having count(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,boundary_id,source,year,month,question_key,questiongroup_id,questiongroup_name,gender ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questiongroup_gender_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questiongroup_gender_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,gender,question_key,year,month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    gender,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        ag.institution_id as institution_id,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        ans1.answer as gender,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag inner join assessments_answerinstitution ans1 on (ag.id=ans1.answergroup_id and ans1.question_id=291),
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            count(q.id) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
            and qg.survey_id = 2 
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.survey_id=2
        and ag.is_verified=true
    GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source,qg.id, ans1.answer,qg.name,ag.institution_id
    having count(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,source,year,month,question_key,questiongroup_id,questiongroup_name,gender,institution_id ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_questiongroup_gender_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_questiongroup_gender_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,questiongroup_id,gender,question_key,year,month) as id,
    survey_id,
    survey_tag,
    source,
    questiongroup_id,
    questiongroup_name,
    gender,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        ans1.answer as gender,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag inner join assessments_answerinstitution ans1 on (ag.id=ans1.answergroup_id and ans1.question_id=291),
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            count(q.id) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
            and qg.survey_id = 2 
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.survey_id=2
        and ag.is_verified=true
    GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source,qg.id, ans1.answer,qg.name
    having count(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,source,year,month,question_key,questiongroup_id,questiongroup_name,gender ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_class_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_class_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,sg_name,question_key,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    sg_name,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        b.id as boundary_id,
        sg.name as sg_name,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        schools_student stu,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            sum(q.max_score) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is not null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score,
        schools_institution s,
        boundary_boundary b
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.student_id = stu.id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and ag.is_verified=true
        and sg.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source,sg.name,b.id
    having sum(ans.answer::int)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,source,year,month,question_key,sg_name,boundary_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_class_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_class_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,sg_name,question_key,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    sg_name,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        sg.institution_id as institution_id,
        sg.name as sg_name,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        schools_student stu,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            sum(q.max_score) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is not null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.student_id = stu.id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and ag.is_verified=true
    GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source,sg.name,sg.institution_id
    having sum(ans.answer::int)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,source,year,month,question_key,sg_name,institution_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_class_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_class_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,sg_name,question_key,year, month) as id,
    survey_id,
    survey_tag,
    source,
    sg_name,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        sg.name as sg_name,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        schools_student stu,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            sum(q.max_score) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is not null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.student_id = stu.id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and ag.is_verified=true
    GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source,sg.name
    having sum(ans.answer::int)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,source,year,month,question_key,sg_name;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_class_gender_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_class_gender_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,sg_name,gender,question_key,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    sg_name,
    gender,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        b.id as boundary_id,
        sg.name as sg_name,
        stu.gender_id as gender,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        schools_student stu,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            sum(q.max_score) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is not null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score,
        schools_institution s,
        boundary_boundary b
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.student_id = stu.id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and ag.is_verified=true
        and sg.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source,sg.name,stu.gender_id,b.id
    having sum(ans.answer::int)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,source,year,month,question_key,sg_name,gender,boundary_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_class_gender_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_class_gender_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,sg_name,gender,question_key,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    sg_name,
    gender,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        sg.institution_id as institution_id,
        sg.name as sg_name,
        stu.gender_id as gender,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        schools_student stu,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            sum(q.max_score) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is not null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.student_id = stu.id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and ag.is_verified=true
    GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source,sg.name,stu.gender_id,sg.institution_id
    having sum(ans.answer::int)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,source,year,month,question_key,sg_name,gender,institution_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_class_gender_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_class_gender_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,sg_name,gender,question_key,year, month) as id,
    survey_id,
    survey_tag,
    source,
    sg_name,
    gender,
    question_key,
    year,
    month,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        sg.name as sg_name,
        stu.gender_id as gender,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        schools_student stu,
        (SELECT distinct
            qg.id as qgid,
            q.key as key,
            sum(q.max_score) as maxscore
        FROM
            assessments_question q,
            assessments_questiongroup_questions qgq,
            assessments_questiongroup qg
        WHERE
            q.is_featured=true
            and q.max_score is not null
            and qgq.question_id =q.id
            and qgq.questiongroup_id = qg.id
        GROUP BY 
            qg.survey_id,
            qg.id,
            q.key)max_score
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.key=max_score.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.student_id = stu.id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and ag.is_verified=true
    GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,year,month,source,sg.name,stu.gender_id
    having sum(ans.answer::int)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,source,year,month,question_key,sg_name,gender;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_question_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_question_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,question_key,question_id) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    question_key,
    question_id,
    question_desc,
    score
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        ag.institution_id as institution_id, 
        qg.source_id as source,
        q.key as question_key,
        q.id as question_id,
        case q.display_text when '' then q.question_text else q.display_text end as question_desc,
        bool_and(case when ans.answer::int=100 then true else false end) as score
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (4)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        ag.institution_id,
        qg.source_id,
        q.question_text,
        q.key,q.id,q.display_text)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questiongroup_ans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questiongroup_ans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,boundary_id,source,questiongroup_id,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    year,
    month,
    question_id,
    question_desc,
    answer_option,
    num_answers
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        qg.id as questiongroup_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ans.question_id as question_id,
        case q.display_text when '' then q.question_text else q.display_text end as question_desc,
        ans.answer as answer_option,
        count(ans) as num_answers
    FROM assessments_survey survey,
        assessments_questiongroup as qg,
        assessments_answergroup_institution as ag,
        assessments_surveytagmapping as surveytag,
        assessments_question q,
        assessments_answerinstitution ans,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        b.id,
        qg.id,
        q.display_text,
        q.question_text,
        ans.question_id,
        ans.answer,
        year,month)data
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,boundary_id,source,questiongroup_id,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    year,
    month,
    question_id,
    question_desc,
    answer_option,
    num_answers
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        qg.id as questiongroup_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ans.question_id as question_id,
        case q.display_text when '' then q.question_text else q.display_text end as question_desc,
        ans.answer as answer_option,
        count(ans) as num_answers
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q,
        assessments_surveytaginstitutionmapping st_instmap,
        schools_institution s,
        boundary_boundary b 
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ans.question_id = q.id
        and q.is_featured = true
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        qg.id,
        q.display_text,
        q.question_text,
        ans.question_id,
        ans.answer,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,boundary_id,source,questiongroup_id,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    year,
    month,
    question_id,
    question_desc,
    answer_option,
    num_answers
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        qg.id as questiongroup_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ans.question_id as question_id,
        case q.display_text when '' then q.question_text else q.display_text end as question_desc,
        ans.answer as answer_option,
        count(ans) as num_answers
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_question q,
        assessments_answerstudent ans,
        schools_institution s,
        schools_student stu,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and ag.student_id = stu.id
        and stu.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,       
        qg.source_id,
        qg.id,
        q.display_text,
        q.question_text,
        ans.question_id,
        ans.answer,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,boundary_id,source,questiongroup_id,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    year,
    month,
    question_id,
    question_desc,
    answer_option,
    num_answers
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        qg.id as questiongroup_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ans.question_id as question_id,
        case q.display_text when '' then q.question_text else q.display_text end as question_desc,
        ans.answer as answer_option,
        count(ans) as num_answers
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        schools_student stu,
        assessments_question q,
        assessments_surveytaginstitutionmapping st_instmap,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.id = ans.answergroup_id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.student_id = stu.id
        and stu.institution_id = st_instmap.institution_id
        and stu.institution_id = s.id
        and ans.question_id = q.id
        and q.is_featured = true
        and ag.is_verified=true
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,       
        qg.source_id,
        qg.id,
        q.display_text,
        q.question_text,
        ans.question_id,
        ans.answer,
        year,month)data ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questiongroup_ans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questiongroup_ans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,institution_id,questiongroup_id,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    year,
    month,
    question_id,
    question_desc,
    answer_option,
    num_answers
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        s.id as institution_id,
        qg.source_id as source,
        qg.id as questiongroup_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ans.question_id as question_id,
        case q.display_text when '' then q.question_text else q.display_text end as question_desc,
        ans.answer as answer_option,
        count(ans) as num_answers
    FROM assessments_survey survey,
        assessments_questiongroup as qg,
        assessments_answergroup_institution as ag,
        assessments_surveytagmapping as surveytag,
        assessments_question q,
        assessments_answerinstitution ans,
        schools_institution s
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and ag.institution_id = s.id
    GROUP BY survey.id,
        surveytag.tag_id,
        s.id,
        qg.source_id,
        qg.id,
        q.display_text,
        q.question_text,
        ans.question_id,
        ans.answer,
        year,month)data
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,institution_id,questiongroup_id,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    year,
    month,
    question_id,
    question_desc,
    answer_option,
    num_answers
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        s.id as institution_id,
        qg.source_id as source,
        qg.id as questiongroup_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ans.question_id as question_id,
        case q.display_text when '' then q.question_text else q.display_text end as question_desc,
        ans.answer as answer_option,
        count(ans) as num_answers
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q,
        assessments_surveytaginstitutionmapping st_instmap,
        schools_institution s
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ans.question_id = q.id
        and q.is_featured = true
        and ag.is_verified=true
        and ag.institution_id = s.id
    GROUP BY survey.id,
        surveytag.tag_id,
        s.id,
        qg.source_id,
        qg.id,
        q.display_text,
        q.question_text,
        ans.question_id,
        ans.answer,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,institution_id,questiongroup_id,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    year,
    month,
    question_id,
    question_desc,
    answer_option,
    num_answers
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        s.id as institution_id,
        qg.source_id as source,
        qg.id as questiongroup_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ans.question_id as question_id,
        case q.display_text when '' then q.question_text else q.display_text end as question_desc,
        ans.answer as answer_option,
        count(ans) as num_answers
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_question q,
        assessments_answerstudent ans,
        schools_institution s,
        schools_student stu
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and ag.student_id = stu.id
        and stu.institution_id = s.id
    GROUP BY survey.id,
        surveytag.tag_id,
        s.id,       
        qg.source_id,
        qg.id,
        q.display_text,
        q.question_text,
        ans.question_id,
        ans.answer,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,institution_id,questiongroup_id,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    year,
    month,
    question_id,
    question_desc,
    answer_option,
    num_answers
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        s.id as institution_id,
        qg.source_id as source,
        qg.id as questiongroup_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ans.question_id as question_id,
        case q.display_text when '' then q.question_text else q.display_text end as question_desc,
        ans.answer as answer_option,
        count(ans) as num_answers
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        schools_student stu,
        assessments_question q,
        assessments_surveytaginstitutionmapping st_instmap,
        schools_institution s
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.id = ans.answergroup_id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.student_id = stu.id
        and stu.institution_id = st_instmap.institution_id
        and stu.institution_id = s.id
        and ans.question_id = q.id
        and q.is_featured = true
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        s.id,       
        qg.source_id,
        qg.id,
        q.display_text,
        q.question_text,
        ans.question_id,
        ans.answer,
        year,month)data ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_questiongroup_ans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_questiongroup_ans_agg AS
SELECT format('A%s_%s_%s_%s_%s', survey_id,questiongroup_id,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    questiongroup_id,
    year,
    month,
    question_id,
    question_desc,
    answer_option,
    num_answers
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.id as questiongroup_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ans.question_id as question_id,
        case q.display_text when '' then q.question_text else q.display_text end as question_desc,
        ans.answer as answer_option,
        count(ans) as num_answers
    FROM assessments_survey survey,
        assessments_questiongroup as qg,
        assessments_answergroup_institution as ag,
        assessments_surveytagmapping as surveytag,
        assessments_question q,
        assessments_answerinstitution ans
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.id,
        q.display_text,
        q.question_text,
        ans.question_id,
        ans.answer,
        year,month)data
union
SELECT format('A%s_%s_%s_%s_%s', survey_id,questiongroup_id,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    questiongroup_id,
    year,
    month,
    question_id,
    question_desc,
    answer_option,
    num_answers
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.id as questiongroup_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ans.question_id as question_id,
        case q.display_text when '' then q.question_text else q.display_text end as question_desc,
        ans.answer as answer_option,
        count(ans) as num_answers
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.id = ans.answergroup_id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ans.question_id = q.id
        and q.is_featured = true
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.id,
        q.display_text,
        q.question_text,
        ans.question_id,
        ans.answer,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s', survey_id,questiongroup_id,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    questiongroup_id,
    year,
    month,
    question_id,
    question_desc,
    answer_option,
    num_answers
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.id as questiongroup_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ans.question_id as question_id,
        case q.display_text when '' then q.question_text else q.display_text end as question_desc,
        ans.answer as answer_option,
        count(ans) as num_answers
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_question q,
        assessments_answerstudent ans,
        schools_student stu
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
        and ag.student_id = stu.id
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.id,
        q.display_text,
        q.question_text,
        ans.question_id,
        ans.answer,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,questiongroup_id,question_id,answer_option,year, month) as id,
    survey_id,
    survey_tag,
    questiongroup_id,
    year,
    month,
    question_id,
    question_desc,
    answer_option,
    num_answers
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.id as questiongroup_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        ans.question_id as question_id,
        case q.display_text when '' then q.question_text else q.display_text end as question_desc,
        ans.answer as answer_option,
        count(ans) as num_answers
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        assessments_answerstudent ans,
        schools_student stu,
        assessments_question q,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.id = ans.answergroup_id
        and surveytag.tag_id = st_instmap.tag_id
        and ag.student_id = stu.id
        and stu.institution_id = st_instmap.institution_id
        and ans.question_id = q.id
        and q.is_featured = true
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.id,
        q.display_text,
        q.question_text,
        ans.question_id,
        ans.answer,
        year,month)data ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questiongroup_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questiongroup_agg AS
SELECT format('A%s_%s_%s_%s_%s', survey_id,boundary_id,questiongroup_id,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    questiongroup_id,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    num_users,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.id as questiongroup_id,
        b.id as boundary_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.institution_id) as num_schools,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        count(distinct ag.created_by_id) as num_users,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.id,
        ag.is_verified,
        b.id,
        year,month)data
union
SELECT format('A%s_%s_%s_%s_%s', survey_id,boundary_id,questiongroup_id,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    questiongroup_id,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    num_users,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.id as questiongroup_id,
        b.id as boundary_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.institution_id) as num_schools,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        count(distinct ag.created_by_id) as num_users,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        schools_institution s,
        boundary_boundary b,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.id,
        ag.is_verified,
        b.id,
        year,month)data
union
SELECT format('A%s_%s_%s_%s_%s', survey_id,boundary_id,questiongroup_id,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    questiongroup_id,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    num_users,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.id as questiongroup_id,
        b.id as boundary_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct stu.institution_id) as num_schools,
        count(distinct ag.student_id) as num_children,
        count(distinct ag.created_by_id) as num_users,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
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
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.id,
        ag.is_verified,
        b.id,
        year,month)data
union
SELECT format('A%s_%s_%s_%s_%s', survey_id,boundary_id,questiongroup_id,year, month) as id,
    survey_id,
    survey_tag,
    boundary_id,
    questiongroup_id,
    year,
    month,
    num_assessments,
    num_schools,
    num_children,
    num_users,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.id as questiongroup_id,
        b.id as boundary_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct stu.institution_id) as num_schools,
        count(distinct ag.student_id) as num_children,
        count(distinct ag.created_by_id) as num_users,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        schools_institution s,
        boundary_boundary b,
        assessments_surveytaginstitutionmapping st_instmap
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.id,
        ag.is_verified,
        b.id,
        year,month)data ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questiongroup_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questiongroup_agg AS
SELECT format('A%s_%s_%s_%s_%s', survey_id,institution_id,questiongroup_id,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    questiongroup_id,
    year,
    month,
    num_assessments,
    num_children,
    num_users,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.id as questiongroup_id,
        ag.institution_id as institution_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        count(distinct ag.created_by_id) as num_users,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.id,
        ag.is_verified,
        ag.institution_id, 
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s', survey_id,institution_id,questiongroup_id,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    questiongroup_id,
    year,
    month,
    num_assessments,
    num_children,
    num_users,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.id as questiongroup_id,
        ag.institution_id as institution_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        case survey.id when 2 then count(distinct ag.id) else 0 end as num_children,
        count(distinct ag.created_by_id) as num_users,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_surveytaginstitutionmapping st_instmap
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and surveytag.tag_id = st_instmap.tag_id
        and ag.institution_id = st_instmap.institution_id
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.id,
        ag.is_verified,
        ag.institution_id, 
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s', survey_id,institution_id,questiongroup_id,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    questiongroup_id,
    year,
    month,
    num_assessments,
    num_children,
    num_users,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.id as questiongroup_id,
        stu.institution_id as institution_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.student_id) as num_children,
        count(distinct ag.created_by_id) as num_users,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and surveytag.tag_id not in (select distinct tag_id from assessments_surveytaginstitutionmapping)
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.id,
        ag.is_verified,
        stu.institution_id,
        year,month)data
union 
SELECT format('A%s_%s_%s_%s_%s', survey_id,institution_id,questiongroup_id,year, month) as id,
    survey_id,
    survey_tag,
    institution_id,
    questiongroup_id,
    year,
    month,
    num_assessments,
    num_children,
    num_users,
    last_assessment
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        qg.id as questiongroup_id,
        stu.institution_id as institution_id,
        to_char(ag.date_of_visit,'YYYY')::int as year,
        to_char(ag.date_of_visit,'MM')::int as month,
        count(distinct ag.id) as num_assessments,
        count(distinct ag.student_id) as num_children,
        count(distinct ag.created_by_id) as num_users,
        max(ag.date_of_visit) as last_assessment
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.id,
        ag.is_verified,
        stu.institution_id,
        year,month)data;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_tagmapping_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_tagmapping_agg AS
SELECT format('A%s_%s_%s', instmap.tag_id, b.id, instmap.academic_year_id) as id,
    instmap.tag_id as survey_tag,
    b.id as boundary_id, 
    instmap.academic_year_id as academic_year_id,
    count(distinct instmap.institution_id) as num_schools,
    count(distinct stu.id) as num_students
FROM
    assessments_surveytaginstitutionmapping instmap,
    schools_institution s,
    schools_student stu,
    schools_studentstudentgrouprelation stusg,
    schools_studentgroup sg,
    boundary_boundary b,
    assessments_surveytagclassmapping sgmap
WHERE
    instmap.institution_id = s.id
    and s.id = sg.institution_id
    and sg.id = stusg.student_group_id
    and stusg.academic_year_id = instmap.academic_year_id
    and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    and instmap.tag_id = 'gka'
    and instmap.tag_id = sgmap.tag_id
    and instmap.academic_year_id = sgmap.academic_year_id
    and sg.name = sgmap.sg_name
    and stusg.status_id !='DL' and stusg.student_id=stu.id 
    and stu.status_id !='DL'
GROUP BY
    instmap.tag_id,
    b.id,
    instmap.academic_year_id;
