\COPY stories_survey(id,created_at, updated_at,name,partner_id) FROM 'stories_survey.csv' with csv NULL 'null';
update stories_questiongroup set survey_id=5 where id in (1,6);
update stories_questiongroup set survey_id=6 where id=2;
update stories_questiongroup set survey_id=1 where id in (3,4,7,9);
update stories_questiongroup set survey_id=3 where id in (5,8,16,17);
update stories_questiongroup set survey_id=4 where id in (10,11,12,13,14,15);
update stories_questiongroup set survey_id=2 where id in (21,22,23);
update stories_questiongroup set survey_id=7 where id in (18,20);
