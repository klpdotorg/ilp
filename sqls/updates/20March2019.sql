--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values ('6304','','Chikkamadinal','GP','2','AC');

--update schools to gp mapping
update scools_institution set gp_id=6304 where id in (19715,19718,19726);