-- Create new school for IGRS Mangalore
INSERT INTO dise_basicdata(
    school_name,
    district,
    school_code,
    block_name,
    cluster_name,
    academic_year_id,
    state_name) VALUES(
    'IGRS Mangalore',
    'KOPPAL',
    '29070909118',
    'YELBURGA',
    'MANGALORE',
    '1718', 'karnataka');
insert into schools_institution(name,admin0_id,admin1_id, admin2_id, admin3_id,gp_id, institution_type_id, category_id, gender_id, management_id, dise_id, status_id)
    values('IGRS Mangalore', 2, 419, 495, 1170, 4244,'primary', 13, 'co-ed', 1,630632, 'AC');