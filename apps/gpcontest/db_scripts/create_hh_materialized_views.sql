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
 
