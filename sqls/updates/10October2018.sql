--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6252,'','MUGALANAGAON','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6253,'','MINDIGAL','GP','2','AC');


--update school to gp mapping
update schools_institution set gp_id=6253 where id=11103;
update schools_institution set gp_id=6253 where id=11105;
update schools_institution set gp_id=6253 where id=10924;
update schools_institution set gp_id=6252 where id=14414;
update schools_institution set gp_id=6252 where id=14415;
update schools_institution set gp_id=6252 where id=14416;
