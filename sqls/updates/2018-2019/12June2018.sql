--update assessments_survey
update assessments_survey set name='GKA Class Visit' where id=11;
update assessments_survey set name='GKA Class Visit' where id=14;

--update assessments_questiongroup
update assessments_questiongroup set name='GKA Class Visit' where id=42;

--delete repeated/duplicate answers for question_group=17
delete from assessments_answerinstitution where answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=17) and question_id in (144,138,147,270,145,143,269,148,150,149);
