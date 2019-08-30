DROP MATERIALIZED VIEW IF EXISTS mvw_hh_survey_institution_respondent_ans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_hh_survey_institution_respondent_ans_agg AS
SELECT format('A%s_%s_%s_%s_%s', survey_id,institution_id,yearmonth,question_id,respondent_type) as id,
    survey_id,
    institution_id,
    yearmonth,
    respondent_type,
    question_id,
    question_desc,
    count_yes,
    count_no,
    count_unknown
FROM(
	select questiongroup.survey_id as survey_id,
	ag.institution_id as institution_id,
	to_char(ag.date_of_visit,'YYYYMM')::int as yearmonth,
	respondent.name as respondent_type,
	q.id as question_id,
        case q.display_text when '' then q.question_text else q.display_text end as question_desc,
	count(case ans.answer when 'Yes' then ag.id end) as count_yes,
	count(case ans.answer when 'No' then ag.id end) as count_no,
       	count( case when ans.answer not in ('Yes','No') then ag.id end) as count_unknown
	from
	assessments_answergroup_institution ag, assessments_answerinstitution ans, assessments_questiongroup as questiongroup, common_respondenttype as respondent, assessments_question as q 
	where
	ag.questiongroup_id=questiongroup.id
	and ag.respondent_type_id=respondent.char_id
	and ans.answergroup_id=ag.id
	and ans.question_id=q.id
	and questiongroup.survey_id=7
	group by questiongroup.survey_id, ag.institution_id,to_char(ag.date_of_visit,'YYYYMM')::int,respondent.name,q.id)info;
-- 
DROP MATERIALIZED VIEW IF EXISTS mvw_hh_institution_question_ans_agg CASCADE;
CREATE MATERIALIZED VIEW mvw_hh_institution_question_ans_agg AS
WITH subquery1 AS
(
SELECT format('A%s_%s_%s', survey_id,institution_id) as id,
	questiongroup.survey_id as survey_id,
	ag.institution_id as institution_id,
	schools.name as institution_name,
	schools.gp_id as gp_id,
	eb.const_ward_name as gp_name,
	b1.name as district_name,
	b2.name as block_name,
	b3.name as cluster_name,
	q.id as question_id,
	CASE q.display_text WHEN '' THEN q.question_text ELSE q.display_text END as question_desc,
	q.lang_name as lang_questiondesc,
	qngroup_questions.sequence AS seq,
	COUNT(CASE ans.answer WHEN 'Yes' THEN ag.id END) AS count_yes,
	COUNT(CASE ans.answer WHEN 'No' THEN ag.id END) AS count_no,
	COUNT(CASE WHEN ans.answer NOT IN ('Yes','No') THEN ag.id END) AS count_unknown,
	COUNT(ans.answer) AS total
FROM assessments_answergroup_institution ag, 
	assessments_answerinstitution ans, 
	assessments_questiongroup as questiongroup, 
	assessments_question as q,
	assessments_questiongroup_questions qngroup_questions,
	schools_institution as schools,
	boundary_electionboundary as eb,
	boundary_boundary as b1,
	boundary_boundary as b2,
	boundary_boundary as b3
WHERE
	ag.date_of_visit BETWEEN :from_date and :to_date
	and ag.questiongroup_id=questiongroup.id
	and ans.answergroup_id=ag.id
	and ans.question_id=q.id
	and questiongroup.survey_id=7
	and q.id=qngroup_questions.question_id 
	and qngroup_questions.questiongroup_id=questiongroup.id
	and schools.id = ag.institution_id
	and schools.gp_id = eb.id
	and schools.admin1_id = b1.id
	and schools.admin2_id = b2.id
	and schools.admin3_id = b3.id
GROUP BY
	questiongroup.survey_id, 
	ag.institution_id,
	schools.name,
	schools.gp_id,
	b1.name,
	b2.name,
	b3.name,
	eb.const_ward_name,
	qngroup_questions.sequence,
	q.id
)
SELECT 
	id,
	survey_id, 
	institution_id,
	institution_name,
	gp_id,
	gp_name,
	district_name,
	block_name,
	cluster_name,
	question_id,
	question_desc,
	lang_questiondesc,
	seq,
	total,
	count_yes*100/total AS perc_yes,
	count_no*100/total AS perc_no,
	count_unknown*100/total AS perc_unknown
FROM
subquery1
GROUP BY id,survey_id, institution_id, institution_name, gp_id, gp_name, district_name, block_name, cluster_name, question_id, question_desc,lang_questiondesc,seq,total,count_yes, count_no, count_unknown;


