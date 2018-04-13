update common_respondenttype set name='NGO' where char_id='CM';
update common_respondenttype set name='GP Member' where char_id='ER';
update common_respondenttype set state='ka' where char_id='BRC';
update common_respondenttype set name='DIET Official' where char_id='DIET';
update common_respondenttype set name='DDPI/DyPc/ECO' where char_id='DDPI';
insert into common_respondenttype(char_id,name,state,active_id) values('NOD', 'GKA Nodal Officer', 'ka','AC');
