update assessments_questiongroupkey set max_score=1 where questiongroup_id in (select id from assessments_questiongroup where survey_id=3);
