UPDATE schools_institution SET gp_id=5655 WHERE id=51370;
UPDATE schools_institution SET gp_id=4591 WHERE id=12914;
UPDATE schools_institution SET gp_id=6313 WHERE id=51950;
UPDATE schools_institution SET village='NADIKERI' where id=51950;
UPDATE schools_institution SET gp_id=4790 WHERE id=50894;

-- Create classes for schools where classes don't exist. Don't enter section
INSERT INTO schools_studentgroup (name, group_type_id, institution_id, status_id)
    VALUES('4', 'class', 293044, 'AC');
INSERT INTO schools_studentgroup (name, group_type_id, institution_id, status_id)
    VALUES('5', 'class', 293044, 'AC');
INSERT INTO schools_studentgroup (name, group_type_id, institution_id, status_id)
    VALUES('6', 'class', 293044, 'AC');
INSERT INTO schools_studentgroup (name, group_type_id, institution_id, status_id)
    VALUES('4', 'class', 293077, 'AC');
INSERT INTO schools_studentgroup (name, group_type_id, institution_id, status_id)
    VALUES('5', 'class', 293077, 'AC');
INSERT INTO schools_studentgroup (name, group_type_id, institution_id, status_id)
    VALUES('6', 'class', 293077, 'AC');
