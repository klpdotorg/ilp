UPDATE boundary_electionboundary SET const_ward_lang_name='ಮರಟುರಾ' WHERE id=4336;
UPDATE boundary_electionboundary SET const_ward_lang_name='ಪಸಪುಲ್' WHERE id=4967;
UPDATE boundary_electionboundary SET const_ward_lang_name='ಎಲ್ಲೇರಿ' WHERE id=6083;
UPDATE boundary_electionboundary SET const_ward_lang_name='ನಾರಾಯಣಪುರ' WHERE id=6417;
UPDATE boundary_electionboundary SET const_ward_lang_name='ಕಲ್ಲಹಂಗರಗ' WHERE id=213009038;

-- GP contest double dates fixes
update assessments_answergroup_institution set date_of_visit='2019-01-25'::timestamp::date where questiongroup_id in (select id from assessments_questiongroup where survey_id=2) and institution_id in (select id from schools_institution where gp_id=5893) and to_char(date_of_visit,'YYYYMM') = '201911';
update assessments_answergroup_institution set date_of_visit='2019-12-30'::timestamp::date where questiongroup_id in (select id from assessments_questiongroup where survey_id=2) and institution_id in (select id from schools_institution where gp_id=213009038) and to_char(date_of_visit,'YYYYMM') = '201911';

