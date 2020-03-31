--adding option 'Not Applicable' to easy english survey questions
update assessments_question set options='{Conversation,Rhymes,Grammer,Phonics,Reading,Writing,Assessment,Not Applicable}' where id=609;
update assessments_question set options='{Tab,Flash cards,Teacher-made TLM,Not Applicable}' where id=610;
update assessments_question set options='{Reading,Writing,Speaking in english,Singing rhymes with action,Listening Component,Not Applicable}' where id=611;
update assessments_question set options='{Lesson 1,Lesson 2,Lesson 3,Lesson 4,Lesson 5,Lesson 6,Lesson 7,Not Applicable}' where id=612;
