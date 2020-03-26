UPDATE schools_institution set gp_id=4151 where id=20301;
update assessments_answergroup_institution set date_of_visit='2019-11-20'::timestamp::date where questiongroup_id in (select id from assessments_questiongroup where survey_id=2) and institution_id in (select id from schools_institution where gp_id=1395)  and to_char(date_of_visit,'YYYYMM') = '201911';
update assessments_answergroup_institution set date_of_visit='2019-11-18'::timestamp::date where questiongroup_id in (select id from assessments_questiongroup where survey_id=2) and institution_id in (select id from schools_institution where gp_id=2069)  and to_char(date_of_visit,'YYYYMM') = '201911';
-- Beeranur
UPDATE boundary_electionboundary set const_ward_lang_name='ಬೀರನೂರ' where id=1125;
--Gogi P
UPDATE boundary_electionboundary set const_ward_lang_name='ಗೋಗಿ (ಕೆ)' where id=2114;
-- Heragonagara
UPDATE boundary_electionboundary set const_ward_lang_name='ಹಿರೇಗೊಣ್ಣಾಗರ' where id=2583;
-- Hiramanapura
UPDATE boundary_electionboundary set const_ward_lang_name='ಹಿರೇಮನ್ನಾಪೂರ' where id=2611;
-- Malageti
UPDATE boundary_electionboundary set const_ward_lang_name='ಮಾಲಗಿತ್ತಿ' where id=4151;

