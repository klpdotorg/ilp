INSERT INTO boundary_boundary (name,lang_name,dise_slug, status_id,type_id, boundary_type_id, parent_id) VALUES('kittur','ಕಿತ್ತೂರು','belagavi-kittur', 'AC','primary','SB', 413);

-- UPDATE kittur cluster existing to kittur block instead of bailhongal
UPDATE boundary_boundary SET dise_slug='kittur-ambadgatti', parent_id=28387 WHERE id=658; 
UPDATE boundary_boundary SET dise_slug='kittur-bailur', parent_id=28387 WHERE id=9756; 
UPDATE boundary_boundary SET dise_slug='kittur-kulavalli', parent_id=28387 WHERE id=9763; 
UPDATE boundary_boundary SET dise_slug='kittur-hosa-kadarvalli', parent_id=28387 WHERE id=9761; 
UPDATE boundary_boundary SET dise_slug='kittur-kalbhavi', parent_id=28387 WHERE id=9762; 
UPDATE boundary_boundary SET dise_slug='kittur-m.k.hubli', parent_id=28387 WHERE id=663; 
UPDATE boundary_boundary SET dise_slug='kittur-kittur', parent_id=28387 WHERE id=662; 


