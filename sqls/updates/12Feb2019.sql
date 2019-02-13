--delete invalid assessment
delete from assessments_answerinstitution where answergroup_id in (1432520,1432514,1432513,1471868,1471869,1471870,1471871);
delete from assessments_answergroup_institution where id in (1432520,1432514,1432513,1471868,1471869,1471870,1471871);

--update schools_institution
update schools_institution set gp_id=3798 where id in (43470,43465);
update schools_institution set gp_id=2644 where id in (10884);
update schools_institution set gp_id=5373 where id in (37655,37657,37656);

--update date_of_visit
update assessments_answergroup_institution set date_of_visit=Timestamp '2019-01-25' where questiongroup_id in (47) and institution_id in (37655,37656,37657) and date_of_visit::timestamp BETWEEN to_timestamp('24/12/2018','dd/mm/yyyy') and to_timestamp('26/12/2018','dd/mm/yyyy');
update assessments_answergroup_institution set date_of_visit=Timestamp '2019-01-06' where questiongroup_id in (45) and institution_id in (11267) and date_of_visit::timestamp BETWEEN to_timestamp('05/12/2018','dd/mm/yyyy') and to_timestamp('07/12/2018','dd/mm/yyyy');
