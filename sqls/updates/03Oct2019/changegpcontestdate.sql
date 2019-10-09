update assessments_answergroup_institution set date_of_visit='2019-08-17' where questiongroup_id in (62,63,64) and institution_id in (select id from schools_institution where gp_id=4035);
