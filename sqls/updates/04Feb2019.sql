--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6297,'','Kalkeri','GP','3','AC');

--update schools_institution
update schools_institution set gp_id=1938 where id in (14222);
update schools_institution set gp_id=2872 where id in (13130);
update schools_institution set gp_id=2105 where id in (11994,11996,11997,11998,12039);
update schools_institution set gp_id=4285 where id in (43465,43470);
update schools_institution set gp_id=4155 where id in (37296);
update schools_institution set gp_id=4736 where id in (43497);
update schools_institution set gp_id=5088 where id in (13479,13494,13495,13496,13497);
update schools_institution set gp_id=6189 where id in (48030);
update schools_institution set gp_id=6198 where id in (42658);
update schools_institution set gp_id=6297 where id in (35305,37368,35302,35436);
update schools_institution set gp_id=2771 where id in (6675);
