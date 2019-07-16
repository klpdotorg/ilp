SELECT
    data.qgid,
    data1.numstu,
    sum(
        CASE WHEN percentage <= 35 THEN
            1
        END) AS per35,
    sum(
        CASE WHEN percentage <= 60
            AND percentage > 35 THEN
            1
        END) AS per35_60,
    sum(
        CASE WHEN percentage > 60
            AND percentage <= 75 THEN
            1
        END) AS per61_70,
    sum(
        CASE WHEN percentage > 75 THEN
            1
        END) AS perc75
FROM ( SELECT DISTINCT
        ag.questiongroup_id qgid,
        ag.id agid,
        sum(ans.answer::int) * 100 / 20 percentage
    FROM
        assessments_answergroup_institution ag,
        assessments_answerinstitution ans
    WHERE
        ans.answergroup_id = ag.id
        AND ag.questiongroup_id IN (
            SELECT
                id
            FROM
                assessments_questiongroup
            WHERE
                survey_id = 2)
            AND ag.institution_id IN (
                SELECT
                    id
                FROM
                    schools_institution
                WHERE
                    gp_id = 741)
                AND ans.question_id NOT IN (291, 130)
            GROUP BY
                ag.questiongroup_id,
                ag.id) data,
    ( SELECT DISTINCT
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
                AND ag.institution_id IN (
                    SELECT
                        id
                    FROM
                        schools_institution
                    WHERE
                        gp_id = 741)
                GROUP BY
                    ag.questiongroup_id) data1
WHERE
    data.qgid = data1.qgid
GROUP BY
    data.qgid,
    data1.numstu;

SELECT
    data.key,
    data.qgid,
    data1.numstu,
    count(data.agid),
    (count(data.agid) * 100) / data1.numstu
FROM ( SELECT DISTINCT
        qmap.key AS KEY,
        ag.questiongroup_id AS qgid,
        qmap.max_score,
        ag.id AS agid,
        sum(ans.answer::int) AS answer
    FROM
        assessments_competencyquestionmap qmap,
        assessments_answergroup_institution ag,
        assessments_answerinstitution ans
    WHERE
        ag.id = ans.answergroup_id
        AND ag.questiongroup_id = qmap.questiongroup_id
        AND ans.question_id = qmap.question_id
        AND ag.institution_id IN (
            SELECT
                id
            FROM
                schools_institution
            WHERE
                gp_id = 741)
        GROUP BY
            qmap.key,
            ag.questiongroup_id,
            qmap.max_score,
            ag.id
        HAVING
            sum(ans.answer::int) >= sum(qmap.max_score)) data,
    ( SELECT DISTINCT
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
                AND ag.institution_id IN (
                    SELECT
                        id
                    FROM
                        schools_institution
                    WHERE
                        gp_id = 741)
                GROUP BY
                    ag.questiongroup_id) data1
WHERE
    data.qgid = data1.qgid
GROUP BY
    data.key,
    data.qgid,
    data1.numstu
ORDER BY
    data.qgid;

