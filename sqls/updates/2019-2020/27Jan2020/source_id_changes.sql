-- Update to modify source ID for Konnect gka class visit question groups
UPDATE assessments_questiongroup SET source_id = 4 WHERE id IN (40,42);