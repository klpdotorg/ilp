--Correcting gp mapping for Bagewadi gp
update schools_institution set gp_id=6236 where admin1_id=424 and admin2_id=532 and gp_id=926;

--update gp names
update boundary_electionboundary set const_ward_name='Bennuru (sh)' where id=1229;
update boundary_electionboundary set const_ward_name='Bennuru (bg)' where id=6222;

--update GP id by GP present in db
update schools_institution set gp_id=1455 where admin1_id=435 and admin2_id=596 and gp_id=1454;

--Update gp id by GP present in db
update schools_institution set gp_id=2059 where admin1_id=435 and admin2_id=596 and gp_id=2058;

--update gp id with gp present in db
update schools_institution set gp_id=4506 where admin1_id=414 and admin2_id=467 and gp_id=4505;


--Updates after clarification with Srikant and team
-- Both gajendragad north and south are muncipal wards itseems. So they are not Gram Panchayath names.
-- All these schools belong to muncipal wards, so remove the GP association(make gp_id null) for all school under 2024(gajendragad north) & 6200(gajendragad south). and update  const_ward_type_id='MW'  for both id's=2024 & 6200.
update schools_institution set gp_id=null where gp_id in (2024,6200);
update boundary_electionboundary set const_ward_type_id='MW' where id in (2024,6200);

--Updating gp id for schools in dharwad    | 421 | kundagol  | 505 | urdu kundagol  
update boundary_electionboundary set const_ward_name='Ingalagi (dwd)' where id=6195;
update schools_institution set gp_id=6195 where id in (37619,37618);

--Updating gp id to null as Schools belong to muncipal ward
update schools_institution set gp_id=null where gp_id =3762;
--All these schools belong to wards
update schools_institution set gp_id=null where id in (44393,44391,44394);  
update boundary_electionboundary set const_ward_type_id='MW' where id =3762;

--Updating gp of a wrongly mapped school
update schools_institution set gp_id=4941 where id in (48078);
update schools_institution set gp_id=4942 where id in (6856,6862);
