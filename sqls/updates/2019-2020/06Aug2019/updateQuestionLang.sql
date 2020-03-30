update assessments_question set lang_name=replace(lang_name, '-', ',') where id in (select question_id from assessments_questiongroup_questions where questiongroup_id in (62,63,64));
