update assessments_questiongroup set image_required =true where id=40;
update assessments_questiongroup set image_required =true where id=42;
update assessments_question set question_text='If you have any questions regarding the GKA kit teaching methodology, whom do you ask your questions?' where id in (604,606);
update assessments_question set lang_name='ಜಿಕೆಎ ಕಿಟ್ ಬಗ್ಗೆ ಅಥವಾ ಬೋಧನಾ ವಿಧಾನದ ಬಗ್ಗೆ ನಿಮಗೆ ಯಾವುದೇ ಪ್ರಶ್ನೆಗಳು ಇದ್ದಲ್ಲಿ, ನೀವು ಯಾರಿಗೆ ನಿಮ್ಮ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳುತ್ತೀರಿ?' where id=604;
update assessments_question set display_text='' where id in (604,606);
update assessments_question set lang_options='{ಸಿ ಆರ್ ಪಿ,ಬಿ ಆರ್ ಪಿ,ಮುಖ್ಯೋಪಾಧ್ಯಾಯ,ಡಯಟ್,ಅಕ್ಷರ ಶಿಬ್ಬಂದಿ,ಬೇರೆ ಶಿಕ್ಷಕರು }' where id in (604);

update assessments_question set question_text='Did you participate in ''Samudaya Datta Shaale'' last time?' where id in (270);

update assessments_question set display_text='How many responses indicate that the respondent has participated in ''Samudaya Datta Shaale'' last time it was held?' where id in (270);

update assessments_question set display_text='How many responses indicate that the school has been visited last month?' where id in (143);

update assessments_question set is_featured =true where id in (select question_id from assessments_questiongroup_questions where questiongroup_id in (select id from assessments_questiongroup where survey_id =7));

