--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6234,'','Hulluru (g)','GP','2','AC');

--update schools_institution
update schools_institution set gp_id=6234 where id in (47982,47981,48045,47951);
update schools_institution set gp_id=5825 where id in (24775,24776);
