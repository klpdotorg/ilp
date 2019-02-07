--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6283,'','Anoor','GP','2','AC');

--update schools_institution
update schools_institution set gp_id=6283 where id in (11058,11055,11057,11073,11067,11068,11061,11054,11070,11069);
