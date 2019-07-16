--delete invalid assessment
delete from assessments_answerinstitution where answergroup_id in (1303759,1283360,1283361,1289550);
delete from assessments_answergroup_institution where id in (1303759,1283360,1283361,1289550);
