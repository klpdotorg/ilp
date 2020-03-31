update assessments_answergroup_institution set date_of_visit='2019-08-22'::timestamp::date where questiongroup_id in (select id from assessments_questiongroup where survey_id=2) and institution_id in (select id from schools_institution where gp_id =5017)  and to_char(date_of_visit,'YYYYMM') = '201909';
update assessments_answergroup_institution set date_of_visit='2019-08-21'::timestamp::date where questiongroup_id in (select id from assessments_questiongroup where survey_id=2) and institution_id in (select id from schools_institution where gp_id =5741)  and to_char(date_of_visit,'YYYYMM') = '201909';
update assessments_answergroup_institution set date_of_visit='2019-12-12'::timestamp::date where questiongroup_id in (select id from assessments_questiongroup where survey_id=2) and institution_id in (select id from schools_institution where gp_id =4037)  and to_char(date_of_visit,'YYYYMM') = '201909';

--Lot 21 gp names updates
UPDATE boundary_electionboundary SET const_ward_lang_name='ಮುಖಹಳ್ಲಿ' WHERE id=4533;
UPDATE boundary_electionboundary SET const_ward_lang_name='ಮೇಣದಾಳ' WHERE id=4425;
UPDATE boundary_electionboundary SET const_ward_lang_name='ಹದ್ಲಿ' WHERE id=2291;
--Chamarajanagara name update
UPDATE boundary_boundary SET lang_name='ಚಾಮರಾಜನಗರ' WHERE id=439;