--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values ('6298','','Navali (kpl)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values ('6299','','Begur (dwd)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values ('6300','','Begur (chkmglr)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values ('6301','','Begur (tmkr)','GP','2','AC');

--update schools to gp mapping
update schools_institution set gp_id=6298 where id in (19738,19742,38254,19739,19729,19732);
update schools_institution set gp_id=6299 where id in (37538,37537,37535,37534,37532);
update schools_institution set gp_id=6300 where id in (44957,44945,44958,44955,44950,44951,44956,44946,44947);
update schools_institution set gp_id=6301 where id in (58377,58376,58346,58347,58348,58349,58345);
