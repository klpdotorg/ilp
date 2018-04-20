update common_respondenttype set state_code_id='od' where char_id='BRC';
insert into common_respondenttype(char_id,name,state_code_id,active_id) values('BRCNO','BRC Nodal Officer','ka','AC');
update common_respondenttype set active_id='IA' where char_id = 'DIET';
insert into common_respondenttype(char_id,name,active_id) values('SO','State Official','AC');
