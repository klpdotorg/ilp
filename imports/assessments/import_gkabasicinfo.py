from os import sys
import csv
import psycopg2
import os, inspect

if len(sys.argv) != 2:
    print("Please give database name as arguments. USAGE: " +
          "python import_gka.py ilp")
    sys.exit()

questionfile = 'EkStepQuestions.csv'
todatabase = sys.argv[1]

basename = "gka"
scriptdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
inputsqlfile = scriptdir+"/"+basename+"_getdata.sql"
loadsqlfile = scriptdir+"/"+basename+"_loaddata.sql"


connectionstring = "dbname=%s user=klp" % todatabase
conn = psycopg2.connect(connectionstring)
cursor = conn.cursor()
f = open(scriptdir+"/"+questionfile, 'r')
csv_f = csv.reader(f)

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


sqlinsert = "insert into assessments_survey (id, name, created_at, status_id, admin0_id) values(%s, %s, %s, %s, %s);"
cursor.execute(sqlinsert, (3, 'Ganitha Kalika Andolana', '2016-05-19', 'AC', 2))

count = 0
for row in csv_f:
    if count < 1:
        count += 1
        continue

    question_text = row[0]
    questiongroup_name = row[1]
    question_key = row[2]
    question_displaytext = row[3]

    sqlselect = "select id from assessments_question where question_text=%s;"
    cursor.execute(sqlselect, [question_text])
    if cursor.rowcount > 0:
        question_id = cursor.fetchall()[0]
    else:
        sqlinsert = "insert into assessments_question (question_text, display_text, key, options, is_featured, question_type_id, status_id) values(%s, %s, %s, %s, %s, %s, %s) returning id;"
        cursor.execute(sqlinsert, (question_text, question_displaytext, question_key,
                       questiongroup[questiongroup_name]["options"],
                       question_featured, question_type, 'AC'))
        question_id = cursor.fetchone()[0]

    sqlselect = "select id from assessments_questiongroup where name=%s;"
    cursor.execute(sqlselect, [questiongroup_name])
    if cursor.rowcount > 0:
        questiongroup_id = cursor.fetchall()[0]
    else:
        if questiongroup_name in questiongroup:
            sqlinsert = "insert into assessments_questiongroup (name, group_text, start_date, end_date, double_entry, created_at, inst_type_id, status_id, survey_id, survey_on_id, type_id ) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) returning id;"
            cursor.execute(sqlinsert, (questiongroup_name,
                           questiongroup[questiongroup_name]["text"],
                           questiongroup[questiongroup_name]["start_date"],
                           questiongroup[questiongroup_name]["end_date"], 'false',
                           questiongroup[questiongroup_name]["start_date"], 'primary',
                           questiongroup[questiongroup_name]["status"], 3, 'student',
                           'assessment'))
            questiongroup_id = cursor.fetchone()[0]

    if questiongroup_id and question_id:
        sqlinsert = "insert into assessments_questiongroup_questions (question_id, questiongroup_id) values(%s,%s) returning id;"
        cursor.execute(sqlinsert, (question_id, questiongroup_id))


conn.commit()
cursor.close()
conn.close()
