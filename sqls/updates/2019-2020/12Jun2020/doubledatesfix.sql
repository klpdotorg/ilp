update assessments_answergroup_institution set date_of_visit='2020-03-11'::timestamp::date where questiongroup_id in (select id from assessments_questiongroup where survey_id=2) and institution_id in (select id from schools_institution where gp_id=676);
update assessments_answergroup_institution set date_of_visit='2020-02-20'::timestamp::date where questiongroup_id in (select id from assessments_questiongroup where survey_id=2) and institution_id in (select id from schools_institution where gp_id=2971);
update assessments_answergroup_institution set date_of_visit='2020-01-30'::timestamp::date where questiongroup_id in (select id from assessments_questiongroup where survey_id=2) and institution_id in (select id from schools_institution where gp_id=3606);
update schools_institution set gp_id=4651 where id=59251;
update schools_institution set gp_id=3076 where id=58483;

-- Another double dates issue after above fixes were done
update assessments_answergroup_institution set date_of_visit='2019-10-25'::timestamp::date where questiongroup_id in (select id from assessments_questiongroup where survey_id=2) and institution_id in (select id from schools_institution where gp_id=4651);
