--delete duplicate assessment
delete from assessments_answerinstitution where answergroup_id in (1389071,1389072,1389073,1389074,1389075,1389076,1389077,1389078,1389079,1389080,1389081,1389082,1389083,1389084,1389085,1389086,1389087,1389088,1389089,1389090,1389091,1389092,1389093,1389094);
delete from assessments_answergroup_institution where id in (1389071,1389072,1389073,1389074,1389075,1389076,1389077,1389078,1389079,1389080,1389081,1389082,1389083,1389084,1389085,1389086,1389087,1389088,1389089,1389090,1389091,1389092,1389093,1389094);