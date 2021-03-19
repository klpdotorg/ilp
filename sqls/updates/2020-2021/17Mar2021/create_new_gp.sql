insert into boundary_electionboundary (const_ward_name, dise_slug, const_ward_type_id, state_id, status_id, const_ward_lang_name) VALUES('aarji','','GP', 2, 'AC', 'ಆರ್ಜಿ');
update schools_institution set gp_id=5729 where id=34262;
update schools_institution set gp_id=213009047 where id=51921;
-- Create new school for Kanaganahally. This was there in 12-13 but vanished in later years
INSERT INTO dise_basicdata(
    school_name,
    district,
    school_code,
    block_name,
    cluster_name,
    academic_year_id,
    state_name) VALUES(
    'GLPS KANAGANA HALLY',
    'MANDYA',
    '29220607402',
    'PANDAVAPURA',
    'CHINAKURALI',
    '1718', 'karnataka');
insert into schools_institution(name,admin0_id,admin1_id, admin2_id, admin3_id,gp_id, village,institution_type_id, category_id, gender_id, management_id, dise_id, status_id)
    values('GLPS Kanagana Hally', 2, 434, 593, 2483, 1635,'kanaganahalli','primary', 13, 'co-ed', 1,630631, 'AC');