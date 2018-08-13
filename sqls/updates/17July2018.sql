--update assessment_answergroup_institution
update assessments_answergroup_institution set date_of_visit=Timestamp '2018-01-31' where questiongroup_id in (21,22) and institution_id=12834 and date_of_visit::timestamp BETWEEN to_timestamp('31/01/2018','dd/mm/yyyy') and to_timestamp('02/02/2018','dd/mm/yyyy');

--update schools_institution
update schools_institution set gp_id=6172 where id=13709;
