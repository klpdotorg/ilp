DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questiongroup_qdetails_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questiongroup_qdetails_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,question_id,concept,microconcept_group,microconcept,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    yearmonth,
    question_id,
    concept,
    microconcept_group,
    microconcept,
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
        q.id as question_id,
        q.concept_id as concept,
        q.microconcept_group_id as microconcept_group,
        q.microconcept_id as microconcept,
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
        and survey.id in (2,18)
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and q.is_featured = true
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        ag.institution_id,
        qg.source_id,
        qg.name,qg.id,
        q.id,
        q.concept_id,q.microconcept_group_id,q.microconcept_id,
        yearmonth)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,question_id,concept,microconcept_group,microconcept,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    yearmonth,
    question_id,
    concept,
    microconcept_group,
    microconcept,
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
        q.id as question_id,
        q.concept_id as concept,
        q.microconcept_group_id as microconcept_group,
        q.microconcept_id as microconcept,
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
        qg.name,qg.id,q.id,
        q.concept_id,q.microconcept_group_id,q.microconcept_id,
        yearmonth)data
;

DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questiongroup_qdetails_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questiongroup_qdetails_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,question_id,concept,microconcept_group,microconcept,yearmonth) as id,
    survey_id, 
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    question_id,
    concept,
    microconcept_group,
    microconcept,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        ag.institution_id as institution_id,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        q.id as question_id,
        q.concept_id as concept,
        q.microconcept_group_id as microconcept_group,
        q.microconcept_id as microconcept,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag,
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
	assessments_competencyquestionmap qgc
        --assessments_questiongroupconcept qgc --table for storing pass score
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.survey_id in (2,18)
        and qg.id=qgc.questiongroup_id
        and ans.question_id=q.id
	    and q.id=qgc.question_id
        and stmap.survey_id=qg.survey_id
        and ag.is_verified=true
    GROUP BY q.concept_id,q.microconcept_group_id,q.microconcept_id,q.id,ag.id,qgc.max_score,qg.survey_id,stmap.tag_id,yearmonth,source,qg.id,qg.name,ag.institution_id
    having sum(case ans.answer when 'Yes'then 1 when 'No' then 0 when '1' then 1 when '0' then 0 end)>=qgc.max_score)correctanswers --correct ans logic
GROUP BY survey_id, survey_tag,institution_id,source,yearmonth,concept,microconcept_group,microconcept,question_id,questiongroup_id,questiongroup_name;

DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id, 
    source,
    yearmonth,
    question_key,
    lang_question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        b.id as boundary_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        qmap.key as question_key,
	qmap.lang_key as lang_question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_competencyquestionmap qmap,
        assessments_question q,
        schools_institution s,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and qg.id = qmap. questiongroup_id
        and q.id = qmap.question_id
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
        qmap.key,
	qmap.lang_key,
        yearmonth)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id, 
    source,
    yearmonth,
    question_key,
    '' as lang_question_key,
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
    lang_question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        ag.institution_id as institution_id,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        qmap.key as question_key,
	qmap.lang_key as lang_question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_competencyquestionmap qmap,
        assessments_question q
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and qmap.questiongroup_id = qg.id
        and qmap.question_id = q.id
        and q.is_featured = true
        and ag.is_verified=true
    GROUP BY survey.id,
        ag.institution_id,
        surveytag.tag_id,
        qg.source_id,
        qmap.key,
	qmap.lang_key,
        yearmonth)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    yearmonth,
    question_key,
    '' as lang_question_key,
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
    lang_question_key,
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
        qmap.key as question_key,
	qmap.lang_key as lang_question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q,
        schools_institution s,
        assessments_competencyquestionmap qmap,
        boundary_boundary b
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and qmap.questiongroup_id = qg.id
        and qmap.question_id = q.id
        and q.is_featured = true
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        b.id,
        qg.source_id,
        qg.name,qg.id,
        qmap.key,
	qmap.lang_key,
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
    '' as lang_question_key,
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

DROP MATERIALIZED VIEW IF EXISTS mvw_survey_eboundary_questiongroup_questionkey_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_eboundary_questiongroup_questionkey_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,eboundary_id,source,questiongroup_id,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    eboundary_id,
    const_ward_type_id,
    source,
    questiongroup_id,
    questiongroup_name,
    yearmonth,
    question_key,
    lang_question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        eb.id as eboundary_id,
        eb.const_ward_type_id as const_ward_type_id,
        qg.source_id as source,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        qmap.key as question_key,
	qmap.lang_key as lang_question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_question q,
        schools_institution s,
        assessments_competencyquestionmap qmap,
        boundary_electionboundary eb
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and qmap.questiongroup_id = qg.id
        and qmap.question_id = q.id
        and q.is_featured = true
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.mp_id = eb.id or s.mla_id = eb.id or s.gp_id = eb.id or s.ward_id = eb.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        eb.id,
        qg.source_id,
        qg.name,qg.id,
        eb.const_ward_type_id,
        qmap.key,
	qmap.lang_key,
        yearmonth)data
union 
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,eboundary_id,source,questiongroup_id,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    eboundary_id,
    const_ward_type_id,
    source,
    questiongroup_id,
    questiongroup_name,
    yearmonth,
    question_key,
    '' as lang_question_key,
    num_assessments
FROM(
    SELECT
        survey.id as survey_id,
        surveytag.tag_id as survey_tag,
        eb.id as eboundary_id,
        eb.const_ward_type_id as const_ward_type_id,
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
        boundary_electionboundary eb,
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
        and (s.mp_id = eb.id or s.mla_id = eb.id or s.gp_id = eb.id or s.ward_id = eb.id) 
    GROUP BY survey.id,
        surveytag.tag_id,
        eb.id,
        eb.const_ward_type_id,
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
    lang_question_key,
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
        qmap.key as question_key,
	qmap.lang_key as lang_question_key,
        count(distinct ag.id) as num_assessments
    FROM assessments_survey survey,
        assessments_questiongroup qg,
        assessments_answergroup_institution ag,
        assessments_surveytagmapping surveytag,
        assessments_answerinstitution ans,
        assessments_competencyquestionmap qmap,
        assessments_question q
    WHERE 
        survey.id = qg.survey_id
        and qg.id = ag.questiongroup_id
        and survey.id = surveytag.survey_id
        and ag.id = ans.answergroup_id
        and ans.question_id = q.id
        and qmap.questiongroup_id = qg.id
        and qmap.question_id = q.id
        and q.is_featured = true
        and ag.is_verified=true
    GROUP BY survey.id,
        surveytag.tag_id,
        ag.institution_id,
        qg.source_id,
        qg.name,qg.id,
        qmap.key,
	qmap.lang_key,
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
    '' as lang_question_key,
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

DROP MATERIALIZED VIEW IF EXISTS mvw_survey_eboundary_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_eboundary_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,eboundary_id,source,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    eboundary_id,
    source,
    question_key,
    '' as lang_question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        eb.id as eboundary_id,
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        assessments_questiongroupkey qgk, --table for storing max score
        schools_student stu,
        schools_institution s,
        boundary_electionboundary eb
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
        and (s.mp_id = eb.id or s.mla_id = eb.id or s.ward_id = eb.id or s.gp_id = eb.id) 
        GROUP BY q.key,ag.id,eb.id,qgk.max_score,qg.survey_id,stmap.tag_id,yearmonth,source
        having sum(ans.answer::int)>=qgk.max_score)correctanswers --condition for correct answer
GROUP BY survey_id,survey_tag,eboundary_id,source,yearmonth,question_key,lang_question_key
union
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,eboundary_id,source,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    eboundary_id,
    source,
    question_key,
    lang_question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        eb.id as eboundary_id,
        qmap.key as question_key,
	qmap.lang_key as lang_question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag,
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        assessments_competencyquestionmap qmap, --table for storing max score
        schools_institution s,
        boundary_electionboundary eb
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=qmap.questiongroup_id
        and ans.question_id=q.id
        and q.id = qmap.question_id
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.mp_id = eb.id or s.mla_id = eb.id or s.ward_id = eb.id or s.gp_id = eb.id) 
    GROUP BY qmap.key,qmap.lang_key,ag.id,eb.id,qmap.max_score,qg.survey_id,stmap.tag_id,yearmonth,source
    having sum(case ans.answer when 'Yes'then 1 when 'No' then 0 when '1' then 1 when '0' then 0 end)>=sum(qmap.max_score))correctanswers --correct ans logic
GROUP BY survey_id,survey_tag,eboundary_id,source,yearmonth,question_key,lang_question_key ;

DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    boundary_id,
    source,
    question_key,
    '' as lang_question_key,
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
        assessments_questiongroupkey qgk, --table for storing max score
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
        having sum(ans.answer::int)>=qgk.max_score)correctanswers --correct ans logic
GROUP BY survey_id,survey_tag,boundary_id,source,yearmonth,question_key,lang_question_key
union
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    boundary_id,
    source,
    question_key,
    lang_question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        b.id as boundary_id,
        qmap.key as question_key,
	qmap.lang_key as lang_question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag,
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        assessments_competencyquestionmap qmap, --table for scoring max score
        schools_institution s,
        boundary_boundary b
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=qmap.questiongroup_id
        and ans.question_id=q.id
        and q.id = qmap.question_id
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY qmap.key,qmap.lang_key,ag.id,b.id,qmap.max_score,qg.survey_id,stmap.tag_id,yearmonth,source
    having sum(case ans.answer when 'Yes'then 1 when 'No' then 0 when '1' then 1 when '0' then 0 end)>=sum(qmap.max_score))correctanswers --correct ans logic
GROUP BY survey_id,survey_tag,boundary_id,source,yearmonth,question_key,lang_question_key ;

DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    institution_id,
    source,
    question_key,
    '' as lang_question_key,
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
        assessments_questiongroupkey qgk, --table for storing max score
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
        having sum(ans.answer::int)>=qgk.max_score)correctanswers --correct ans logic
GROUP BY survey_id,survey_tag,institution_id,source,yearmonth,question_key,lang_question_key
union
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    institution_id,
    source,
    question_key,
    lang_question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        ag.institution_id as institution_id,
        qmap.key as question_key,
	qmap.lang_key as lang_question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag,
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        assessments_competencyquestionmap qmap --table for storing max score
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=qmap.questiongroup_id
        and ans.question_id=q.id
        and q.id = qmap.question_id
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.is_verified=true
    GROUP BY qmap.key,qmap.lang_key,ag.id,ag.institution_id,qmap.max_score,qg.survey_id,stmap.tag_id,yearmonth,source
    having sum(case ans.answer when 'Yes'then 1 when 'No' then 0 when '1' then 1 when '0' then 0 end)=sum(qmap.max_score))correctanswers --correct ans logic
GROUP BY survey_id,survey_tag,institution_id,source,yearmonth,question_key,lang_question_key ;

DROP MATERIALIZED VIEW IF EXISTS mvw_survey_eboundary_questiongroup_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_eboundary_questiongroup_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,eboundary_id,source,questiongroup_id,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    eboundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    question_key,
    '' as lang_question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        eb.id as eboundary_id,
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
        assessments_questiongroupkey qgk, --table for max score
        schools_student stu,
        schools_institution s,
        boundary_electionboundary eb
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
    and (s.mp_id = eb.id or s.mla_id = eb.id or s.ward_id = eb.id or s.gp_id = eb.id) 
    GROUP BY q.key,ag.id,eb.id,qgk.max_score,qg.survey_id,stmap.tag_id,yearmonth,source,qg.id,qg.name
    having sum(ans.answer::int)>=qgk.max_score)correctanswers --correct ans logic
GROUP BY survey_id,survey_tag,eboundary_id,source,yearmonth,question_key,lang_question_key,questiongroup_id,questiongroup_name
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,eboundary_id,source,questiongroup_id,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    eboundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    question_key,
    lang_question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        eb.id as eboundary_id,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        qmap.key as question_key,
	qmap.lang_key as lang_question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag,
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        assessments_competencyquestionmap qmap, --table for max score
        schools_institution s,
        boundary_electionboundary eb
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=qmap.questiongroup_id
        and ans.question_id=q.id
        and q.id = qmap.question_id
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.mp_id = eb.id or s.mla_id = eb.id or s.ward_id = eb.id or s.gp_id = eb.id) 
    GROUP BY qmap.key,qmap.lang_key,ag.id,eb.id,qmap.max_score,qg.survey_id,stmap.tag_id,yearmonth,source,qg.id,qg.name
    having sum(case ans.answer when 'Yes'then 1 when 'No' then 0 when '1' then 1 when '0' then 0 end)>=sum(qmap.max_score))correctanswers -- correct ans logic
GROUP BY survey_id, survey_tag,eboundary_id,source,yearmonth,question_key,lang_question_key,questiongroup_id,questiongroup_name;

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
    '' as lang_question_key,
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
        assessments_questiongroupkey qgk, --table for max score
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
    having sum(ans.answer::int)>=qgk.max_score)correctanswers --correct ans logic
GROUP BY survey_id,survey_tag,boundary_id,source,yearmonth,question_key,lang_question_key,questiongroup_id,questiongroup_name
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,questiongroup_id,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    question_key,
    lang_question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        b.id as boundary_id,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        qmap.key as question_key,
	qmap.lang_key as lang_question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag,
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        assessments_competencyquestionmap qmap, --table for max score
        schools_institution s,
        boundary_boundary b
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=qmap.questiongroup_id
        and ans.question_id=q.id
        and q.id = qmap.question_id
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY qmap.key,qmap.lang_key,ag.id,b.id,qmap.max_score,qg.survey_id,stmap.tag_id,yearmonth,source,qg.id,qg.name
    having sum(case ans.answer when 'Yes'then 1 when 'No' then 0 when '1' then 1 when '0' then 0 end)>=sum(qmap.max_score))correctanswers --correct ans logic
GROUP BY survey_id, survey_tag,boundary_id,source,yearmonth,question_key,lang_question_key,questiongroup_id,questiongroup_name;

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
    '' as lang_question_key,
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
        assessments_questiongroupkey qgk, --table for storing max score
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
    having sum(ans.answer::int)>=qgk.max_score)correctanswers --correct ans logic
GROUP BY survey_id,survey_tag,institution_id,source,yearmonth,question_key,lang_question_key,questiongroup_id,questiongroup_name
union
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    question_key,
    lang_question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        ag.institution_id as institution_id,
        qg.id as questiongroup_id,
        qg.name as questiongroup_name,
        qmap.key as question_key,
	qmap.lang_key as lang_question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag,
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
        assessments_competencyquestionmap qmap --table for storing max score
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.id=qmap.questiongroup_id
        and ans.question_id=q.id
        and q.id = qmap.question_id
        and q.is_featured=true
        and stmap.survey_id=qg.survey_id
        and qg.type_id='assessment'
        and ag.is_verified=true
    GROUP BY qmap.key,qmap.lang_key,ag.id,qmap.max_score,qg.survey_id,stmap.tag_id,yearmonth,source,qg.id,qg.name,ag.institution_id
    having sum(case ans.answer when 'Yes'then 1 when 'No' then 0 when '1' then 1 when '0' then 0 end)>=sum(qmap.max_score))correctanswers --correct ans logic
GROUP BY survey_id, survey_tag,institution_id,source,yearmonth,question_key,lang_question_key,questiongroup_id,questiongroup_name;

DROP MATERIALIZED VIEW IF EXISTS mvw_survey_eboundary_qdetails_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_eboundary_qdetails_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,eboundary_id,source,concept,microconcept_group,microconcept,yearmonth) as id,
    survey_id, 
    survey_tag,
    eboundary_id,
    source,
    concept,
    microconcept_group,
    microconcept,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        eb.id as eboundary_id,
        q.id as question_id,
        q.concept_id as concept,
        q.microconcept_group_id as microconcept_group,
        q.microconcept_id as microconcept,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_institution ag,
        assessments_answerinstitution ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
	    assessments_competencyquestionmap qgc,
        --assessments_questiongroupconcept qgc, --table that stores passscore
        schools_institution s,
        boundary_electionboundary eb
    WHERE
        ans.answergroup_id=ag.id
        and ag.questiongroup_id=qg.id
        and qg.survey_id in (2,18)
        and qg.id=qgc.questiongroup_id
        and ans.question_id=q.id
	and q.id = qgc.question_id
        and stmap.survey_id=qg.survey_id
        and ag.is_verified=true
        and ag.institution_id = s.id
        and (s.gp_id = eb.id or s.ward_id = eb.id or s.mla_id = eb.id or s.mp_id = eb.id) 
    GROUP BY q.concept_id,q.id,q.microconcept_id,q.microconcept_group_id,ag.id,eb.id,qgc.max_score,qg.survey_id,stmap.tag_id,yearmonth,source
    having sum(case ans.answer when 'Yes'then 1 when 'No' then 0 when '1' then 1 when '0' then 0 end)>=qgc.max_score)correctanswers --correct ans check
GROUP BY survey_id,survey_tag,eboundary_id,source,yearmonth,concept,microconcept_group,microconcept;


