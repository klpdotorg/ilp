--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values ('6302','','Baragur (kpl)','GP','2','AC');

--update schools to gp mapping
update schools_institution set gp_id=5656 where id=35143;
update schools_institution set gp_id=6178 where id=43431;
update schools_institution set gp_id=6302 where id in (19745,19772,19752,19777,19773);
