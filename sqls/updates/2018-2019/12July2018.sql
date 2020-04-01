--insert new gps
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6212,'','I Basapura','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6213,'','Govinda Wadi','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6214,'','Jodalli','GP','2','AC');

--update schools_institution
update schools_institution set gp_id=6213 where id in (47546,47538,47544);
update schools_institution set gp_id=6212 where id in (42549,42546);
update schools_institution set gp_id=6213 where id in (43339);
