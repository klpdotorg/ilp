--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6282,'','Nelajeri','GP','2','AC');

--update schools_institution
update schools_institution set gp_id=6282 where id in (20357,20361,20358);

