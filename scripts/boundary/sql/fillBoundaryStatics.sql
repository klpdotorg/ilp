INSERT INTO boundary_boundarytype (char_id, name) VALUES
('C', 'Country'),
('ST', 'State');
INSERT INTO boundary_boundary(id, name, dise_slug,boundary_type_id,status_id) 
VALUES (1, 'India', 'India', 'C','AC');
INSERT INTO boundary_boundary(id,name, dise_slug, parent,boundary_type_id,status_id)
VALUES(2, 'Karnataka', 'Karnataka', 1,'ST', 'AC');