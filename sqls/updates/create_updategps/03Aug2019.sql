--Creating GP for Kudluru
SELECT MAX(id) FROM boundary_electionboundary;
SELECT nextval('boundary_electionboundary_id_seq');
BEGIN;
LOCK TABLE boundary_electionboundary IN EXCLUSIVE MODE;
SELECT setval('boundary_electionboundary_id_seq', COALESCE((SELECT MAX(id)+1 FROM boundary_electionboundary), 1), false);
COMMIT;

insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Kudluru', 'GP',2,'AC', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where admin1_id=444 and admin2_id=652 and gp_id=3838;

--Creating GP for Ingalagi
insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Ingalagi', 'GP',2,'AC', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where admin1_id=414 and admin2_id=467 and gp_id=2953;

insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Ingalagi', 'GP',2,'AC', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where admin1_id=415 and admin2_id=470 and gp_id=2953;

insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Ingalagi', 'GP',2,'AC', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where admin1_id=416 and admin2_id=478 and gp_id=2953;

update schools_institution set gp_id=2953 where id=37580;
