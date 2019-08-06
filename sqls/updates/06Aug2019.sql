--Updating date of visit for household survey batch 30 from 12/2019 to 12/2018
update assessments_answergroup_institution set date_of_visit='2018-12-29'::timestamp where date_of_visit::date ='2019-12-29' and questiongroup_id=20;
--Updating date of visit for household survey batch 30 from 08/2019 to 07/01/2019
update assessments_answergroup_institution set date_of_visit='2019-01-07'::timestamp where date_of_visit::date ='2019-08-03' and questiongroup_id=20;
