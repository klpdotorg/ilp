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
    year_month
union
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
union 
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
    qg.inst_type_id
union 
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
union 
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
union 
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
    count(distinct ag.institution_id) as num_schools,
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
union
SELECT format('A%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,b.id) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    b.id as boundary_id,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    count(ag) as num_assessments,
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
    count(distinct ag.institution_id) as num_schools,
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
union 
SELECT format('A%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,eb.id) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    eb.id as electionboundary_id,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    count(ag) as num_assessments,
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
    year_month,
    qg.source_id,
    ag.is_verified,
    eb.id;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_respondenttype_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_respondenttype_agg AS
SELECT format('A%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,rt.name) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    rt.name as respondent_type,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    count(ag) as num_assessments,
    count(distinct ag.institution_id) as num_schools,
    case survey.id when 2 then count(ag) else 0 end as num_children,
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
    year_month,
    ag.is_verified,
    rt.name
union 
SELECT format('A%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,rt.name) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    rt.name as respondent_type,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    count(ag) as num_assessments,
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
    year_month,
    qg.source_id,
    ag.is_verified,
    rt.name;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_usertype_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_usertype_agg AS
SELECT format('A%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,ut.user_type) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    ut.user_type as user_type,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    count(ag) as num_assessments,
    count(distinct ag.institution_id) as num_schools,
    case survey.id when 2 then count(ag) else 0 end as num_children,
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
    year_month,
    ag.is_verified,
    ut.user_type
union 
SELECT format('A%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,ut.user_type) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    ut.user_type as user_type,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    count(ag) as num_assessments,
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
    year_month,
    qg.source_id,
    ag.is_verified,
    ut.user_type;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_ans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_ans_agg AS
SELECT format('A%s_%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,ans.question_id,ans.answer) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
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
    year_month,
    ans.question_id,
    ans.answer
union 
SELECT format('A%s_%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,ans.question_id,ans.answer) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
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
    year_month,
    qg.source_id,
    ans.question_id,
    ans.answer;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_questionkey_agg AS
SELECT format('A%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,q.key) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    q.key as question_key,
    count(ag) as num_assessments,
    count(ag) as num_correct_assessments
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
    year_month,
    q.key
union 
SELECT format('A%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,q.key) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    q.key as question_key,
    count(ag) as num_assessments,
    count(ag) as num_correct_assessments
FROM assessments_survey survey,
    assessments_questiongroup as qg,
    assessments_answergroup_student as ag,
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
    year_month,
    qg.source_id,
    q.key;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_class_gender_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_class_gender_agg AS
SELECT format('A%s_%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,sg.name,stu.gender_id) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
    sg.name as sg_name,
    stu.gender_id as gender,
    count(ag) as num_assessments,
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
    year_month,
    qg.source_id,
    sg.name,
    stu.gender_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_class_ans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_class_ans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey.id,surveytag.tag_id,qg.source_id,sg.name,ans.question_id,ans.answer) as id,
    survey.id as survey_id,
    surveytag.tag_id as survey_tag,
    qg.source_id as source,
    to_char(ag.date_of_visit,'YYYY-MM') as year_month,
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
    year_month,
    qg.source_id,
    sg.name,
    ans.question_id,
    ans.answer;


