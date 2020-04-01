update schools_institution set status_id='DL' where id in (10452,10455,10254,10312);
update schools_student set status_id='DL' where institution_id in (10452,10455,10254,10312);
update schools_studentgroup set status_id='DL' where institution_id in (10452,10455,10254,10312);
update schools_studentstudentgrouprelation set status_id='DL' where student_id in (select id from schools_student where institution_id in (10452,10455,10254,10312));
