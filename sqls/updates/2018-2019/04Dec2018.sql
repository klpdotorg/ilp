--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6265,'','Rampurahalli','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6266,'','Rampura (dvg)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6267,'','Rampura (hsn)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6268,'','Rampura (rmngr)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6269,'','Rampura (mysr)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6270,'','Aluru (chmngr)','GP','2','AC');

--update schools_institution
update schools_institution set gp_id=6265 where id in (38340,14336,14341,38068);
update schools_institution set gp_id=5087 where id in (13495,13479,13494,13496,13497);
update schools_institution set gp_id=6266 where id in (47227,47226,47228,47291);
update schools_institution set gp_id=6267 where id in (48774,48748,48744,48669,48778,48776,48779,48775);
update schools_institution set gp_id=6268 where id in (34680,34677,34679,34681,34682,34683,34676);
update schools_institution set gp_id=6269 where id in (54990,54988,54991,33513,54989);
update schools_institution set gp_id=6270 where id in (6501,43318,6530,6497,6499,6529,6551,6508,6498,30202);

--update boundary_electionboundary
update boundary_electionboundary set const_ward_name='Rampura (cht)' where id=5087;
update boundary_electionboundary set const_ward_name='Rampura (bly)' where id=5088;
