--correcting invalid klp_id for gp contest data
update assessments_answergroup_institution set institution_id=20425 where institution_id in (select id from schools_institution where gp_id =3421 and admin1_id=414) and questiongroup_id in (21,22,23,45,46,47) ;

--updating GKA Class Visit survey question
update assessments_question set lang_name='ನೀವು ಭೇಟಿ ನೀಡಿದ ತರಗತಿಯ ಗಣಿತ ಶಿಕ್ಷಕ/ಶಿಕ್ಷಕಿಯರಿಗೆ ಜಿ ಕೆ ಏ ತರಬೇತಿ ಆಗಿದೆಯೇ?' where id=599;
