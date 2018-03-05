from os import sys
import psycopg2
import datetime
import os, inspect

if len(sys.argv) != 5:
    print("Please give password, host,from and to+1 dates as arguments. USAGE: " +
          "python GKAtoILPAssess password host 2017-11-01 2017-11-02")
    sys.exit()

password = sys.argv[1]
host = sys.argv[2] 
fromdate = sys.argv[3]
todate = sys.argv[4]

fromconnectionstring = "dbname=ekstep user=klp password="+password+" host="+host
print(fromconnectionstring)
fromconn = psycopg2.connect(fromconnectionstring)
fromcursor = fromconn.cursor()

toconnectionstring = "dbname=ilp user=klp password="+password+" host="+host
print(toconnectionstring)
toconn = psycopg2.connect(toconnectionstring)
tocursor = toconn.cursor()

excpconnectionstring = "dbname=ekstep user=klp password="+password+" host="+host
print(excpconnectionstring)
excpconn = psycopg2.connect(excpconnectionstring)
excpcursor = excpconn.cursor()

sqlselect = "select stu.student_id, assess.question_id, assess.content_id, assess.pass , assess.assessed_ts, assess.assess_uid  from ekstep_assess assess, students stu, gka_devices c, gka_content d where assess.student_uid=stu.uid::varchar and assess.sync_ts > %s and assess.sync_ts < %s and assess.device_id = c.device_id and assess.content_id = d.content_id and not exists (select * from ekstep_assess  as dup where dup.assess_uid=assess.assess_uid and  dup.student_uid=assess.student_uid and dup.question_id=assess.question_id and dup.assessed_ts::date=assess.assessed_ts::date and dup.content_id=assess.content_id and dup.sync_ts = assess.sync_ts and dup.assessed_ts > assess.assessed_ts)"
fromcursor.execute(sqlselect,(fromdate, todate))
now = str(datetime.datetime.now())

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
    assess_uid = row[5]
    #print (student_id, question_text, questiongroup_desc, score, timestamp, dateofvisit)

    sqlselect = "select exists(select 1 from schools_student where id=%s);"
    tocursor.execute(sqlselect, [student_id])
    if not tocursor.fetchall()[0][0]:
        sqlinsert = "insert into ilp_exception(datarow, excp_id, excp_data, update_date) values (%s, 1, %s, %s);"
        excpcursor.execute(sqlinsert, (row, student_id, now))
        excpconn.commit()
        continue

    
    # Get questiongroup id
    sqlselect = "select id from assessments_questiongroup where description=%s;"
    tocursor.execute(sqlselect, [questiongroup_desc])
    if tocursor.rowcount == 0:
        sqlinsert = "insert into ilp_exception(datarow, excp_id, excp_data, update_date) values (%s, 2, %s, %s);"
        excpcursor.execute(sqlinsert, (row, questiongroup_desc, now))
        excpconn.commit()
        continue
    else:
        questiongroup_id = tocursor.fetchall()[0]

    # Get question_id
    sqlselect = "select id from assessments_question where question_text=%s;"
    tocursor.execute(sqlselect, [question_text])
    if tocursor.rowcount == 0:
        sqlinsert = "insert into ilp_exception(datarow, excp_id, excp_data, update_date) values (%s, 3, %s, %s);"
        excpcursor.execute(sqlinsert, (row, question_text, now))
        excpconn.commit()
        continue
    else:
        question_id = tocursor.fetchall()[0]

    # check if answergroup is present
    sqlselect = "select id, date_of_visit from assessments_answergroup_student where student_id=%s and questiongroup_id=%s and date_of_visit::date=%s and comments=%s;"
    tocursor.execute(sqlselect, (student_id, questiongroup_id, dateofvisit, assess_uid))
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
        sqlinsert = "insert into assessments_answergroup_student(date_of_visit, is_verified, questiongroup_id, status_id, student_id, comments) values (%s, %s, %s, %s, %s, %s) returning id;"
        tocursor.execute(sqlinsert, (timestamp, 'true', questiongroup_id, 'AC', student_id, assess_uid))
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

excpcursor.close()
excpconn.close()

fromcursor.close()
fromconn.close()
