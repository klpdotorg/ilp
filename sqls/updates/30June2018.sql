--update boundary_electionboundary
update boundary_electionboundary set const_ward_name='K Ayyanahalli' where id =3113;

--update schools_institution
update schools_institution set gp_id=3113 where id=3221;

--delete boundary_electionboundary
delete from boundary_electionboundary where id=6211;

--update assessments_answergroup_institution(total 83 records)
update assessments_answergroup_institution set institution_id=3426 where institution_id=3526 and questiongroup_id in (21,22,23) and date_of_visit::timestamp between to_timestamp('01-06-2017','dd-mm-yyyy') and to_timestamp('31-04-2018','dd-mm-yyyy');
