insert into common_respondenttype(char_id,name,state_code_id,active_id) values('DyPc','DyPc','ka','AC');
insert into common_respondenttype(char_id,name,state_code_id,active_id) values('DIETSL','DIET Senior Lecturer','ka','AC');
insert into common_respondenttype(char_id,name,state_code_id,active_id) values('DIETL','DIET Lecturer','ka','AC');
insert into common_respondenttype(char_id,name,state_code_id,active_id) values('DSERTN','DSERT Nodal','ka','AC');
insert into common_respondenttype(char_id,name,state_code_id,active_id) values('DSERTD','DSERT Director','ka','AC');
insert into common_respondenttype(char_id,name,state_code_id,active_id) values('SSAN','SSA Nodel','ka','AC');
insert into common_respondenttype(char_id,name,state_code_id,active_id) values('SSAD','SSA Director','ka','AC');
insert into common_respondenttype(char_id,name,state_code_id,active_id) values('GPP','GP President','ka','AC');


insert into assessments_surveyusertypemapping(survey_id,usertype_id) SELECT 11 id, x FROM unnest(ARRAY['DyPc','ECO','DIETSL','DIETL','DSERTN','DSERTD','SSAN','SSAD','GPP']) x;
