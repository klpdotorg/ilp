from os import sys
import psycopg2
import datetime

if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: " +
          "python import_gkaassessmentdata.py dubdubdub ilp")
    sys.exit()

fromdatabase = sys.argv[1]

todatabase = sys.argv[2]

basename = "gkaassessment"
inputsqlfile = basename+"_getdata.sql"
loadsqlfile = basename+"_loaddata.sql"

fromconnectionstring = "dbname=%s user=klp" % fromdatabase
fromconn = psycopg2.connect(fromconnectionstring)
fromcursor = fromconn.cursor()

toconnectionstring = "dbname=%s user=klp" % todatabase
toconn = psycopg2.connect(toconnectionstring)
tocursor = toconn.cursor()

question_featured = True
question_type = 4
questiongroup = {'do_30048087': {'text': 'Class 4 and 5', 'year': '1617',
                                 'start_date': '06-01-2016', 'end_date': '04-30-2017',
                                 'status': 'IA', 'options': '{0,1,2,3,4,5}'},
                 'do_30093116': {'text': 'Class 4', 'year': '1617',
                                 'start_date': '06-01-2016', 'end_date': '04-30-2017',
                                 'status': 'IA', 'options': '{0,1,2,3,4,5}'},
                 'do_30097179': {'text': 'Class 5', 'year': '1617',
                                 'start_date': '06-01-2016', 'end_date': '04-30-2017',
                                 'status': 'IA', 'options': '{0,1}'},
                 'do_31228112328675328021100': {'text': 'Class 4', 'year': '1718',
                                                'start_date': '06-01-2017',
                                                'end_date': '04-30-2018',
                                                'status': 'AC', 'options': '{0,1}'},
                 'do_31228116672723353621122': {'text': 'Class 5', 'year': '1718',
                                                'start_date': '06-01-2017',
                                                'end_date': '04-30-2018',
                                                'status': 'AC', 'options': '{0,1}'}}


sqlselect = "select stu.student_id, assess.question_id, assess.ekstep_tag, assess.score, assess.assessed_ts from assessments_v2 assess, students_v2 stu where assess.student_uid=stu.uid and assess.ekstep_tag in %s and not exists (select * from assessments_v2  as dup where dup.student_uid=assess.student_uid and dup.question_id=assess.question_id and dup.assessed_ts::date=assess.assessed_ts::date and dup.ekstep_tag=assess.ekstep_tag and dup.assessed_ts > assess.assessed_ts);"
data = ('do_31228112328675328021100', 'do_31228116672723353621122')
fromcursor.execute(sqlselect, (data,))

for row in fromcursor.fetchall():
    student_id = row[0]
    question_text = row[1]
    questiongroup_name = row[2]
    score = row[3]
    timestamp = row[4]
    dateofvisit = datetime.datetime.date(row[4])
    # check student valid
    sqlselect = "select exists(select 1 from schools_student where id=%s);"
    tocursor.execute(sqlselect, [student_id])
    if not tocursor.fetchall()[0][0]:
        print('student id not present :'+student_id)
        continue

    # Check if questiongroup is present
    sqlselect = "select id from assessments_questiongroup where name=%s;"
    tocursor.execute(sqlselect, [questiongroup_name])
    if tocursor.rowcount == 0:
        print('questiongroup is not present :'+questiongroup_name)
        continue
    else:
        questiongroup_id = tocursor.fetchall()[0]

    # Check if question is present
    sqlselect = "select id from assessments_question where question_text=%s;"
    tocursor.execute(sqlselect, [question_text])
    if tocursor.rowcount == 0:
        print('question is not present :'+question_text)
        continue
    else:
        question_id = tocursor.fetchall()[0]

    # check if answergroup is present
    sqlselect = "select id, date_of_visit from assessments_answergroup_student where student_id=%s and questiongroup_id=%s and date_of_visit::date=%s;"
    tocursor.execute(sqlselect, (student_id, questiongroup_id, dateofvisit))
    data = tocursor.fetchall()
    answergroup_present = tocursor.rowcount
    if answergroup_present != 0:
        answergroup_present = 0
        for row in data:
            answergroup_id = row[0]
            enteredtimestamp = row[1]
            if datetime.datetime.date(enteredtimestamp) == dateofvisit:
                answergroup_present = 1
                continue

    if answergroup_present == 0:
        sqlinsert = "insert into assessments_answergroup_student(double_entry, date_of_visit, is_verified, questiongroup_id, status_id, student_id) values (%s, %s, %s, %s, %s, %s) returning id;"
        tocursor.execute(sqlinsert, (0, timestamp, 'true', questiongroup_id, 'AC',
                         student_id))
        answergroup_id = tocursor.fetchone()[0]

    if answergroup_present == 1:
        # Check for duplicate answer
        sqlselect = "select id,answer from assessments_answerstudent where answergroup_id=%s and question_id=%s;"
        tocursor.execute(sqlselect, (answergroup_id, question_id,))
        answer_present = tocursor.rowcount
        if answer_present > 0:
            data = tocursor.fetchall()[0]
            answer_id = data[0]
            old_score = int(data[1])
            if old_score != score:
                if enteredtimestamp < timestamp:
                    # Replace answer
                    print("Replacing: present timestamp"+str(enteredtimestamp)+" new timestamp: "+str(timestamp)+" answergroup_id: "+str(answergroup_id)+" answer_id: "+str(answer_id)+" old score: "+str(old_score)+" new score: "+str(score))
                    sqlupdate = "Update assessments_answergroup_student set date_of_visit=%s where id=%s;"
                    tocursor.execute(sqlupdate, (timestamp, answergroup_id))
                    sqlupdate = "update assessments_answerstudent set answer=%s where id=%s;"
                    tocursor.execute(sqlupdate, (score, answer_id))
        else:
            # Answer not present so inserting
            sqlinsert = "insert into assessments_answerstudent(answergroup_id, question_id, answer) values(%s, %s, %s)"
            tocursor.execute(sqlinsert, (answergroup_id, question_id, score))
    else:
        # New answergoup so inserting answer
        sqlinsert = "insert into assessments_answerstudent(answergroup_id, question_id, answer) values(%s, %s, %s)"
        tocursor.execute(sqlinsert, (answergroup_id, question_id, score))

    toconn.commit()
tocursor.close()
toconn.close()

fromcursor.close()
fromconn.close()
