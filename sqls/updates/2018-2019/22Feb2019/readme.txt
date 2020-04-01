1. get list of questions using :-
select string_agg(question_id::text, ',') from assessments_questiongroup_questions where questiongroup_id in (select id from assessments_questiongroup where survey_id=22);
2. put this outupt in 2 query in the delete sql file.

