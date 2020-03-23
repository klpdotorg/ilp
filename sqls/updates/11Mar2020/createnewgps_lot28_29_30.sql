--Creating GP for Kotabagi 
SELECT MAX(id) FROM boundary_electionboundary;
SELECT nextval('boundary_electionboundary_id_seq');
BEGIN;
LOCK TABLE boundary_electionboundary IN EXCLUSIVE MODE;
SELECT setval('boundary_electionboundary_id_seq', COALESCE((SELECT MAX(id)+1 FROM boundary_electionboundary), 1), false);
COMMIT;

insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Kallahangarga', 'GP',2,'AC', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where id in (14717,14883,14793,38335);

insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Ranjanagi', 'GP',2,'AC', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where id in (14675,14681,14691,14786,14773,14774,14785);

insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Kachapur', 'GP',2,'AC', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where id in (14761);

insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Sumbad', 'GP',2,'AC', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where id in (14805,14637,14812);

insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Hullur', 'GP',2,'AC', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where id in (14660,14661,14668);

insert into boundary_electionboundary(const_ward_name, const_ward_type_id, state_id, status_id, dise_slug) values('Madari', 'GP',2,'AC', '');
update schools_institution set gp_id=(select currval('boundary_electionboundary_id_seq')) where id in (14832,14829,14838,14830);


