UPDATE assessments_answergroup_institution SET date_of_visit='2020-12-14' WHERE institution_id IN (select id from schools_institution where gp_id=2534) AND date_of_visit='2018-12-16' and questiongroup_id IN (45,46,47);