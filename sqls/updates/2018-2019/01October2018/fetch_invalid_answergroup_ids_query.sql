select id from assessments_answergroup_institution where questiongroup_id=42 and institution_id in (select id from schools_institution where admin1_id not in (433,439,441,425,421,420,417,419,416,418,445,424));