from os import sys
import psycopg2
import datetime
import os, inspect

if len(sys.argv) != 7:
    print("Please give host source, password source, host target, password target,from and to+1 dates as arguments. USAGE: " +
          "python A3toILPAssess.py hostA3 passA3 hostILP passILP 2017-11-01 2017-11-02")
    sys.exit()

hostA3 = sys.argv[1] 
passA3 = sys.argv[2]
hostILP = sys.argv[3]
passILP = sys.argv[4]
fromdate = sys.argv[5]
todate = sys.argv[6]

fromconnectionstring = "dbname=a3 user=a3 password="+passA3+" host="+hostA3
fromconn = psycopg2.connect(fromconnectionstring)
fromcursor = fromconn.cursor()

toconnectionstring = "dbname=ilp user=postgres password="+passILP+" host="+hostILP
toconn = psycopg2.connect(toconnectionstring)
tocursor = toconn.cursor()

excpconnectionstring = "dbname=a3 user=a3 password="+passA3+" host="+hostA3
excpconn = psycopg2.connect(excpconnectionstring)
excpcursor = excpconn.cursor()

sqlselect = "select assess.id_assessment as assess_uid,assess.id_child as student_id,to_timestamp(datetime_start) as start_time,to_timestamp(datetime_submission) as sync_time, ques.id, dtl.pass, qset.id from a3_assessment_tbl assess,a3_assessment_detail_tbl dtl,a3_question_tbl ques,a3_questionset_tbl qset where assess.id_assessment = dtl.id_assessment and assess.id_questionset = qset.id and dtl.id_question = ques.id_question and to_timestamp(datetime_start) > %s and to_timestamp(datetime_start) < %s;"
fromcursor.execute(sqlselect,(fromdate, todate))
now = str(datetime.datetime.now())

for row in fromcursor.fetchall():
    assess_uid = row[0]
    student_id = row[1]
    start_time = row[2]
    sync_time = row[3]
    question_id = row[4]
    if row[5] == 'P':
        score = 1
    else:
        score = 0
    qset_id = row[6]
    dateofvisit = datetime.datetime.date(row[2])

    sqlselect = "select exists(select 1 from schools_student where id=%s);"
    tocursor.execute(sqlselect, [student_id])
    if not tocursor.fetchall()[0][0]:
        sqlinsert = "insert into ilp_exception(datarow, excp_id, excp_data, update_date) values (%s, 1, %s, %s);"
        excpcursor.execute(sqlinsert, (row, student_id, now))
        excpconn.commit()
        continue

    
    # Get questiongroup id
    sqlselect = "select id from assessments_questiongroup where description=%s::text;"  
    tocursor.execute(sqlselect, [qset_id])
    if tocursor.rowcount == 0:
        sqlinsert = "insert into ilp_exception(datarow, excp_id, excp_data, update_date) values (%s, 2, %s, %s);"
        excpcursor.execute(sqlinsert, (row, qset_id, now))
        excpconn.commit()
        continue
    else:
        questiongroup_id = tocursor.fetchall()[0]

    # Get question_id
    sqlselect = "select id from assessments_question where question_text=%s::text;"
    tocursor.execute(sqlselect, [question_id])
    if tocursor.rowcount == 0:
        sqlinsert = "insert into ilp_exception(datarow, excp_id, excp_data, update_date) values (%s, 3, %s, %s);"
        excpcursor.execute(sqlinsert, (row, question_id, now))
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
        tocursor.execute(sqlinsert, (start_time, 'true', questiongroup_id, 'AC', student_id, assess_uid))
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
                if enteredtimestamp < start_time:
                    # Replace answer
                    sqlupdate = "Update assessments_answergroup_student set date_of_visit=%s where id=%s;"
                    tocursor.execute(sqlupdate, (start_time, answergroup_id))
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
