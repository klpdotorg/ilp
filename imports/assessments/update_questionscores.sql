update assessments_question set pass_score='Yes' where id in (select question_id from assessments_questiongroup_questions  where questiongroup_id in (21,22,23)) and options='{Yes,No}';
update assessments_question set pass_score=1 where question_text like 'do_%';
