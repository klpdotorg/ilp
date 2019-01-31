--update date_of_visit
update assessments_answergroup_institution set date_of_visit=Timestamp '2018-11-09' where questiongroup_id in (46,47) and institution_id in (36737,36758,36763,42555,42557) and date_of_visit::timestamp BETWEEN to_timestamp('08/10/2018','dd/mm/yyyy') and to_timestamp('12/10/2018','dd/mm/yyyy');
update assessments_answergroup_institution set date_of_visit=Timestamp '2018-11-09' where questiongroup_id in (46) and institution_id in (42616) and date_of_visit::timestamp BETWEEN to_timestamp('10/10/2018','dd/mm/yyyy') and to_timestamp('12/10/2018','dd/mm/yyyy');
