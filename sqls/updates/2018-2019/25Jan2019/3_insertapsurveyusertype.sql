insert into assessments_surveyusertypemapping(survey_id, usertype_id)  select 21, x from unnest(ARRAY[ 'CRP', 'MEO', 'BRP', 'BEO', 'DEO', 'DIET_Lec', 'AMO'])x;
