update assessments_question set question_text='Is the teacher of Nali-Kali is conducting the class ?' where id=639;
update assessments_question set question_text='Is the teacher trained by Akshara Foundation ?' where id=640;
update assessments_question set question_text='Is the teacher carrying out the expected day’s timetable ?' where id=641;
update assessments_question set question_text='Is the teacher following the activity schedule for that day ?' where id=642;
update assessments_question set question_text='Is the teacher using the TLM provided ?' where id=643;
update assessments_question set question_text='Are the children using the TLM applicable ?' where id=644;
update assessments_question set question_text='Which lesson was being taught in the class during your visit ?' where id=645;
update assessments_question set question_text='Are Children’s work books up to date ?' where id=646;
update assessments_question set question_text='Are the activity books corrected by the teacher up to date ?' where id=647;
update assessments_question set question_text='Is the child tracker completed ?' where id=648;

update assessments_question set question_type=1 where id in (642,643,644,645);
