--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6235,'','Ibrahimpur (d)','GP','2','AC');

--db update
update boundary_electionboundary set const_ward_name='Ibrahimpur (y)' where id=2914;
update schools_institution set gp_id=5078 where id=11248;
update schools_institution set gp_id=6235 where id=37721;
