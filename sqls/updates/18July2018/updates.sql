--update schools_institution
update schools_institution set gp_id=3336 where id in (12644,12643);
update schools_institution set gp_id=6233 where id=37301;
update schools_institution set gp_id=6233 where id=37298;

--update boundary_electionboundary
update boundary_electionboundary  set const_ward_name='Kantanakunte' where id=3399;

--update schools_student
update schools_student set first_name='ARCHITHA' where id=5509323;
update schools_student set first_name='ANIL KUMAR N' where id=2490480;

--update schools_studentstudentgrouprelation
update schools_studentstudentgrouprelation set student_group_id=3478808 where student_id=2491666 and academic_year_id='1819';
update schools_studentstudentgrouprelation set student_group_id=3478808 where student_id=2781134 and academic_year_id='1819';
update schools_studentstudentgrouprelation set student_group_id=3478808 where student_id=2781133 and academic_year_id='1819';

