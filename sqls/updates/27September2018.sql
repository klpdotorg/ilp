--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6240,'','Muradi','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6241,'','Petalur','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6242,'','Kondikoppa','GP','2','AC');

--update schools to gp mapping
update schools_institution set gp_id=6240 where id=36832;
update schools_institution set gp_id=6240 where id=36836;
update schools_institution set gp_id=6240 where id=36817;
update schools_institution set gp_id=6240 where id=36833;
update schools_institution set gp_id=6241 where id=36829;
update schools_institution set gp_id=6241 where id=36904;
update schools_institution set gp_id=6241 where id=36900;
update schools_institution set gp_id=6242 where id=37657;
