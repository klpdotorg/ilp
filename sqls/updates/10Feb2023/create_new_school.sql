-- Create new school for GLPS HUNASEGHATTE PALYA
INSERT INTO dise_basicdata(id,
    school_name,
    district,
    school_code,
    block_name,
    cluster_name,
    academic_year_id,
    state_name) VALUES(
    630633,
    'GLPS HUNASEGHATTE PALYA',
    'BENGALURU RURAL',
    '29210119502',
    'NELAMANGALA',
    'SOLADEVANAHALLI',
    '1718', 'karnataka');
insert into schools_institution(id,name,admin0_id,admin1_id, admin2_id, admin3_id,gp_id, institution_type_id, category_id, gender_id, management_id, dise_id, status_id)
    values(293098,'GLPS HUNASEGHATTE PALYA', 2, 433, 584, 9944, 5448,'primary', 13, 'co-ed', 1,630633, 'AC');