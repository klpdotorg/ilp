--gka class visit survey updates for odisha
delete from assessments_surveyusertypemapping where survey_id=14 and usertype_id in ('CM','EY','GO');

insert into assessments_surveyusertypemapping (survey_id,usertype_id) values (14,'GP');
insert into assessments_surveyusertypemapping (survey_id,usertype_id) values (14,'BRCC');

--gka class visit survey updates for karnataka
delete from assessments_surveyusertypemapping where survey_id=11 and usertype_id in ('CM','EY','GO','ECO','DIET');

--community survey updates for karnataka
delete from assessments_surveyusertypemapping where survey_id=7 and usertype_id in ('EY');

--GKA teacher survey updates for karnataka
delete from assessments_surveyusertypemapping where survey_id=12 and usertype_id in ('ECO','DIET');

--easy english survey updates for karnataka
delete from assessments_surveyusertypemapping where survey_id=16 and usertype_id in ('DIET');

--school readiness program survey updates for karnataka
insert into assessments_surveyusertypemapping (survey_id,usertype_id) values (17,'HM');
