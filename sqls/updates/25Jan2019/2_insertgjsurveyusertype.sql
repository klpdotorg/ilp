insert into assessments_surveyusertypemapping(survey_id, usertype_id)  select 22, x from unnest(ARRAY['CRP', 'DEO', 'BEO', 'BRP', 'DIET_Lec'])x
