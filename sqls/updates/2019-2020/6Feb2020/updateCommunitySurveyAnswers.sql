update assessments_answerinstitution set answer=1 where answer='Yes' and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id in (select id from assessments_questiongroup where survey_id=7));
update assessments_answerinstitution set answer=0 where answer='No' and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id in (select id from assessments_questiongroup where survey_id=7));
update assessments_answerinstitution set answer=99 where answer like 'Don%' and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id in (select id from assessments_questiongroup where survey_id=7));
update assessments_answerinstitution set answer=88 where answer='Unknown' and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id in (select id from assessments_questiongroup where survey_id=7));