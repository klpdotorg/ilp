from os import sys
import psycopg2
import datetime
import os, inspect
import csv

if len(sys.argv) != 4:
    print("Please give host, password,filename as arguments. USAGE: " +
          "python3 ILPUpdateAnswers.py host password <filename>.csv")
    sys.exit()

host = sys.argv[1] 
password = sys.argv[2]
filename = sys.argv[3]

fromconnectionstring = "dbname=ekstep user=klp password="+password+" host="+host
fromconn = psycopg2.connect(fromconnectionstring)
fromcursor = fromconn.cursor()

toconnectionstring = "dbname=ilp user=klp password="+password+" host="+host
toconn = psycopg2.connect(toconnectionstring)
tocursor = toconn.cursor()

dir = os.path.dirname(__file__)
input_file = os.path.join(dir,'../../datapull/'+filename)
for line in open(input_file, 'r'):
    parts = line.split('|')
    question_id = parts[0]
    correct_ans = parts[1]
    sqlselect = "select assess_uid, question_id from ekstep_assess where question_id=%s and result=%s and score=0;"
    fromcursor.execute(sqlselect,(question_id, correct_ans))
    for row in fromcursor.fetchall():
        assess_uid = row[0]
        question = row[1]
        sqlselect = "select ans.id, ans.answer from assessments_answerstudent ans, assessments_answergroup_student ansgrp,  assessments_question ques where ans.answergroup_id = ansgrp.id and ansgrp.comments = %s and ans.question_id = ques.id and ques.question_text = %s;" 
        tocursor.execute(sqlselect, (assess_uid, question))
        answer_present = tocursor.rowcount
        if answer_present != 0:
            sqlupdate = "update assessments_answerstudent ans set answer = 1 from assessments_answergroup_student ansgrp,  assessments_question ques where ans.answergroup_id = ansgrp.id and ansgrp.comments = %s and ans.question_id = ques.id and ques.question_text = %s;"
            tocursor.execute(sqlupdate, (assess_uid, question))
        toconn.commit()

tocursor.close()
toconn.close()
fromcursor.close()
fromconn.close()
