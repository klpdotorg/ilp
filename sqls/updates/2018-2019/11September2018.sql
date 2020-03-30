--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6236,'','Bagewadi (b)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6237,'','Ramapura (ch)','GP','2','AC');
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6238,'','Yaragera','GP','2','AC');

--update gp name
update boundary_electionboundary set const_ward_name='Bagewadi (g)' where id=926;
update boundary_electionboundary set const_ward_name='Ramapura (cb)' where id=5078;
update boundary_electionboundary set const_ward_name='Yeragera' where id=6105;
