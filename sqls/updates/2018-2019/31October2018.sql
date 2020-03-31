--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6254,'','Hallikeri (g)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6255,'','Mangala (my)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6256,'','Mangala (gpt)','GP','2','AC');

--db update
update boundary_electionboundary set const_ward_name='Hallikeri (d)' where id=2359;
update schools_institution set gp_id=6254 where id in (36905,36906,36901,36902,36903);
update schools_institution set gp_id=6255 where id in (53318,53317,53309,53314,53311);
update schools_institution set gp_id=6256 where id in (6798,6802,6800,6795,6797);
update schools_institution set gp_id=2377 where id=11604;
update schools_institution set gp_id=2624 where id=11232;
update schools_institution set gp_id=5375 where id=43235;
update schools_institution set gp_id=2753 where id=42832;
update schools_institution set gp_id=3815 where id=7045;
update schools_institution set gp_id=3575 where id=6909;
update schools_institution set gp_id=5375 where id=43235;
update schools_institution set gp_id=3795 where id=6686;
update schools_institution set gp_id=1647 where id=11120;
update schools_institution set gp_id=6097 where id=43315;
update schools_institution set gp_id=5061 where id=47886;
update schools_institution set gp_id=1298 where id=43088;
update schools_institution set gp_id=5257 where id=37657;

--update date_of_visit
update assessments_answergroup_institution set date_of_visit=Timestamp '2018-08-28' where questiongroup_id in (46) and institution_id=11606 and date_of_visit::timestamp BETWEEN to_timestamp('01/09/2018','dd/mm/yyyy') and to_timestamp('05/09/2018','dd/mm/yyyy');
update assessments_answergroup_institution set date_of_visit=Timestamp '2018-09-04' where questiongroup_id in (46) and institution_id=11593 and date_of_visit::timestamp BETWEEN to_timestamp('01/08/2018','dd/mm/yyyy') and to_timestamp('30/08/2018','dd/mm/yyyy');
