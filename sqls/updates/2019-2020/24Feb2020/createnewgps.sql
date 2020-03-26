--Creating GP for Kotabagi 
SELECT MAX(id) FROM boundary_electionboundary;
SELECT nextval('boundary_electionboundary_id_seq');
BEGIN;
LOCK TABLE boundary_electionboundary IN EXCLUSIVE MODE;
SELECT setval('boundary_electionboundary_id_seq', COALESCE((SELECT MAX(id)+1 FROM boundary_electionboundary), 1), false);
COMMIT;

insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Cherambane', 'GP',2,'AC', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where id in (51623,51625,51620,51626,51624);

insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Mustur', 'GP',2,'AC', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where id in (19784	,19778,19779);



insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug,const_ward_lang_name) values('Kalakera', 'GP',2,'AC', '','ಕಲಕೇರಾ');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where id in (20040,19946,20049,20036);


insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug,const_ward_lang_name) values('Halavarthi', 'GP' ,2, 'AC', '', 'ಹಾಲವರ್ತಿ');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where id in (20012,20020,20006,20022,20023);

insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug,const_ward_lang_name) values('Vanaballari', 'GP' ,2, 'AC', '', 'ವಣಬಳ್ಳಾರಿ');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where id in (20112);


insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug,const_ward_lang_name) values('Bevinahalli', 'GP' ,2, 'AC', '', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where id in (19972,33464,20110);
