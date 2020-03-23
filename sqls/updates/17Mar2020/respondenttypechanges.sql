update common_respondenttype set name='SSA Nodal' where char_id='SSAN';
update common_respondenttype set name='Education Volunteer' where char_id='EV';
update common_respondenttype set name='Executive officer' where char_id='EO';
update common_respondenttype set name='Chief Executive Officer' where char_id='CEO';
update common_respondenttype set name='DIET Senior Lecturer' where char_id='DIETSL';
update common_respondenttype set name='Education coordinator' where char_id='ECO';
insert into assessments_surveyusertypemapping(usertype_id,survey_id) values('EO',11);
