DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_agg AS
SELECT format('A%s_%s_%s_%s_%s', survey_id,survey_tag,source,institution_id,yearmonth) as id,
    survey_id,
    survey_tag,
    source,
    institution_id,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        ag.is_verified,
        ag.institution_id, 
        yearmonth)data
union 
SELECT format('A%s_%s_%s_%s_%s', survey_id,survey_tag,source,institution_id,yearmonth) as id,
    survey_id,
    survey_tag,
    source,
    institution_id,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        ag.is_verified,
        stu.institution_id,
        yearmonth)data
;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_agg AS
SELECT format('A%s_%s_%s_%s_%s', survey_id,survey_tag,source,boundary_id,yearmonth) as id,
    survey_id,
    survey_tag,
    source,
    boundary_id,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        ag.is_verified,
        b.id,
        yearmonth)data
union
SELECT format('A%s_%s_%s_%s_%s', survey_id,survey_tag,source,boundary_id,yearmonth) as id,
    survey_id,
    survey_tag,
    source,
    boundary_id,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        ag.is_verified,
        b.id,
        yearmonth)data
;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_electionboundary_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_electionboundary_agg AS
SELECT format('A%s_%s_%s_%s_%s', survey_id,survey_tag,source,electionboundary_id,yearmonth) as id,
    survey_id,
    survey_tag,
    source,
    electionboundary_id,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        ag.is_verified,
        eb.id,
        yearmonth)data
union
SELECT format('A%s_%s_%s_%s_%s', survey_id,survey_tag,source,electionboundary_id,yearmonth) as id,
    survey_id,
    survey_tag,
    source,
    electionboundary_id,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        ag.is_verified,
        eb.id,
        yearmonth)data
;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_respondenttype_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_respondenttype_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,respondent_type,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    respondent_type,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.source_id,
        ag.is_verified,
        rt.name,
        b.id,
        yearmonth)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,respondent_type,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    respondent_type,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
        and stu.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        ag.is_verified,
        rt.name,
        yearmonth)data
;



DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_respondenttype_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_respondenttype_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,respondent_type,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    respondent_type,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        ag.institution_id,
        qg.source_id,
        ag.is_verified,
        rt.name,
        yearmonth)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,respondent_type,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    respondent_type,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        stu.institution_id,
        qg.source_id,
        ag.is_verified,
        rt.name,
        yearmonth)data
;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_usertype_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_usertype_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,boundary_id,survey_tag,source,user_type,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    user_type,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        ag.is_verified,
	users.user_type_id,
        yearmonth)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,boundary_id,survey_tag,source,user_type,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    user_type,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
        and stu.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        ag.is_verified,
	users.user_type_id,
        yearmonth)data
;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_usertype_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_usertype_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,user_type,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    user_type,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        ag.institution_id,
        qg.source_id,
        ag.is_verified,
        ut.user_type_id,
        yearmonth)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,user_type,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    user_type,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        stu.institution_id,
        qg.source_id,
        ag.is_verified,
        ut.user_type_id,
        yearmonth)data
;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id, 
    source,
    yearmonth,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        q.key,
        yearmonth)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id, 
    source,
    yearmonth,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
        and ag.student_id = stu.id
        and stu.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        q.key,
        yearmonth)data
;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    yearmonth,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        ag.institution_id as institution_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        ag.institution_id,
        surveytag.tag_id,
        qg.source_id,
        q.key,
        yearmonth)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    yearmonth,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        stu.institution_id as institution_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
        and ag.student_id = stu.id
    GROUP BY survey.id,
        surveytag.tag_id,
        stu.institution_id,
        qg.source_id,
        q.key,
        yearmonth)data
;



DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questiongroup_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questiongroup_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,questiongroup_id,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        qg.name,qg.id,
        q.key,
        yearmonth)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,questiongroup_id,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        yearmonth)data
;

DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questiongroup_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questiongroup_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        ag.institution_id,
        qg.source_id,
        qg.name,qg.id,
        q.key,
        yearmonth)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
        and ag.student_id = stu.id
    GROUP BY survey.id,
        surveytag.tag_id,
        stu.institution_id,
        qg.source_id,
        qg.name,qg.id,
        q.key,
        yearmonth)data
;

DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questiongroup_gender_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questiongroup_gender_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,questiongroup_id,gender,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    gender,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
    group by ag.id,qg.survey_id,b.id,stmap.tag_id,yearmonth,source,qg.id, ans1.answer)data
GROUP BY survey_id, survey_tag,boundary_id,source,yearmonth,questiongroup_id,questiongroup_name,gender ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questiongroup_gender_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questiongroup_gender_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,gender,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    gender,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
    group by ag.id,qg.survey_id,stmap.tag_id,ag.institution_id,yearmonth,source,qg.id, ans1.answer)data
GROUP BY survey_id, survey_tag,institution_id,source,yearmonth,questiongroup_id,questiongroup_name,gender ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_class_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_class_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,sg_name,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    sg_name,
    yearmonth,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        sg.name as sg_name,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and stusg.academic_year_id = qg.academic_year_id
        and ag.is_verified=true
        and sg.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,sg.name,
        q.key,
        yearmonth)data
;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_class_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_class_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,sg_name,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    sg_name,
    yearmonth,
    question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        sg.institution_id as institution_id,
        qg.source_id as source,
        sg.name as sg_name,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and stusg.academic_year_id = qg.academic_year_id
        and q.is_featured = true
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        sg.institution_id,
        qg.source_id,sg.name,
        q.key,
        yearmonth)data
;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_class_gender_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_class_gender_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,sg_name,gender,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    yearmonth,
    sg_name,
    gender,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and stusg.academic_year_id = qg.academic_year_id
        and ag.is_verified=true
        and sg.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        sg.name,
        stu.gender_id,
        yearmonth)data
;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_class_gender_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_class_gender_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,sg_name,gender,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    yearmonth,
    sg_name,
    gender,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        sg.institution_id as institution_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and stusg.academic_year_id = qg.academic_year_id
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        sg.institution_id,
        qg.source_id,
        sg.name,
        stu.gender_id,
        yearmonth)data
;



DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_class_ans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_class_ans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,sg_name,question_id,answer_option,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    sg_name,
    question_id,
    answer_option,
    yearmonth,
    num_answers
FROM(SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and stusg.academic_year_id = qg.academic_year_id
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
        yearmonth)data
;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_class_ans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_class_ans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,sg_name,question_id,answer_option,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    sg_name,
    question_id,
    answer_option,
    yearmonth,
    num_answers
FROM(SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        sg.institution_id as institution_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and stusg.academic_year_id = stusg.academic_year_id
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        sg.institution_id,
        qg.source_id,
        sg.name,
        ans.question_id,
        ans.answer,
        yearmonth)data
;



DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    boundary_id,
    source,
    question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        b.id as boundary_id,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        assessments_questiongroupkey qgk,
        schools_student stu,
        schools_institution s,
        boundary_boundary b
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=qgk.questiongroup_id
        and ans.question_id=q.id
        and q.key=qgk.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.is_verified=true
        and ag.student_id = stu.id
        and stu.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
        GROUP BY q.key,ag.id,b.id,qgk.max_score,qg.survey_id,stmap.tag_id,yearmonth,source
        having sum(ans.answer::int)=qgk.max_score)correctanswers
GROUP BY survey_id,survey_tag,boundary_id,source,yearmonth,question_key
union
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    boundary_id,
    source,
    question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        b.id as boundary_id,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
    GROUP BY q.key,ag.id,b.id,max_score.maxscore,qg.survey_id,stmap.tag_id,yearmonth,source
    having sum(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id,survey_tag,boundary_id,source,yearmonth,question_key ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    institution_id,
    source,
    question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        stu.institution_id as institution_id,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        assessments_questiongroupkey qgk,
        schools_student stu
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=qgk.questiongroup_id
        and ans.question_id=q.id
        and q.key=qgk.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.is_verified=true
        and ag.student_id = stu.id
        GROUP BY q.key,ag.id,stu.institution_id,qgk.max_score,qg.survey_id,stmap.tag_id,yearmonth,source
        having sum(ans.answer::int)=qgk.max_score)correctanswers
GROUP BY survey_id,survey_tag,institution_id,source,yearmonth,question_key
union
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    institution_id,
    source,
    question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        ag.institution_id as institution_id,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
    GROUP BY q.key,ag.id,ag.institution_id,max_score.maxscore,qg.survey_id,stmap.tag_id,yearmonth,source
    having sum(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id,survey_tag,institution_id,source,yearmonth,question_key ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questiongroup_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questiongroup_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,questiongroup_id,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    question_key,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        assessments_questiongroupkey qgk,
        schools_student stu,
        schools_institution s,
        boundary_boundary b
    WHERE
    ans.answergroup_id=ag.id
    and ag.questiongroup_id=qg.id
    and qg.id=qgk.questiongroup_id
    and ans.question_id=q.id
    and q.key=qgk.key
    and q.is_featured=true
    and stmap.survey_id=qg.survey_id
    and qg.type_id='assessment'
    and ag.is_verified=true
    and ag.student_id = stu.id
    and stu.institution_id = s.id
    and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY q.key,ag.id,b.id,qgk.max_score,qg.survey_id,stmap.tag_id,yearmonth,source,qg.id,qg.name
    having sum(ans.answer::int)=qgk.max_score)correctanswers
GROUP BY survey_id,survey_tag,boundary_id,source,yearmonth,question_key,questiongroup_id,questiongroup_name
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,questiongroup_id,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    question_key,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
    GROUP BY q.key,ag.id,b.id,max_score.maxscore,qg.survey_id,stmap.tag_id,yearmonth,source,qg.id,qg.name
    having sum(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,boundary_id,source,yearmonth,question_key,questiongroup_id,questiongroup_name;



DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questiongroup_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questiongroup_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    question_key,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        assessments_questiongroupkey qgk,
        schools_student stu
    WHERE
    ans.answergroup_id=ag.id
    and ag.questiongroup_id=qg.id
    and qg.id=qgk.questiongroup_id
    and ans.question_id=q.id
    and q.key=qgk.key
    and q.is_featured=true
    and stmap.survey_id=qg.survey_id
    and qg.type_id='assessment'
    and ag.is_verified=true
    and ag.student_id = stu.id
    GROUP BY q.key,ag.id,stu.institution_id,qgk.max_score,qg.survey_id,stmap.tag_id,yearmonth,source,qg.id,qg.name
    having sum(ans.answer::int)=qgk.max_score)correctanswers
GROUP BY survey_id,survey_tag,institution_id,source,yearmonth,question_key,questiongroup_id,questiongroup_name
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    question_key,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
    GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,yearmonth,source,qg.id,qg.name,ag.institution_id
    having sum(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,institution_id,source,yearmonth,question_key,questiongroup_id,questiongroup_name;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_class_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_class_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,sg_name,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    sg_name,
    question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        b.id as boundary_id,
        sg.name as sg_name,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        schools_student stu,
        assessments_questiongroupkey qgk,
        schools_institution s,
        boundary_boundary b
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=qgk.questiongroup_id
        and ans.question_id=q.id
        and q.key=qgk.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.student_id = stu.id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and stusg.academic_year_id = qg.academic_year_id
        and ag.is_verified=true
        and sg.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY q.key,ag.id,qgk.max_score,qg.survey_id,stmap.tag_id,yearmonth,source,sg.name,b.id
    having sum(ans.answer::int)=qgk.max_score)correctanswers
GROUP BY survey_id, survey_tag,source,yearmonth,question_key,sg_name,boundary_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_class_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_class_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,sg_name,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    sg_name,
    question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        sg.institution_id as institution_id,
        sg.name as sg_name,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        schools_student stu,
        assessments_questiongroupkey qgk
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=qgk.questiongroup_id
        and ans.question_id=q.id
        and q.key=qgk.key
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.student_id = stu.id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and stusg.academic_year_id = qg.academic_year_id
        and ag.is_verified=true
    GROUP BY q.key,ag.id,qgk.max_score,qg.survey_id,stmap.tag_id,yearmonth,source,sg.name,sg.institution_id
    having sum(ans.answer::int)=qgk.max_score)correctanswers
GROUP BY survey_id, survey_tag,source,yearmonth,question_key,sg_name,institution_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questiongroup_ans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questiongroup_ans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,boundary_id,source,questiongroup_id,question_id,answer_option,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        yearmonth)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,boundary_id,source,questiongroup_id,question_id,answer_option,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        yearmonth)data
;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questiongroup_ans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questiongroup_ans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,institution_id,questiongroup_id,question_id,answer_option,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        yearmonth)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,institution_id,questiongroup_id,question_id,answer_option,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        yearmonth)data
;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questiongroup_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questiongroup_agg AS
SELECT format('A%s_%s_%s_%s', survey_id,boundary_id,questiongroup_id,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    questiongroup_id,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.id,
        ag.is_verified,
        b.id,
        yearmonth)data
union
SELECT format('A%s_%s_%s_%s', survey_id,boundary_id,questiongroup_id,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    questiongroup_id,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.id,
        ag.is_verified,
        b.id,
        yearmonth)data
;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questiongroup_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questiongroup_agg AS
SELECT format('A%s_%s_%s_%s', survey_id,institution_id,questiongroup_id,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    questiongroup_id,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.id,
        ag.is_verified,
        ag.institution_id, 
        yearmonth)data
union 
SELECT format('A%s_%s_%s_%s', survey_id,institution_id,questiongroup_id,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    questiongroup_id,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        qg.id,
        ag.is_verified,
        stu.institution_id,
        yearmonth)data
;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_tagmapping_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_tagmapping_agg AS
SELECT distinct format('A%s_%s_%s', instmap.tag_id, b.id, instmap.academic_year_id) as id,
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
    and sgmap.academic_year_id = instmap.academic_year_id  
    and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    and instmap.tag_id = 'gka'
    and instmap.academic_year_id = '1617'
    and instmap.tag_id = sgmap.tag_id
    and stusg.academic_year_id = instmap.academic_year_id
    and sg.name = sgmap.sg_name
    and stusg.status_id !='DL' and stusg.student_id=stu.id 
    and stu.status_id !='DL'
GROUP BY
    instmap.tag_id,
    b.id,
    instmap.academic_year_id
union
SELECT distinct format('A%s_%s_%s', data.survey_tag, data.boundary_id, data.academic_year_id) as id,
    data.survey_tag as survey_tag,
    data.boundary_id as boundary_id, 
    data.academic_year_id as academic_year_id,
    count(distinct school_id) as num_schools,
    count(distinct student_id) as num_students
FROM
(
 SELECT distinct 
    instmap.tag_id  as  survey_tag,
    b.id as boundary_id, 
    '1718' as academic_year_id,
    instmap.institution_id as school_id,
    stu.id as student_id
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
    and sgmap.academic_year_id = instmap.academic_year_id  
    and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    and instmap.tag_id = 'gka'
    and instmap.academic_year_id = '1617'
    and instmap.tag_id = sgmap.tag_id
    and stusg.academic_year_id = instmap.academic_year_id
    and sg.name = sgmap.sg_name
    and stusg.status_id !='DL' and stusg.student_id=stu.id 
    and stu.status_id !='DL'
union
SELECT distinct
    instmap.tag_id as  survey_tag,
    b.id as boundary_id, 
    instmap.academic_year_id as academic_year_id,
    instmap.institution_id as school_id,
    stu.id as student_id 
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
    and sgmap.academic_year_id = instmap.academic_year_id  
    and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    and instmap.tag_id = 'gka'
    and instmap.academic_year_id = '1718'
    and instmap.tag_id = sgmap.tag_id
    and stusg.academic_year_id = instmap.academic_year_id
    and sg.name = sgmap.sg_name
    and stusg.status_id !='DL' and stusg.student_id=stu.id 
    and stu.status_id !='DL'
)data
GROUP BY
data.survey_tag,
data.boundary_id,
data.academic_year_id
union
SELECT distinct format('A%s_%s_%s', data.survey_tag, data.boundary_id, data.academic_year_id) as id,
    data.survey_tag as survey_tag,
    data.boundary_id as boundary_id, 
    data.academic_year_id as academic_year_id,
    count(distinct school_id) as num_schools,
    count(distinct student_id) as num_students
FROM
(
 SELECT distinct 
    instmap.tag_id  as  survey_tag,
    b.id as boundary_id, 
    '1819' as academic_year_id,
    instmap.institution_id as school_id,
    stu.id as student_id
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
    and sgmap.academic_year_id = instmap.academic_year_id  
    and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    and instmap.tag_id = 'gka'
    and instmap.academic_year_id = '1617'
    and instmap.tag_id = sgmap.tag_id
    and stusg.academic_year_id = instmap.academic_year_id
    and sg.name = sgmap.sg_name
    and stusg.status_id !='DL' and stusg.student_id=stu.id 
    and stu.status_id !='DL'
union
SELECT distinct
    instmap.tag_id as  survey_tag,
    b.id as boundary_id, 
    '1819' as academic_year_id,
    instmap.institution_id as school_id,
    stu.id as student_id 
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
    and sgmap.academic_year_id = instmap.academic_year_id  
    and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    and instmap.tag_id = 'gka'
    and instmap.academic_year_id = '1718'
    and instmap.tag_id = sgmap.tag_id
    and stusg.academic_year_id = instmap.academic_year_id
    and sg.name = sgmap.sg_name
    and stusg.status_id !='DL' and stusg.student_id=stu.id 
    and stu.status_id !='DL'
union
SELECT distinct
    instmap.tag_id as  survey_tag,
    b.id as boundary_id, 
    '1819' as academic_year_id,
    instmap.institution_id as school_id,
    stu.id as student_id 
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
    and sgmap.academic_year_id = instmap.academic_year_id  
    and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    and instmap.tag_id = 'gka'
    and instmap.academic_year_id = '1819'
    and instmap.tag_id = sgmap.tag_id
    and stusg.academic_year_id = instmap.academic_year_id
    and sg.name = sgmap.sg_name
    and stusg.status_id !='DL' and stusg.student_id=stu.id 
    and stu.status_id !='DL'
)data
GROUP BY
data.survey_tag,
data.boundary_id,
data.academic_year_id

;

DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questiongroup_gender_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questiongroup_gender_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,questiongroup_id,gender,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    gender,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        b.id as boundary_id,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        ans1.answer as gender,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag inner join assessments_answerinstitution ans1 on (ag.id=ans1.answergroup_id and ans1.question_id=291),
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        (SELECT distinct
            qg.id as qgid,
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
            qg.id)max_score,
        schools_institution s,
        boundary_boundary b
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.survey_id=2
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY ag.id,b.id,max_score.maxscore,qg.survey_id,stmap.tag_id,yearmonth,source,qg.id, ans1.answer,qg.name
    having sum(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,boundary_id,source,yearmonth,questiongroup_id,questiongroup_name,gender ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questiongroup_gender_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questiongroup_gender_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,gender,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    gender,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        ag.institution_id as institution_id,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        ans1.answer as gender,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag inner join assessments_answerinstitution ans1 on (ag.id=ans1.answergroup_id and ans1.question_id=291),
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        (SELECT distinct
            qg.id as qgid,
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
            qg.id)max_score
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=max_score.qgid
        and ans.question_id=q.id
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.survey_id=2
        and ag.is_verified=true
    GROUP BY ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,yearmonth,source,qg.id, ans1.answer,qg.name,ag.institution_id
    having sum(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,source,yearmonth,questiongroup_id,questiongroup_name,gender,institution_id ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_class_gender_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_class_gender_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,sg_name,gender,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    sg_name,
    gender,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        b.id as boundary_id,
        sg.name as sg_name,
        stu.gender_id as gender,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        schools_student stu,
        assessments_questiongroupkey qgk,
        schools_institution s,
        boundary_boundary b
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=qgk.questiongroup_id
        and ans.question_id=q.id
        and q.is_featured=true
        and q.key=qgk.key
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.student_id = stu.id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and stusg.academic_year_id = qg.academic_year_id
        and ag.is_verified=true
        and sg.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY ag.id,qgk.max_score,qg.survey_id,stmap.tag_id,yearmonth,source,sg.name,stu.gender_id,b.id
    having sum(ans.answer::int)=qgk.max_score)correctanswers
GROUP BY survey_id, survey_tag,source,yearmonth,sg_name,gender,boundary_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_class_gender_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_class_gender_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,sg_name,gender,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    sg_name,
    gender,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        sg.institution_id as institution_id,
        sg.name as sg_name,
        stu.gender_id as gender,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        schools_studentstudentgrouprelation stusg,
        schools_studentgroup sg,
        schools_student stu,
        assessments_questiongroupkey qgk
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=qgk.questiongroup_id
        and ans.question_id=q.id
        and q.is_featured=true
        and q.key=qgk.key
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.student_id = stu.id
        and stu.id = stusg.student_id
        and stusg.student_group_id = sg.id
        and stusg.academic_year_id = qg.academic_year_id
        and ag.is_verified=true
    GROUP BY ag.id,qgk.max_score,qg.survey_id,stmap.tag_id,yearmonth,source,sg.name,stu.gender_id,sg.institution_id
    having sum(ans.answer::int)=qgk.max_score)correctanswers
GROUP BY survey_id, survey_tag,source,yearmonth,sg_name,gender,institution_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_electiontype_count CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_electiontype_count AS
SELECT format('A%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,yearmonth,const_ward_type) as id,
    survey_id,
    survey_tag,
    boundary_id,
    yearmonth,
    const_ward_type,
    electionboundary_count
FROM(
    SELECT distinct 
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        eb.const_ward_type_id as const_ward_type,
	count(distinct eb.id) as electionboundary_count
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        schools_institution s,
        boundary_electionboundary eb,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (1, 2, 4, 5, 6, 7, 11)
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
        and (s.mp_id = eb.id or s.mla_id = eb.id or s.ward_id = eb.id or s.gp_id = eb.id) 
        and ag.is_verified=true
    GROUP BY
        survey.id, surveytag.tag_id, b.id, yearmonth, eb.const_ward_type_id
        )data
union
SELECT format('A%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,yearmonth,const_ward_type) as id,
    survey_id,
    survey_tag,
    boundary_id,
    yearmonth,
    const_ward_type,
    electionboundary_count
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        eb.const_ward_type_id as const_ward_type,
	count(distinct eb.id) as electionboundary_count
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_student ag,
        assessments_surveytagmapping surveytag,
        schools_student stu,
        schools_institution s,
        boundary_electionboundary eb,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and survey.id in (3)
        and ag.student_id = stu.id
        and stu.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
        and (s.mp_id = eb.id or s.mla_id = eb.id or s.ward_id = eb.id or s.gp_id = eb.id) 
        and ag.is_verified=true
    GROUP BY survey.id, surveytag.tag_id, b.id, yearmonth, eb.const_ward_type_id)data
;
