UPDATE boundary_electionboundary SET const_ward_lang_name='ಬೆಳಗಲಿ' where id=950;
-- update for schools to map to Kittur block
update schools_institution SET admin2_id=23387 WHERE admin1_id=413 and admin3_id IN (662,663,9762,9761,9763,9756,658);