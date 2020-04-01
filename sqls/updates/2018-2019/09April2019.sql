--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6305,'','Somanathapura (mys)','GP','2','AC');

--update schools to gp mapping
update schools_institution set gp_id=5458 where id=10497;
update schools_institution set gp_id=1467 where id=10273;
update schools_institution set gp_id=6305 where id in (55697,55694,55696,55590,55695,55693);
update schools_institution set gp_id=3962 where id=6756;

--update date_of_visit
update assessments_answergroup_institution set institution_id=6756 where questiongroup_id in (45,46,47) and institution_id=7055 and date_of_visit::timestamp BETWEEN to_timestamp('24/02/2018','dd/mm/yyyy') and to_timestamp('27/02/2018','dd/mm/yyyy');
update assessments_answergroup_institution set date_of_visit=Timestamp '2019-02-25' where questiongroup_id in (45,46,47) and institution_id=6755 and date_of_visit::timestamp BETWEEN to_timestamp('24/02/2018','dd/mm/yyyy') and to_timestamp('27/02/2018','dd/mm/yyyy');
update assessments_answergroup_institution set date_of_visit=Timestamp '2019-02-25' where questiongroup_id in (45,46,47) and institution_id=6756 and date_of_visit::timestamp BETWEEN to_timestamp('24/02/2018','dd/mm/yyyy') and to_timestamp('27/02/2018','dd/mm/yyyy');
