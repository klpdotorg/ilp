--assessments_survey

update assessments_survey set lang_name='ಸಮುದಾಯ' where id=1;
update assessments_survey set lang_name='ಗ್ರಾಮ ಪಂಚಾಯತಿ  ಸ್ಪರ್ಧೆ' where id=2;
update assessments_survey set lang_name='ಗಣಿತ ಕಲಿಕಾ ಆಂದೋಲನ' where id=3;
update assessments_survey set lang_name='ಅಂಗನವಾಡಿ ಮೂಲಸೌಕರ್ಯ' where id=4;
update assessments_survey set lang_name='ಶೇರ್ ಯೂಅರ್ ಸ್ಟೋರೀ' where id=5;
update assessments_survey set lang_name='ಸಮುದಾಯ-ಐವಿಆರ್ ಎಸ್' where id=6;
update assessments_survey set lang_name='ಸಮುದಾಯ ಸರ್ವೆ' where id=7;
update assessments_survey set lang_name='ಜಿಕೆಎ ಮಾನಿಟರಿಂಗ್' where id=11;

--assessments_questiongroup

update assessments_questiongroup set lang_name='ಜಿಕೆಎ ಎಸ್ ಎಮ್ ಎಸ್ ಮಾನಿಟರಿಂಗ್' where id=17;
update assessments_questiongroup set lang_name='ಐ ಎಲ್ ಪಿ ಕನೆಕ್ಟ್ ಮೊಬೈಲ್' where id=18;
update assessments_questiongroup set lang_name='ಐ ಎಲ್ ಪಿ ಕನೆಕ್ಟ್  ಪೇಪರ್' where id=20;
update assessments_questiongroup set lang_name='ಜಿಕೆಎ ಕನೆಕ್ಟ್ ಮಾನಿಟರಿಂಗ್' where id=24;

--assessments_question for question_group=18

update assessments_question set lang_name='ಶಾಲೆಯಲ್ಲಿ ಬಳಸಲು ಯೋಗ್ಯ ಪ್ರತ್ಯೇಕ ಹುಡುಗಿಯರ ಶೌಚಾಲಯವಿದೆಯೇ?' where id=138;
update assessments_question set lang_options='{ಹೌದು,ಇಲ್ಲ,ಗೊತ್ತಿಲ್ಲ}' where id=138;
update assessments_question set lang_name='ಕಳೆದ ತಿಂಗಳಲ್ಲಿ ನಿಮ್ಮ ಮಗುವಿನ ಶಾಲೆಗೆ ಭೇಟಿ ನೀಡಿದ್ದೀರಾ?' where id=143;
update assessments_question set lang_options='{ಹೌದು,ಇಲ್ಲ,ಗೊತ್ತಿಲ್ಲ}' where id=143;
update assessments_question set lang_name='ಶಾಲೆಯಲ್ಲಿ ಮಧ್ಯಾಹ್ನದ ಊಟದ ಬಗ್ಗೆ ನಿಮಗೆ ತೃಪ್ತಿ ಇದೆಯೇ?' where id=144;
update assessments_question set lang_options='{ಹೌದು,ಇಲ್ಲ,ಗೊತ್ತಿಲ್ಲ}' where id=144;
update assessments_question set lang_name='ಶಾಲೆಯಲ್ಲಿ ಶಿಕ್ಷಕರ ಕೊರತೆ ಇದೆಯೇ?' where id=145;
update assessments_question set lang_options='{ಹೌದು,ಇಲ್ಲ,ಗೊತ್ತಿಲ್ಲ}' where id=145;
update assessments_question set lang_name='ನಿಮ್ಮ ಮಗು ಕನ್ನಡ ಓದುತ್ತಾಳೆ/ನೆ ಅನ್ನಿಸುತ್ತದೆಯೇ?' where id=147;
update assessments_question set lang_options='{ಹೌದು,ಇಲ್ಲ,ಗೊತ್ತಿಲ್ಲ}' where id=147;
update assessments_question set lang_name='ನಿಮ್ಮ ಮಗು ಇಂಗ್ಲೀಷ್ ಓದುತ್ತಾಳೆ/ನೆ ಅನ್ನಿಸುತ್ತದೆಯೇ?' where id=148;
update assessments_question set lang_options='{ಹೌದು,ಇಲ್ಲ,ಗೊತ್ತಿಲ್ಲ}' where id=148;
update assessments_question set lang_name='ನಿಮ್ಮ ಮಗು ಕೂಡುವ ಲೆಕ್ಕ ಮಾಡುತ್ತಾಳೆ/ನೆ ಅನ್ನಿಸುತ್ತದೆಯೇ?' where id=149;
update assessments_question set lang_options='{ಹೌದು,ಇಲ್ಲ,ಗೊತ್ತಿಲ್ಲ}' where id=149;
update assessments_question set lang_name='ನಿಮ್ಮ ಮಗು ಕಳೆಯುವ ಲೆಕ್ಕ ಮಾಡುತ್ತಾಳೆ/ನೆ ಅನ್ನಿಸುತ್ತದೆಯೇ?' where id=150;
update assessments_question set lang_options='{ಹೌದು,ಇಲ್ಲ,ಗೊತ್ತಿಲ್ಲ}' where id=150;
update assessments_question set lang_name='ಎಸ್.ಡಿ.ಎಮ್.ಸಿ ಪ್ರತಿ ತಿಂಗಳು ಸಭೆ ಸೇರುತ್ತದೆಯೇ?' where id=269;
update assessments_question set lang_options='{ಹೌದು,ಇಲ್ಲ,ಗೊತ್ತಿಲ್ಲ}' where id=269;
update assessments_question set lang_name='ಕಳೆದ ಬಾರಿಯ ಸಮುದಾಯದತ್ತ ಶಾಲಾ ಕಾರ್ಯಕ್ರಮದಲ್ಲಿ ನೀವು ಭಾಗವಹಿಸಿದ್ದೀರಾ?' where id=270;
update assessments_question set lang_options='{ಹೌದು,ಇಲ್ಲ,ಗೊತ್ತಿಲ್ಲ}' where id=270;

--assessments_question for question_group=24

update assessments_question set lang_name='ನಿಮ್ಮ ಶಾಲಾ ಭೇಟಿಯ ಸಮಯದಲ್ಲಿ ಗಣಿತ ತರಗತಿಯಲ್ಲಿ ಗುಂಪು ಕಲಿಕೆ ಆಗುತ್ತಿತ್ತೇ?' where id=300;
update assessments_question set lang_options='{ಹೌದು,ಇಲ್ಲ,ಗೊತ್ತಿಲ್ಲ}' where id=300;
update assessments_question set lang_name='ನೀವು ವೀಕ್ಷಿಸಿದ ಗಣಿತ ತರಗತಿಯಲ್ಲಿ ಗಣಿತ ಕಲಿಕಾ ಆಂದೋಲನದ ಕಲಿಕೋಪಕಾರಗಳನ್ನು ಬಳಸುತ್ತಿದ್ದರೆ?' where id=301;
update assessments_question set lang_options='{ಹೌದು,ಇಲ್ಲ,ಗೊತ್ತಿಲ್ಲ}' where id=301;
update assessments_question set lang_name='ನೀವು ವೀಕ್ಷಿಸಿದ ತರಗತಿಯಲ್ಲಿ ಗಣಿತ ಪಾಠ ನಡೆಯುತ್ತಿತ್ತೆ?' where id=302;
update assessments_question set lang_options='{ಹೌದು,ಇಲ್ಲ,ಗೊತ್ತಿಲ್ಲ}' where id=302;
update assessments_question set lang_name='ನೀವು ಭೇಟಿ ನೀಡಿದ ಶಾಲೆಯಲ್ಲಿ 4 ನೇ ಮತ್ತು 5 ನೇ ತರಗತಿಯ ಶಿಕ್ಷಕರಿಗೆ ಗಣಿತ ಕಲಿಕಾ ಆಂದೋಲನದ ತರಬೇತಿಯಾಗಿದೆಯೇ?' where id=303;
update assessments_question set lang_options='{ಹೌದು,ಇಲ್ಲ,ಗೊತ್ತಿಲ್ಲ}' where id=303;

