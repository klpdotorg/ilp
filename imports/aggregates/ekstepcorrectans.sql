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


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s', survey_id,survey_tag,source,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    source,
    question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        q.key as question_key,
        qg.source_id as source,
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
        ag.id as ag_id
    FROM assessments_answergroup_student ag,
        assessments_answerstudent ans,
        assessments_surveytagmapping stmap,
        assessments_questiongroup qg,
        assessments_question q,
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
        and ag.is_verified=true
        GROUP BY q.key,ag.id,qgk.max_score,qg.survey_id,stmap.tag_id,yearmonth,source
        having sum(ans.answer::int)=qgk.max_score)correctanswers
GROUP BY survey_id,survey_tag,source,yearmonth,question_key
union
SELECT format('A%s_%s_%s_%s_%s', survey_id,survey_tag,source,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
    source,
    question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
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
    GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,yearmonth,source
    having sum(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id,survey_tag,source,yearmonth,question_key ;


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


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_questiongroup_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_questiongroup_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag ,source,questiongroup_id,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
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
    and ag.is_verified=true
    GROUP BY q.key,ag.id,qgk.max_score,qg.survey_id,stmap.tag_id,yearmonth,source,qg.id,qg.name
    having sum(ans.answer::int)=qgk.max_score)correctanswers
GROUP BY survey_id,survey_tag,source,yearmonth,question_key,questiongroup_id,questiongroup_name
union
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag ,source,questiongroup_id,question_key,yearmonth) as id,
    survey_id, 
    survey_tag,
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
    GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,yearmonth,source,qg.id,qg.name
    having sum(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,source,yearmonth,question_key,questiongroup_id,questiongroup_name;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_questiongroup_questionkey_gender_correctans CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_questiongroup_questionkey_gender_correctans AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,questiongroup_id,gender,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    questiongroup_id,
    questiongroup_name,
    gender,
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
        ans1.answer as gender,
        q.key as question_key,
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
    GROUP BY q.key,ag.id,b.id,max_score.maxscore,qg.survey_id,stmap.tag_id,yearmonth,source,qg.id, ans1.answer,qg.name
    having sum(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,boundary_id,source,yearmonth,question_key,questiongroup_id,questiongroup_name,gender ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_questiongroup_questionkey_gender_correct CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_questiongroup_questionkey_gender_correct AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,questiongroup_id,gender,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    questiongroup_id,
    questiongroup_name,
    gender,
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
        ans1.answer as gender,
        q.key as question_key,
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
    GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,yearmonth,source,qg.id, ans1.answer,qg.name,ag.institution_id
    having sum(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,source,yearmonth,question_key,questiongroup_id,questiongroup_name,gender,institution_id ;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_questiongroup_gender_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_questiongroup_gender_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,questiongroup_id,gender,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    source,
    questiongroup_id,
    questiongroup_name,
    gender,
    question_key,
    yearmonth,
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
        to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
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
    GROUP BY q.key,ag.id,max_score.maxscore,qg.survey_id,stmap.tag_id,yearmonth,source,qg.id, ans1.answer,qg.name
    having sum(case ans.answer when 'Yes'then 1 else 0 end)=max_score.maxscore)correctanswers
GROUP BY survey_id, survey_tag,source,yearmonth,question_key,questiongroup_id,questiongroup_name,gender ;


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
        and ag.is_verified=true
    GROUP BY q.key,ag.id,qgk.max_score,qg.survey_id,stmap.tag_id,yearmonth,source,sg.name,sg.institution_id
    having sum(ans.answer::int)=qgk.max_score)correctanswers
GROUP BY survey_id, survey_tag,source,yearmonth,question_key,sg_name,institution_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_class_questionkey_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_class_questionkey_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,sg_name,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    source,
    sg_name,
    question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
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
        and ag.is_verified=true
    GROUP BY q.key,ag.id,qgk.max_score,qg.survey_id,stmap.tag_id,yearmonth,source,sg.name
    having sum(ans.answer::int)=qgk.max_score)correctanswers
GROUP BY survey_id, survey_tag,source,yearmonth,question_key,sg_name;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_boundary_class_questionkey_gender_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_boundary_class_questionkey_gender_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,boundary_id,source,sg_name,gender,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    boundary_id,
    source,
    sg_name,
    gender,
    question_key,
    yearmonth,
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
        and ag.is_verified=true
        and sg.institution_id = s.id
        and (s.admin0_id = b.id or s.admin1_id = b.id or s.admin2_id = b.id or s.admin3_id = b.id) 
    GROUP BY q.key,ag.id,qgk.max_score,qg.survey_id,stmap.tag_id,yearmonth,source,sg.name,stu.gender_id,b.id
    having sum(ans.answer::int)=qgk.max_score)correctanswers
GROUP BY survey_id, survey_tag,source,yearmonth,question_key,sg_name,gender,boundary_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_institution_class_questionkey_gender_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_institution_class_questionkey_gender_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,institution_id,source,sg_name,gender,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    institution_id,
    source,
    sg_name,
    gender,
    question_key,
    yearmonth,
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
        and ag.is_verified=true
    GROUP BY q.key,ag.id,qgk.max_score,qg.survey_id,stmap.tag_id,yearmonth,source,sg.name,stu.gender_id,sg.institution_id
    having sum(ans.answer::int)=qgk.max_score)correctanswers
GROUP BY survey_id, survey_tag,source,yearmonth,question_key,sg_name,gender,institution_id;


DROP MATERIALIZED VIEW IF EXISTS mvw_survey_class_gender_correctans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_survey_class_gender_correctans_agg AS
SELECT format('A%s_%s_%s_%s_%s_%s_%s', survey_id,survey_tag,source,sg_name,gender,question_key,yearmonth) as id,
    survey_id,
    survey_tag,
    source,
    sg_name,
    gender,
    question_key,
    yearmonth,
    count(ag_id) as num_assessments
FROM
    (SELECT distinct
        qg.survey_id as survey_id, 
        stmap.tag_id as survey_tag, 
        sg.name as sg_name,
        stu.gender_id as gender,
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
        and ag.is_verified=true
    GROUP BY q.key,ag.id,qgk.max_score,qg.survey_id,stmap.tag_id,yearmonth,source,sg.name,stu.gender_id
    having sum(ans.answer::int)=qgk.max_score)correctanswers
GROUP BY survey_id, survey_tag,source,yearmonth,question_key,sg_name,gender;
