\set filename :inputdir '/boundaries.csv'
COPY boundary_boundary(id,name,dise_slug,geom,boundary_type_id,parent_id,status_id,type_id) FROM 
:'filename' DELIMITER ',' CSV HEADER;