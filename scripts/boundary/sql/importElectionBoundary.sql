\set filename :inputdir '/electionboundary.csv'
\set electboundneighbours :inputdir '/electboundneighbours.csv'
COPY boundary_electionboundary(id,dise_slug,elec_comm_code,const_ward_name,const_ward_type_id,
current_elected_rep,
current_elected_party_id,state_id,status_id) FROM 
:'filename' DELIMITER ',' CSV HEADER;

COPY boundary_electionneighbours(elect_boundary_id,neighbour_id) FROM :'electboundneighbours' DELIMITER ',' CSV HEADER;