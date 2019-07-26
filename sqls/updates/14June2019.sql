--delete duplicate assessment for class 4
delete from assessments_answerinstitution where answergroup_id in (1505985,1505986,1505987,1505988,1505989,1505990,1505991);
delete from assessments_answergroup_institution where id in (1505985,1505986,1505987,1505988,1505989,1505990,1505991);

--delete duplicate assessment for class 5
delete from assessments_answerinstitution where answergroup_id in (1507654,1507655,1507656,1507657,1507658,1507659);
delete from assessments_answergroup_institution where id in (1507654,1507655,1507656,1507657,1507658,1507659);

--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6306,'','Tadola','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6307,'','Gorabala','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6308,'','Thaluru','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6309,'','Konkal (ydr)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6310,'','Janukonda','GP','2','AC');


--update school to gp mapping
update schools_institution set gp_id=6306 where id in (13631,13636,13637); 
update schools_institution set gp_id=6193 where id in (23953,23950); 
update schools_institution set gp_id=6307 where id in (2462,39190,2466,2461,39185); 
update schools_institution set gp_id=6308 where id in (30125); 
update schools_institution set gp_id=6309 where id in (25752,25742,25754,25747,25743,25755); 
update schools_institution set gp_id=6310 where id in (11994,11998,11996,11997,12039); 
update schools_institution set gp_id=6259 where id in (35160,35161,35171); 
