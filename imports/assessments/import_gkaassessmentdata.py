from os import sys
import psycopg2
import datetime
import os, inspect
import csv

if len(sys.argv) != 3:
    print("Please give database names as arguments. USAGE: " +
          "python import_gkaassessmentdata.py dubdubdub ilp")
    sys.exit()

fromdatabase = sys.argv[1]

todatabase = sys.argv[2]

basename = "gkaassessment"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
inputsqlfile = scriptdir+"/"+basename+"_getdata.sql"
loadsqlfile = scriptdir+"/"+basename+"_loaddata.sql"

fromconnectionstring = "dbname=%s user=klp" % fromdatabase
fromconn = psycopg2.connect(fromconnectionstring)
fromcursor = fromconn.cursor()

toconnectionstring = "dbname=%s user=klp" % todatabase
toconn = psycopg2.connect(toconnectionstring)
tocursor = toconn.cursor()

question_featured = True
question_type = 4

studentdict={}
questiongroupdict={}
questiondict={}
print("Students not present: ",studentdict)
print("QuestionGroups not present: ",questiongroupdict)
print("Questions not present: ",questiondict)

f = open(scriptdir+"/EkStep_Concepts.csv", 'r')
csv_f = csv.reader(f)
for file_row in csv_f:
    sqlselect = "select stu.student_id, assess.question_id, assess.ekstep_tag, assess.pass , assess.assessed_ts from assessments_v2 assess, students_v2 stu where assess.student_uid=stu.uid and assess.ekstep_tag =  %s and not exists (select * from assessments_v2  as dup where dup.student_uid=assess.student_uid and dup.question_id=assess.question_id and dup.assessed_ts::date=assess.assessed_ts::date and dup.ekstep_tag=assess.ekstep_tag and dup.assessed_ts > assess.assessed_ts);"
    data = file_row[1].strip("'")
    print(data)
    fromcursor.execute(sqlselect, (data,))

    print(fromcursor.rowcount)
    for row in fromcursor.fetchall():
        student_id = row[0]
        question_text = row[1]
        questiongroup_desc = row[2]
        if row[3] == 'Yes':
            score = 1
        else:
            score = 0
        timestamp = row[4]
        dateofvisit = datetime.datetime.date(row[4])
        # check student valid
        sqlselect = "select exists(select 1 from schools_student where id=%s);"
        tocursor.execute(sqlselect, [student_id])
        if not tocursor.fetchall()[0][0]:
            if student_id not in studentdict:
                studentdict[student_id] = 1
            continue

        # Get questiongroup id
        sqlselect = "select id from assessments_questiongroup where description=%s;"
        tocursor.execute(sqlselect, [questiongroup_desc])
        if tocursor.rowcount == 0:
            if questiongroup_desc not in questiongroupdict:
                questiongroupdict[questiongroup_desc] = 1
            continue
        else:
            questiongroup_id = tocursor.fetchall()[0]

        # Check if question is present
        sqlselect = "select id from assessments_question where question_text=%s;"
        tocursor.execute(sqlselect, [question_text])
        if tocursor.rowcount == 0:
            if question_text not in questiondict:
                questiondict[question_text] = 1
            continue
        else:
            question_id = tocursor.fetchall()[0]

        #Check if entry present in questiongroup_questions table
        sqlselect = "select id from assessments_questiongroup_questions where question_id=%s and questiongroup_id=%s;"
        tocursor.execute(sqlselect, (question_id, questiongroup_id))
        if tocursor.rowcount == 0:
            print('mapping is not present...inserting')
            sqlinsert = "insert into assessments_questiongroup_questions(question_id, questiongroup_id) values (%s, %s) returning id;"
            tocursor.execute(sqlinsert, (question_id, questiongroup_id))



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
            sqlinsert = "insert into assessments_answergroup_student(date_of_visit, is_verified, questiongroup_id, status_id, student_id) values (%s, %s, %s, %s, %s) returning id;"
            tocursor.execute(sqlinsert, (timestamp, 'true', questiongroup_id, 'AC',
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

print("Students not present: ",studentdict)
print("QuestionGroups not present: ",questiongroupdict)
print("Questions not present: ",questiondict)
