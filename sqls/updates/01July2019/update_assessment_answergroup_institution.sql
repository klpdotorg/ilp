--update assessment_answergroup_institution
update assessments_answergroup_institution set date_of_visit=Timestamp '2018-09-03' where questiongroup_id in (46) and institution_id=11604
 and date_of_visit::timestamp BETWEEN to_timestamp('27/08/2018','dd/mm/yyyy') and to_timestamp('29/08/2018','dd/mm/yyyy');
update assessments_answergroup_institution set date_of_visit=Timestamp '2018-11-28' where questiongroup_id in (45,46,47) and institution_id in (24154,24156,24158) and date_of_visit::timestamp BETWEEN to_timestamp('27/11/2019','dd/mm/yyyy') and to_timestamp('29/11/2019','dd/mm/yyyy');
update assessments_answergroup_institution set date_of_visit=Timestamp '2018-11-13' where questiongroup_id in (45) and institution_id=43427
 and date_of_visit::timestamp BETWEEN to_timestamp('11/02/2019','dd/mm/yyyy') and to_timestamp('13/02/2019','dd/mm/yyyy');

update assessments_answergroup_institution set institution_id=10636 where id in (1493673,1493683,1493689,1493690,1493692,1493695,1493698,1493699,1493702,1493704,1493708,1493709);

