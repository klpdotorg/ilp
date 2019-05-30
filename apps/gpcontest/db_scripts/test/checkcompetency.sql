SELECT
    data.dateofvisit,
    data.qgid,
    data.instid,
    data.key,
    data1.numstu,
    ((data1.numstu - count(data.agid)) * 100) / data1.numstu
FROM ( SELECT DISTINCT
        to_char(ag.date_of_visit, 'DD/MM/YYYY') AS dateofvisit,
        ag.institution_id AS instid,
        ag.questiongroup_id AS qgid,
        qmap.key AS KEY,
        ag.id AS agid
    FROM
        assessments_competencyquestionmap qmap,
        assessments_answergroup_institution ag,
        assessments_answerinstitution ans
    WHERE
        ag.id = ans.answergroup_id
        AND ag.questiongroup_id = qmap.questiongroup_id
        AND ans.question_id = qmap.question_id
        AND ag.institution_id IN (:institution_id)
        AND ag.questiongroup_id IN (
            SELECT
                id
            FROM
                assessments_questiongroup
            WHERE
                survey_id = 2)
            AND to_char(ag.date_of_visit, 'YYYYMM')::int >= :startyearmonth
            AND to_char(ag.date_of_visit, 'YYYYMM')::int <= :endyearmonth
        GROUP BY
            ag.date_of_visit,
            qmap.key,
            ag.questiongroup_id,
            qmap.max_score,
            ag.id,
            ag.institution_id
        HAVING
            sum(ans.answer::int) < sum(qmap.max_score)) data,
    ( SELECT DISTINCT
            to_char(ag.date_of_visit, 'DD/MM/YYYY') AS dateofvisit,
            ag.questiongroup_id qgid,
            count(DISTINCT ag.id) AS numstu
        FROM
            assessments_answergroup_institution ag
        WHERE
            ag.questiongroup_id IN (
                SELECT
                    id
                FROM
                    assessments_questiongroup
                WHERE
                    survey_id = 2)
                AND ag.institution_id IN (:institution_id)
                AND to_char(ag.date_of_visit, 'YYYYMM')::int >= :startyearmonth
                AND to_char(ag.date_of_visit, 'YYYYMM')::int <= :endyearmonth
            GROUP BY
                ag.questiongroup_id,
                ag.date_of_visit) data1
WHERE
    data.qgid = data1.qgid
    AND data.dateofvisit = data1.dateofvisit
GROUP BY
    data.qgid,
    data.instid,
    data.key,
    data1.numstu,
    data.dateofvisit
HAVING ((data1.numstu - count(data.agid)) * 100) / data1.numstu < 60
ORDER BY
    data.dateofvisit,
    data.qgid;

