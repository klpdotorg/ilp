delete from assessments_questiongroup_questions where questiongroup_id in (select id from assessments_questiongroup where survey_id=22);
delete from assessments_answerinstitution where answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id in (select id from assessments_questiongroup where survey_id =22));
delete from assessments_answergroup_institution where questiongroup_id in (select id from assessments_questiongroup where survey_id =22);
delete from assessments_question where id in ();
delete from assessments_questiongroup where id in (select id from assessments_questiongroup where survey_id=22);
delete from assessments_surveytagmapping where survey_id=22;
delete from assessments_surveyusertypemapping where survey_id=22;
delete from assessments_survey where id=22;
