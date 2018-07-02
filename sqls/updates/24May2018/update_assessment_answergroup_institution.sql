update assessments_answergroup_institution set institution_id=3395 where questiongroup_id in (22) and institution_id=3364 and date_of_visit::timestamp BETWEEN to_timestamp('01/08/2017','dd/mm/yyyy') and to_timestamp('31/08/2017','dd/mm/yyyy');

update assessments_answergroup_institution set institution_id=31104 where questiongroup_id in (23) and institution_id=6432 and date_of_visit::timestamp BETWEEN to_timestamp('01/12/2017','dd/mm/yyyy') and to_timestamp('31/12/2017','dd/mm/yyyy');

update assessments_answergroup_institution set institution_id=23765 where questiongroup_id in (23) and institution_id=23756 and date_of_visit::timestamp BETWEEN to_timestamp('01/02/2018','dd/mm/yyyy') and to_timestamp('28/02/2018','dd/mm/yyyy');

update assessments_answergroup_institution set date_of_visit=Timestamp '2018-01-12' where questiongroup_id in (23) and institution_id=11934 and date_of_visit::timestamp BETWEEN to_timestamp('01/02/2018','dd/mm/yyyy') and to_timestamp('28/02/2018','dd/mm/yyyy');

update assessments_answergroup_institution set date_of_visit=Timestamp '2018-01-12' where questiongroup_id in (23) and institution_id=11935 and date_of_visit::timestamp BETWEEN to_timestamp('01/02/2018','dd/mm/yyyy') and to_timestamp('28/02/2018','dd/mm/yyyy');

update assessments_answergroup_institution set institution_id=3229 where questiongroup_id in (21,22,23) and institution_id=3329 and date_of_visit::timestamp BETWEEN to_timestamp('01/12/2017','dd/mm/yyyy') and to_timestamp('31/12/2017','dd/mm/yyyy');

update assessments_answergroup_institution set institution_id=4164 where questiongroup_id in (21,22) and institution_id=4162 and date_of_visit::timestamp BETWEEN to_timestamp('01/11/2017','dd/mm/yyyy') and to_timestamp('31/11/2017','dd/mm/yyyy');

update assessments_answergroup_institution set institution_id=36222 where questiongroup_id in (21,22,23) and institution_id=35881 and date_of_visit::timestamp BETWEEN to_timestamp('01/12/2017','dd/mm/yyyy') and to_timestamp('31/12/2017','dd/mm/yyyy');

update assessments_answergroup_institution set institution_id=13296 where questiongroup_id in (21) and institution_id=13295 and date_of_visit::timestamp BETWEEN to_timestamp('01/02/2018','dd/mm/yyyy') and to_timestamp('28/02/2018','dd/mm/yyyy');

update assessments_answergroup_institution set institution_id=24846 where institution_id=24847 and questiongroup_id in (21,22,23);

update schools_institution set gp_id=5586 where id in (24846,24847);

