--Creating GP for Kotabagi 
SELECT MAX(id) FROM boundary_electionboundary;
SELECT nextval('boundary_electionboundary_id_seq');
BEGIN;
LOCK TABLE boundary_electionboundary IN EXCLUSIVE MODE;
SELECT setval('boundary_electionboundary_id_seq', COALESCE((SELECT MAX(id)+1 FROM boundary_electionboundary), 1), false);
COMMIT;

insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Hulihyadar', 'GP',2,'AC', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where id in (19873,19876,19877,19674,37975,19871,19872,19879);
