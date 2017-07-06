delete from schools_studentgroup where institution_id in (30725,33709,37176,37201,37901);
delete from schools_institution_languages where institution_id in (30725,33709,37176,37201,37901);
delete from object_permissions_institution_perms where obj_id in (30725,33709,37176,  37201,37901);
delete from schools_assessment_institution_association where institution_id in (30725,33709,37176,  37201,37901);
delete from schools_staff where institution_id in (30725, 33709,37176,  37201,37901);
delete from schools_institution where id in (30725,33709,37176,37201,37901);
update schools_institution set institution_gender='co-ed' where institution_gender='NULL';
