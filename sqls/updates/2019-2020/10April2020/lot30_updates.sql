UPDATE boundary_electionboundary SET const_ward_lang_name='ಅಂದೋಲಾ' WHERE id=705;
UPDATE boundary_electionboundary SET const_ward_lang_name='ಕಡಬೂರ' WHERE id=3149;
UPDATE boundary_electionboundary SET const_ward_lang_name='ಆನೂರಕೋಗನೂರ' WHERE id=3674;
UPDATE boundary_electionboundary SET const_ward_lang_name='ರಂಜಣಗಿ' WHERE id=213009039;
UPDATE boundary_electionboundary SET const_ward_lang_name='ಕಾಚಾಪೂರ' WHERE id=213009040;
UPDATE boundary_electionboundary SET const_ward_lang_name='ಸುಂಬಡ' WHERE id=213009041;
UPDATE boundary_electionboundary SET const_ward_lang_name='ಹುಲ್ಲೂರ' WHERE id=213009042;
UPDATE boundary_electionboundary SET const_ward_lang_name='ಮದರಿ' WHERE id=213009043;

-- Map Srinivas Saradagi GP schools to Gulbarga South (479) and not Aland (475)
update schools_institution set admin2_id=479 where gp_id=5504 and admin2_id=475;