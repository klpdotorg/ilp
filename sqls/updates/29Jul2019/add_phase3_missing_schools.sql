insert into schools_institution(name,admin0_id, admin1_id, admin2_id, admin3_id, gp_id,institution_type_id,management_id, dise_id) 
select 'GLPS CHATTENA HALLY', id from boundary_boundary where boundary_type_id='SD' and name='mandya',
id from boundary_boundary where boundary_type_id='SB' and name='nagamangala', id from boundary_boundary
 where boundary_type_id='SC' and name='lalanakere', 'primary', 1, 29220506901;