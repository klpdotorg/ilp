--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6257,'','Sibatala','GP','3','AC');

--update schools to gp mapping
update schools_institution set gp_id=6257 where id in (145687,120965,144413,164454,176662);
