-- GP 2194 has two dates in 2017-2018. Feb 16 and Feb 20 2018. Srikant
-- needs reports for this GP and asked to fix the date as Feb 20.
update assessments_answergroup_institution set date_of_visit='2018-02-20'::timestamp::date where questiongroup_id in (select id from assessments_questiongroup where survey_id=2) and institution_id in (select id from schools_institution where gp_id=2194)  and to_char(date_of_visit,'YYYYMM') = '201802';
update boundary_electionboundary set const_ward_lang_name='ಗುಡ್ಡದರಂಗವನಹಳ್ಳಿ' where id=2194;