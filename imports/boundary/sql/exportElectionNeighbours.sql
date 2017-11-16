\COPY (SELECT t1.id, t2.neighbours FROM tb_electedrep_master t1 CROSS JOIN LATERAL unnest(string_to_array(t1.neighbours, '|')) AS t2 (neighbours)) TO 'replacefilename' CSV HEADER DELIMITER ',';
