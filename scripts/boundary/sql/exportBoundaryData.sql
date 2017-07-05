COPY(SELECT boundary.id, boundary.name, 
    CASE 
        WHEN boundary.dise_slug IS NULL THEN 'Default' 
        WHEN boundary.dise_slug IS NOT NULL THEN boundary.dise_slug
    END AS dise_slug, 
    coord.coord, 
    CASE 
        WHEN boundary.hid=11 THEN 'SC' 
        WHEN boundary.hid=10 THEN 'SB' 
        WHEN boundary.hid=9 THEN 'SD' 
        WHEN boundary.hid=13 THEN 'PD' 
        WHEN boundary.hid=14 THEN 'PP' 
        WHEN boundary.hid=15 THEN 'PC' 
    END as boundary_type, 
    CASE
        WHEN boundary.parent IS NULL THEN 2
        WHEN boundary.parent=1 THEN 2
        WHEN boundary.parent IS NOT NULL THEN boundary.parent
    END AS parent, 
    CASE 
        WHEN status=2 THEN 'AC' 
        WHEN status=1 THEN 'IA' 
        WHEN status=0 THEN 'DL' 
    END as status, 
    CASE 
        WHEN boundary.type=1 THEN 'primary' 
        WHEN boundary.type=2 THEN 'pre' 
    END  as inst_type
    FROM tb_boundary boundary LEFT JOIN mvw_boundary_coord coord 
    ON boundary.id=coord.id_bndry WHERE boundary.status=2) TO '/Users/Subha/boundaries.csv' CSV HEADER DELIMITER ',';

