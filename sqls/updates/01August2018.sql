--insert new gp
insert into boundary_electionboundary (id,dise_slug,const_ward_name,const_ward_type_id,state_id,status_id) values (6234,'','Hulluru (g)','GP','2','AC');

--update schools_institution
update schools_institution set gp_id=6234 where id in (47982,47981,48045,47951);
update schools_institution set gp_id=5825 where id in (24775,24776);

--delete duplicate student
update schools_student set status_id='DL' where id='2492683';
update schools_studentstudentgrouprelation set status_id='DL' where student_id='2492683' and academic_year_id='1819';

--update student_group
update schools_studentstudentgrouprelation set student_group_id=3479954 where student_id=2492688 and academic_year_id='1819';
