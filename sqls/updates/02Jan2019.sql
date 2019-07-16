--insert schools_institution
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6279,'','Masab Hanchinhal','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6280,'','Tummaraguddi','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6281,'','Gollahalli (blr)','GP','2','AC');

--update schools_institution
update schools_institution set gp_id=6279 where id in (20408,20409,20530);
update schools_institution set gp_id=6280 where id in (20473,20497,20504);
update schools_institution set gp_id=6281 where id in (43075,43074,43073,43072,43068,43070);
