--Creating 2 gps with same name Agara
SELECT MAX(id) FROM boundary_electionboundary;
SELECT nextval('boundary_electionboundary_id_seq');
BEGIN;
LOCK TABLE boundary_electionboundary IN EXCLUSIVE MODE;
SELECT setval('boundary_electionboundary_id_seq', COALESCE((SELECT MAX(id)+1 FROM boundary_electionboundary), 1), false);
COMMIT;
insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Agara', 'GP',2,'AC', 'agara');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where admin1_id=9541 and admin2_id=8879;
insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Agara', 'GP',2,'AC', 'agara');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where admin1_id=431 and admin2_id=576;
