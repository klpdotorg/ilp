--Creating GP for Timmapur
SELECT MAX(id) FROM boundary_electionboundary;
SELECT nextval('boundary_electionboundary_id_seq');
BEGIN;
LOCK TABLE boundary_electionboundary IN EXCLUSIVE MODE;
SELECT setval('boundary_electionboundary_id_seq', COALESCE((SELECT MAX(id)+1 FROM boundary_electionboundary), 1), false);
COMMIT;
insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Timmapur', 'GP',2,'AC', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where admin1_id=420 and admin2_id=501 and gp_id=5776;

--Creating GP for Kalasapura
insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Kalasapura', 'GP',2,'AC', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where admin1_id=429 and admin2_id=564  and gp_id=3247;


--Creating GP for Balaganur
insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Balaganur', 'GP',2,'AC', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where admin1_id=418 and admin2_id=491  and gp_id=952;


insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Balaganur', 'GP',2,'AC', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where admin1_id=420 and admin2_id=501  and gp_id=952;
