--assign temp questions
update assessments_answerinstitution set question_id=50 where question_id=271 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=51 where question_id=272 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));

--start swapping
update assessments_answerinstitution set question_id=271 where question_id=273 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=272 where question_id=274 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=273 where question_id=276 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=274 where question_id=277 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=276 where question_id=278 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=277 where question_id=279 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=278 where question_id=280 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=279 where question_id=281 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=280 where question_id=282 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=281 where question_id=283 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=282 where question_id=284 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=283 where question_id=292 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=284 where question_id=286 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=292 where question_id=287 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=286 where question_id=293 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=287 where question_id=294 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=293 where question_id=295 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=294 where question_id=288 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=295 where question_id=130 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=288 where question_id=291 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));

--update temp questions
update assessments_answerinstitution set question_id=130 where question_id=50 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
update assessments_answerinstitution set question_id=291 where question_id=51 and answergroup_id in (select id from assessments_answergroup_institution where questiongroup_id=22 and to_char(date_of_visit, 'YYYY-MM') in ('2018-06', '2018-07', '2018-08'));
