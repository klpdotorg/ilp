SELECT MAX(id) FROM boundary_electionboundary;
SELECT nextval('boundary_electionboundary_id_seq');
BEGIN;
LOCK TABLE boundary_electionboundary IN EXCLUSIVE MODE;
SELECT setval('boundary_electionboundary_id_seq', COALESCE((SELECT MAX(id)+1 FROM boundary_electionboundary), 1), false);
COMMIT;
insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug, const_ward_lang_name) values('Hagaraga', 'GP',2,'AC','', 'ಹಗ್ಗರಗಾ');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where id in (14457,38391,14452,14456,14534);

insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug, const_ward_lang_name) values('Nedalgi', 'GP',2,'AC','', 'ನೀಡಲಗಿ');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where id in (14657,14669,14666);

insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug, const_ward_lang_name) values('Kakanur', 'GP',2,'AC','', 'ಕಾಕನೂರ್');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where id in (30049,14736,14735);
