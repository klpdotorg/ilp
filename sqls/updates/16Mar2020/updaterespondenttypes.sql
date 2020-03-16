insert into common_respondenttype(char_id, name, state_code_id, active_id) values('DDPIA','DDPI Admin','ka','AC');
insert into common_respondenttype(char_id, name, state_code_id, active_id) values('DDPID','DDPI Devoplment / DIET Principal','ka','AC');
insert into common_respondenttype(char_id, name, state_code_id, active_id) values('PDO','Panchayat Development Officer','ka','AC');
insert into common_respondenttype(char_id, name, state_code_id, active_id) values('GPL','GP Leader','ka','AC');
insert into common_respondenttype(char_id, name, state_code_id, active_id) values('ZPP','Zilla Panchayat President','ka','AC');
insert into common_respondenttype(char_id, name, state_code_id, active_id) values('CEO','Chief exicutive officer','ka','AC');
insert into common_respondenttype(char_id, name, state_code_id, active_id) values('TPP','Taluk Panchayat President','ka','AC');
insert into common_respondenttype(char_id, name, active_id) values('EV','Eduction Volunteer','AC');


update common_respondenttype set active_id='AC', name='Education co-ordinator' where char_id='ECO';
update common_respondenttype set active_id='AC',state_code_id='ka',name='Education officer' where char_id='EO';


update common_respondenttype set active_id='IA' where char_id='DDPI';

update assessments_answergroup_institution set respondent_type_id='DDPIA' where respondent_type_id='DDPI';
update assessments_surveyusertypemapping set usertype_id='DDPIA' where usertype_id='DDPI';
update users_user set user_type_id='DDPIA' where user_type_id='DDPI';

update assessments_answergroup_institution set respondent_type_id='EV' where respondent_type_id='VR';
update assessments_answergroup_student set respondent_type_id='EV' where respondent_type_id='VR';
update assessments_surveyusertypemapping set usertype_id='EV' where usertype_id='VR';
update users_user set user_type_id='EV' where user_type_id='VR';
delete from common_respondenttype where char_id='VR';

insert into assessments_surveyusertypemapping(survey_id,usertype_id) values(11,'DDPID'), (11,'PDO'), (11,'GPL'), (11,'ZPP'), (11,'CEO'), (11,'TPP');

delete from assessments_surveyusertypemapping where survey_id=11 and usertype_id='BRC';
