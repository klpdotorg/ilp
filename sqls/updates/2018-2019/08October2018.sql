--insert new muncipality ward
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6246,'','Chikkaballapur Town','MW','2','AC');

--update schools to gp mapping
update schools_institution set gp_id=6237 where id=7092;
update schools_institution set gp_id=6237 where id=43402;
update schools_institution set gp_id=6140 where id=11606;
update schools_institution set gp_id=6140 where id=11604;
update schools_institution set gp_id=6140 where id=11610;
