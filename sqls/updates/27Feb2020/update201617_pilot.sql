insert into assessments_survey(name,status_id,admin0_id,survey_on_id,created_at) values('GPPilot','IA',2,'institution',current_timestamp);

insert into assessments_questiongroup(name,start_date, double_entry,created_at,inst_type_id,status_id,survey_id,type_id) select 'Class4Pilot','2016-06-01',False,current_timestamp,'primary','IA',currval('assessments_survey_id_seq'),'assessment';
update assessments_answergroup_institution set questiongroup_id=(select currval('assessments_questiongroup_id_seq')) where questiongroup_id=21 and to_char(date_of_visit,'YYYYMM')::int >=201606 and to_char(date_of_visit,'YYYYMM')::int <=201705 and institution_id in(select id from schools_institution where admin1_id in (420,433));

insert into assessments_questiongroup(name,start_date, double_entry,created_at,inst_type_id,status_id,survey_id,type_id) select 'Class5Pilot','2016-06-01',False,current_timestamp,'primary','IA',currval('assessments_survey_id_seq'),'assessment';
update assessments_answergroup_institution set questiongroup_id=(select currval('assessments_questiongroup_id_seq')) where questiongroup_id=22 and to_char(date_of_visit,'YYYYMM')::int >=201606 and to_char(date_of_visit,'YYYYMM')::int <=201705 and institution_id in(select id from schools_institution where admin1_id in (420,433));

insert into assessments_questiongroup(name,start_date, double_entry,created_at,inst_type_id,status_id,survey_id,type_id) select 'Class6Pilot','2016-06-01',False,current_timestamp,'primary','IA',currval('assessments_survey_id_seq'),'assessment';
update assessments_answergroup_institution set questiongroup_id=(select currval('assessments_questiongroup_id_seq')) where questiongroup_id=23 and to_char(date_of_visit,'YYYYMM')::int >=201606 and to_char(date_of_visit,'YYYYMM')::int <=201705 and institution_id in(select id from schools_institution where admin1_id in (420,433));
