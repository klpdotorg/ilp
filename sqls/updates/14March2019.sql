--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values ('6298','','Navali (kpl)','GP','2','AC');

--update schools to gp mapping
update schools_institution set gp_id=6298 where id in (19738,19742,38254,19739,19729,19732);
