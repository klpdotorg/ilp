--Number of pdfs
SELECT DISTINCT
    institution_id,
    count(DISTINCT to_char(date_of_visit, 'DD/MM/YYYY'))
FROM
    assessments_answergroup_institution
WHERE
    questiongroup_id IN (
        SELECT
            id
        FROM
            assessments_questiongroup
        WHERE
            survey_id = 2)
        AND to_char(date_of_visit, 'YYYYMM')::int >= :startyearmonth
        AND to_char(date_of_visit, 'YYYYMM')::int <= :endyearmonth
        AND institution_id IN (:institution_id)
    GROUP BY
        institution_id;

--Upper information

SELECT DISTINCT
    inst.id,
    gp.id,
    gp.const_ward_name,
    district.name,
    block.name,
    cluster.name,
    dise.school_code,
    inst.name
FROM
    schools_institution inst,
    boundary_boundary district,
    boundary_boundary block,
    boundary_boundary CLUSTER,
    boundary_electionboundary gp,
    dise_basicdata dise
WHERE
    inst.admin1_id = district.id
    AND inst.admin2_id = block.id
    AND inst.admin3_id = cluster.id
    AND inst.dise_id = dise.id
    AND inst.gp_id = gp.id
    AND inst.id IN (:institution_id);

--Student count and date of visit per questiongroup

SELECT DISTINCT
    ag.institution_id,
    to_char(ag.date_of_visit, 'DD/MM/YYYY'),
    qg.id,
    qg.name,
    count(DISTINCT ag.id)
FROM
    assessments_answergroup_institution ag,
    assessments_questiongroup qg
WHERE
    ag.questiongroup_id = qg.id
    AND qg.survey_id = 2
    AND to_char(ag.date_of_visit, 'YYYYMM')::int >= :startyearmonth
    AND to_char(ag.date_of_visit, 'YYYYMM')::int <= :endyearmonth
    AND ag.institution_id IN (:institution_id)
GROUP BY
    ag.institution_id,
    ag.date_of_visit,
    qg.id,
    qg.name;

--Table chec

SELECT
    temp.instid,
    temp.dateofvisit,
    temp.qgid,
    temp.qgname,
    temp.sequence,
    temp.numcorrect,
    (temp.numcorrect * 100) / count(DISTINCT ag.id) AS numstudents
FROM
    assessments_answergroup_institution ag,
    ( SELECT DISTINCT
            ag.institution_id AS instid,
            to_char(ag.date_of_visit, 'DD/MM/YYYY') AS dateofvisit,
            qg.id AS qgid,
            qg.name AS qgname,
            qgq.sequence AS SEQUENCE,
            count(ag.id) AS numcorrect
        FROM
            assessments_answergroup_institution ag,
            assessments_questiongroup qg,
            assessments_questiongroup_questions qgq,
            assessments_answerinstitution ans
        WHERE
            ag.questiongroup_id = qg.id
            AND qg.survey_id = 2
            AND to_char(ag.date_of_visit, 'YYYYMM')::int >= :startyearmonth
            AND to_char(ag.date_of_visit, 'YYYYMM')::int <= :endyearmonth
            AND ag.institution_id IN (:institution_id)
            AND ans.answergroup_id = ag.id
            AND ans.question_id = qgq.question_id
            AND ag.questiongroup_id = qgq.questiongroup_id
        GROUP BY
            ag.institution_id,
            ag.date_of_visit,
            qg.id,
            qg.name,
            qgq.sequence,
            ans.answer
        HAVING
            ans.answer = '1') temp
WHERE
    temp.qgid = ag.questiongroup_id
    AND temp.dateofvisit = to_char(ag.date_of_visit, 'DD/MM/YYYY')
    AND ag.institution_id = temp.instid
GROUP BY
    temp.instid,
    temp.dateofvisit,
    temp.qgid,
    temp.qgname,
    temp.sequence,
    temp.numcorrect;

--Least 3 competency <60

SELECT
    instid,
    dateofvisit,
    qgid,
    qgname,
    string_agg(percentage::text, ',')
FROM (
    SELECT
        temp.instid AS instid,
        temp.dateofvisit AS dateofvisit,
        temp.qgid AS qgid,
        temp.qgname AS qgname,
        (temp.numcorrect * 100) / count(DISTINCT ag.id) AS percentage
    FROM
        assessments_answergroup_institution ag,
        ( SELECT DISTINCT
                ag.institution_id AS instid,
                to_char(ag.date_of_visit, 'DD/MM/YYYY') AS dateofvisit,
                qg.id AS qgid,
                qg.name AS qgname,
                qgq.sequence AS SEQUENCE,
                count(ag.id) AS numcorrect
            FROM
                assessments_answergroup_institution ag,
                assessments_questiongroup qg,
                assessments_questiongroup_questions qgq,
                assessments_answerinstitution ans
            WHERE
                ag.questiongroup_id = qg.id
                AND qg.survey_id = 2
                AND to_char(ag.date_of_visit, 'YYYYMM')::int >= :startyearmonth
                AND to_char(ag.date_of_visit, 'YYYYMM')::int <= :endyearmonth
                AND ag.institution_id IN (:institution_id)
                AND ans.answergroup_id = ag.id
                AND ans.question_id = qgq.question_id
                AND ag.questiongroup_id = qgq.questiongroup_id
            GROUP BY
                ag.institution_id,
                ag.date_of_visit,
                qg.id,
                qg.name,
                qgq.sequence,
                ans.answer
            HAVING
                ans.answer = '1') temp
        WHERE
            temp.qgid = ag.questiongroup_id
            AND temp.dateofvisit = to_char(ag.date_of_visit, 'DD/MM/YYYY')
            AND ag.institution_id = temp.instid
        GROUP BY
            temp.instid,
            temp.dateofvisit,
            temp.qgid,
            temp.qgname,
            temp.numcorrect
        HAVING (temp.numcorrect * 100) / count(DISTINCT ag.id) < 60) data
GROUP BY
    instid,
    dateofvisit,
    qgid,
    qgname;

