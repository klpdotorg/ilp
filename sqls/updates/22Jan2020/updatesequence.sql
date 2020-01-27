update assessments_questiongroup_questions set sequence=6 where questiongroup_id=17 and sequence=1;
update assessments_questiongroup_questions set sequence=1 where questiongroup_id=17 and question_id=131;
update assessments_questiongroup_questions set sequence=2 where questiongroup_id=17 and question_id=266;

update assessments_questiongroup_questions set sequence=5 where questiongroup_id=24 and sequence=1;
update assessments_questiongroup_questions set sequence=1 where questiongroup_id=24 and question_id=302;
update assessments_questiongroup_questions set sequence=2 where questiongroup_id=24 and question_id=303;
insert into assessments_questiongroup_questions(sequence, questiongroup_id, question_id) values(4,24,601);
update assessments_questiongroup_questions set sequence=5 where questiongroup_id=24 and question_id=300;
