-- Update to be run for Manday North and Manday South language names (blocks)
-- Mandya North
UPDATE boundary_boundary set lang_name='ಮಂಡ್ಯ ಉತ್ತರ' where id=595;
-- Mandya South
UPDATE boundary_boundary set lang_name='ಮಂಡ್ಯ ದಕ್ಷಿಣ' where id=591;
--chikmagalur block has messed up Kannada name. Fix that
UPDATE boundary_boundary set lang_name='ಚಿಕ್ಕಮಗಳೂರು' where id=564;