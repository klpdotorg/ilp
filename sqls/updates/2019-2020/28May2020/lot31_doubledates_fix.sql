update assessments_answergroup_institution set date_of_visit='2020-03-01'::timestamp::date where questiongroup_id in (select id from assessments_questiongroup where survey_id=2) and institution_id in (select id from schools_institution where gp_id=676) and to_char(date_of_visit,'YYYYMM') = '202003';
update assessments_answergroup_institution set date_of_visit='2020-02-20'::timestamp::date where questiongroup_id in (select id from assessments_questiongroup where survey_id=2) and institution_id in (select id from schools_institution where gp_id=2971) and to_char(date_of_visit,'YYYYMM') = '201909';
update assessments_answergroup_institution set date_of_visit='2020-01-30'::timestamp::date where questiongroup_id in (select id from assessments_questiongroup where survey_id=2) and institution_id in (select id from schools_institution where gp_id=3178) and to_char(date_of_visit,'YYYYMM') = '202001';
update assessments_answergroup_institution set date_of_visit='2020-01-30'::timestamp::date where questiongroup_id in (select id from assessments_questiongroup where survey_id=2) and institution_id in (select id from schools_institution where gp_id=3606) and to_char(date_of_visit,'YYYYMM') = '201911';
update assessments_answergroup_institution set date_of_visit='2020-01-31'::timestamp::date where questiongroup_id in (select id from assessments_questiongroup where survey_id=2) and institution_id in (select id from schools_institution where gp_id=5089) and to_char(date_of_visit,'YYYYMM') = '202001';

